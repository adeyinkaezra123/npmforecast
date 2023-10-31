from streamlit_tags import st_tags
import streamlit as st
import mimetypes
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from utils import convert_to_days
from middlewares.mindsdb import MindsDB


MAX_PACKAGES = 5
PREDICTION_OPTIONS = ('1 Week', '1 Month', "3 Months", '6 Months', '1 Year', "2 Years")
MINDSDB_USERNAME = st.secrets['MINDSDB_USERNAME']
MINDSDB_PASSWORD = st.secrets['MINDSDB_PASSWORD']

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')


st.set_page_config(page_title="NPM Forecast", page_icon="✨", layout="wide")


# mindsdb_instance = MindsDB(email=MINDSDB_USERNAME, password=MINDSDB_PASSWORD)
mindsdb_instance = MindsDB()



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
    '',
    PREDICTION_OPTIONS
    )
    result = st.button(label="Predict", help=None, on_click= mindsdb_instance.collect_database, args=None, kwargs=None, type="primary", disabled=False, use_container_width=False)
    st.write(result)
    # st.button(label="Predict", help=None, on_click= mindsdb_instance.get_package_data, args=('requests', "1 Week"), kwargs=None, type="primary", disabled=False, use_container_width=False)

# with st.container():
#     print('')
#     fig = get_package_data('requests', '1 Week')
#     st.plotly_chart(fig, use_container_width=True)









# def get_package_data(package: Union[str, List[str]], prediction_days: str):
#     database = databases[-1]
#     query = database.query(
#     f'SELECT date, downloads FROM pypi_datasource.overall WHERE package="{package}" AND mirrors=true limit 500'
# )
#     overall_df = query.fetch()

#     converted_prediction_days = convert_to_days(prediction_days)
#     predicted_dataframe = pd.DataFrame(columns=["date", "downloads"])
#     today = datetime.today()
#     prediction_date = (today - timedelta(days=180)).date()
#     for i in range(converted_prediction_days):
#         query = database.query(
#             f'SELECT date, downloads FROM mindsdb.pypi_model WHERE date="{prediction_date}"'
#         )
#         predicted_value = query.fetch()
#         current_date = (today + timedelta(days=i)).date()
#         predicted_dataframe = pd.concat([predicted_dataframe, query.fetch()], ignore_index=True)
#     fig = go.Figure()
#     fig.add_trace(
#         go.Scatter(
#             x=overall_df["date"], y=overall_df["downloads"], mode="lines", name="Data"
#         )
#     )
#     fig.add_trace(
#     go.Scatter(
#         x=predicted_dataframe["date"],
#         y=predicted_dataframe["downloads"],
#         mode="lines",
#         name="Prediction",
#     )
# )
    # fig.update_layout(
    #     title="PyPI Package Download Rate Prediction",
    #     xaxis_title="Dates",
    #     yaxis_title="Downloads",
    #     template="plotly_dark",
    # )
    # return fig
