from streamlit_tags import st_tags
import streamlit as st
import mimetypes
from typing import Any, Union, List
import time
from datetime import datetime, timedelta
from utils import convert_to_days
from middlewares.mindsdb import MindsDB

MAX_PACKAGES = 5
PREDICTION_OPTIONS = ('1 Week', '1 Month', "3 Months", '6 Months', '1 Year')
MINDSDB_USERNAME = st.secrets['mindsdb_username']
MINDSDB_PASSWORD = st.secrets['mindsdb_password']

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')


st.set_page_config(page_title="NPM Forecast", page_icon="✨", layout="wide")

if 'mindsdb_instance' not in st.session_state:
    mindsdb_instance = MindsDB(MINDSDB_USERNAME, MINDSDB_PASSWORD)
    st.session_state["mindsdb_instance"] = mindsdb_instance

if 'can_predict' not in st.session_state:
    st.session_state['can_predict'] = True

if 'chart' not in st.session_state:
    st.session_state['chart'] = None

mindsdb = st.session_state['mindsdb_instance']

chart = None
def predict_package_downloads(packages: List[str], prediction_date):
    st.session_state['can_predict'] = False
    try:
        # Upload downloads data and create prediction models for each package
        toast_msg = st.toast('Retrieving package details...', icon="🎁")
        package_response = mindsdb.fetch_package_data(packages)
        toast_msg.toast('Uploading dataframe to the server...', icon="☁️")
        mindsdb.upload_files(package_data=package_response)
        toast_msg.toast('Creating a prediction model', icon = "🔮")
        for package in packages:
            mindsdb.create_prediction_model_for(package_name=package, prediction_days=prediction_date)
       
        all_models_trained = False
        while not all_models_trained:
            toast_msg.toast('Training prediction model', icon = "☕")
            training_status = []
            print(training_status)
            for model in packages:
                prediction_model = mindsdb.server.models.get(f"{model}_prediction_model")
                model_status = prediction_model.get_status()
                if model_status == 'error':
                    prediction_model.retrain()
                training_status.append(model_status)
                print(training_status)

            all_complete = all(item == "complete" for item in training_status)
            if all_complete:
                all_models_trained = True
                toast_msg.toast('Training prediction model complete', icon = "🤖")

                break
            else:
                time.sleep(5)
                toast_msg.toast('Training prediction model', icon = "☕")
                     
        prediction_results = []
        if all_models_trained:
            for package in packages:
                result = mindsdb.retrieve_predicted_data(package_name=package)
                prediction_results.append(result)
        toast_msg.toast('Performing some cleanup magic', icon = "🧹")
        
        st.session_state['chart']= mindsdb.display_prediction_data(data=prediction_results, package_names=packages)
        

    except Exception as e:
        st.error(body="Package downloads Prediction Failed", icon="🥺")
        print('Error encountered: ', e)
    
    st.session_state['can_predict'] = True


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
with st.sidebar:
    st.markdown("<h1>Predict package download counts over time.<h1>", unsafe_allow_html=True)
    packages = st_tags(
        label=f'### Enter an NPM package: You can enter up to {MAX_PACKAGES} packages',
        text= 'Press enter to add more.',
        value=[],
        suggestions=['react', 'lodash', 'express', 'jquery', 'angular', 'eslint', 'mindsdb-js-sdk'],
        maxtags = MAX_PACKAGES,
        key='1')
    timeframe = st.selectbox(
    'Select time frame',
    PREDICTION_OPTIONS
    )
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    def test(packages, timeframe):
        return [packages, timeframe]  
    if packages and timeframe:
       fig = st.button(label="Predict package downloads", help=None, on_click= predict_package_downloads, args=(packages, timeframe), kwargs=None, type="primary", use_container_width=False, disabled=not st.session_state['can_predict'])

chart = st.session_state['chart']
with st.container():
    if chart:
        st.plotly_chart(chart, use_container_width=True, sharing="streamlit")


