from streamlit_tags import st_tags
import streamlit as st
import mimetypes
from datetime import datetime, timedelta
from utils import convert_to_days
from middlewares.mindsdb import MindsDB


MAX_PACKAGES = 5
PREDICTION_OPTIONS = ('1 Week', '1 Month', "3 Months", '6 Months', '1 Year', "2 Years")
MINDSDB_USERNAME = st.secrets['mindsdb_username']
MINDSDB_PASSWORD = st.secrets['mindsdb_password']

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')


st.set_page_config(page_title="NPM Forecast", page_icon="✨", layout="wide")


mindsdb_instance = MindsDB(MINDSDB_USERNAME, MINDSDB_PASSWORD)
# mindsdb_instance = MindsDB()


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
with st.sidebar:
    st.markdown("<h1>Predict package download counts over time.<h1>", unsafe_allow_html=True)
    keywords = st_tags(
        label=f'### Enter an NPM package: You can enter up to {MAX_PACKAGES} packages',
        text= 'Press enter to add more.',
        value=[],
        suggestions=['five', 'six', 'seven', 'eight', 'nine', 'three', 'eleven', 'ten', 'four'],
        maxtags = MAX_PACKAGES,
        key='1')
    st.markdown("<h3>In the next</h3>",unsafe_allow_html=True)
    time_options = st.selectbox(
    'Select time frame',
    PREDICTION_OPTIONS
    )
    st.button(label="Predict", help=None, on_click= mindsdb_instance.get_package_data, args=('requests', "1 Week"), kwargs=None, type="primary", disabled=False, use_container_width=False)

with st.container():
    print('')
    fig = mindsdb_instance.get_package_data('requests', '1 Week')
    st.plotly_chart(fig, use_container_width=True, sharing="streamlit")


