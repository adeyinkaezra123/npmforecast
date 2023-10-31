from datetime import datetime, timedelta
from typing import Any, Union, List
import mindsdb_sdk
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from mindsdb_sdk.server import Server
from mindsdb_sdk.databases import Database
from pandas import DataFrame
from requests.exceptions import HTTPError, ConnectionError
from exceptions.auth import CredentialsError
from exceptions.connection import NetworkError
from templates.mindsdb_queries import SQL_PACKAGE_QUERY
from utils import *


MINDSDB_HOST = 'https://cloud.mindsdb.com'
MINDSDB_USERNAME = st.secrets['mindsdb_username']
MINDSDB_PASSWORD = st.secrets['mindsdb_password']

class MindsDB:
    """
    MindsDB manager class
    """

    def __init__(self, email: str, password: str) -> None:
        """
        initializer class.
        Args:
            email: MindsDB account email address (that is stored as an env var)
            password: MindsDB account password
        """
        self.email = email
        self.password = password

        self.is_authenticated: bool = False
        self.database: Database = None
        self.server = None
        if not self.is_authenticated:
            self.authenticate()
            
        print(self.is_authenticated)
    def authenticate(self) -> None:
        """
        authorizes the email and password with MindsDB's host
        """
        try:
            # self.server = mindsdb_sdk.connect('http://127.0.0.1:47334')

            self.server = mindsdb_sdk.connect(
                MINDSDB_HOST,
                login=self.email,
                password=self.password,
            )
        except HTTPError as e:
            raise CredentialsError('Email or password is incorrect. Make sure to enter the right credentials.', e)
        except ConnectionError as e:
            raise NetworkError('Make sure you have access to the internet and try again.', e)

        self.is_authenticated = True
        self.database = self.collect_database()

    def collect_database(self) -> Database:
        if self.server:
            self.database = self.server.get_database('pypi_datasource')
            return self.database

    def get_package_data(self, package: Union[str, List[str]], prediction_days: str):
        if type(package) == 'list':
            pass
        query = self.database.query(
        f'SELECT date, downloads FROM pypi_datasource.overall WHERE package="{package}" AND mirrors=true limit 500'
    )
        overall_df = query.fetch()

        converted_prediction_days = convert_to_days(prediction_days)
        predicted_dataframe = pd.DataFrame(columns=["date", "downloads"])
        today = datetime.today()
        prediction_date = (today - timedelta(days=180)).date()
        for i in range(converted_prediction_days):
            query = self.database.query(
                f'SELECT date, downloads FROM mindsdb.pypi_model WHERE date="{prediction_date}"'
            )
            predicted_value = query.fetch()
            current_date = (today + timedelta(days=i)).date()
            predicted_dataframe = pd.concat([predicted_dataframe, query.fetch()], ignore_index=True)
        fig = go.Figure()
        # fig.add_trace(
        #     go.Scatter(
        #         x=overall_df["date"], y=overall_df["downloads"], mode="lines", name="Data"
        #     )
        # )
        fig.add_trace(
        go.Scatter(
            x=predicted_dataframe["date"],
            y=predicted_dataframe["downloads"],
            mode="lines",
            name=f"{package.title()}",
        )
    )
        fig.update_layout(
            title="NPM Module Download Rate Prediction",
            xaxis_title="Timeframe",
            yaxis_title="Estimated Downloads",
            template="plotly_dark",
        )
        print(fig)
        return fig
    # def get_multiple_package_data(self, packages: List[str], prediction_days: str):
    #     fig = go.Figure()
    #     for package in packages:
    #         print(package)
    #         single_fig = self.get_multiple_package_data(package, prediction_days)
    #         fig.add