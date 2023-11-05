from datetime import datetime, timedelta
from typing import Any, Union, List
import mindsdb_sdk
import streamlit as st
import pandas as pd
import json
import requests
import plotly.graph_objects as go
from mindsdb_sdk.server import Server
from mindsdb_sdk.databases import Database
from pandas import DataFrame
from requests.exceptions import HTTPError, ConnectionError
from exceptions.auth import CredentialsError
from exceptions.connection import NetworkError
from templates.mindsdb_queries import RETRIEVE_PREDICTION_QUERY, MODEL_CREATION_QUERY
from utils import *

MINDSDB_HOST = 'https://cloud.mindsdb.com'
MINDSDB_USERNAME = st.secrets['mindsdb_username']
MINDSDB_PASSWORD = st.secrets['mindsdb_password']
NPM_PACKAGES_API = st.secrets['npm_api']

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
        self.database: Union[Database, None] = None 
        self.server = None
        if not self.is_authenticated:
            self.authenticate()

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
            st.error('Email or password is incorrect. Make sure to enter the right credentials.')
            raise CredentialsError('Email or password is incorrect. Make sure to enter the right credentials.', e)
        except ConnectionError as e:
            st.error('We encountered and error while connecting to the Databse.\nMake sure you have access to the internet and try again.')
            raise NetworkError('Make sure you have access to the internet and try again.', e)

        self.is_authenticated = True
        self.database = self.collect_database()

    def collect_database(self) -> Database | None:
        if self.server:
            self.database = self.server.databases.files
            return self.database
        
    def fetch_package_data(self, packages: List[str]):
        """Fetches package data from the API.

        Args:
            package_names: An array of package names.

        Returns:
            An array of package data.
        """
        package_data = []
        if len(packages) < 1:
            raise ValueError("Package data list cannot be empty")
        elif len(packages) == 1:
            response = requests.get(f"{NPM_PACKAGES_API}/{packages[0]}")
            if response.status_code == 200:
                package_downloads = response.json()
                package_data.append(package_downloads)
            else:
                print(f"Failed to fetch package data: {response.status_code}")
        else:
            response = requests.get(f"{NPM_PACKAGES_API}/{','.join(packages)}")
            if response.status_code == 200:
                package_downloads = response.json()
                package_data.append(package_downloads)
            else:
                print(f"Failed to fetch package data for: {response.status_code}")
        return package_data

    def upload_files(self, package_data):
        for package in package_data:
            filename = package['package']
            df = pd.DataFrame(package['downloads'])
            df.columns = ["downloads", "date"]
            df["date"] = pd.to_datetime(df["date"])
        try:
            if len(df):
                try:
                    self.database.tables.drop(filename)
                except Exception as e:
                    print("Table does not exist", e)
                self.database.tables.create(filename, df, replace=True)
        except Exception as e:
            st.error(body="Cannot upload downloads Dataframe to the server", icon="🚨")
            print("Error encountered: ", e)
       
    def create_prediction_model_for(self, package_name: str, prediction_days:str):
        converted_prediction_days = convert_to_days(prediction_days)
        print(package_name)
        try:
            try:
                self.server.models.drop(f'{package_name}_prediction_model')
            except Exception as e:
                print("Table does not exist", e)
            
            model = self.server.models.create(
              name=f'{package_name}_prediction_model',
              predict = 'downloads',
              engine="lightwood",
              database="files",
              query=f"SELECT * FROM files.{package_name}",
              timeseries_options={
                'order': 'date',
                "window": '30',
                "horizon": f'{converted_prediction_days}'
                }
            )
            return model
        #     request = self.database.query(
        #         MODEL_CREATION_QUERY.substitute(
        #                 package=package_name,
        #                 prediction_date=converted_prediction_days
        #         )
        # )
        #     return request.fetch()
        except Exception as e:
            st.error(body=f"Cannot create a prediction model for {package_name}", icon="🚨")
            print("Error encountered: ", e)
        
    def retrieve_predicted_data(self, package_name: str):
        try:
            response = self.server.query(
            RETRIEVE_PREDICTION_QUERY.substitute(
                    package=package_name
        )).fetch()
            return response
        except Exception as e:
            st.error(body=f"Cannot retrieve prediction model data for {package_name}", icon="🚨")
            print("Error encountered: ", e)

    def display_prediction_data(self, data, package_names):
        fig = go.Figure()
        for package, df in zip(package_names,data):
            predicted_df = pd.DataFrame(df)
            predicted_df['downloads'] = predicted_df['downloads'].round().astype(int)
            fig.add_trace(
                go.Scatter( x=predicted_df["date"], y=predicted_df["downloads"], mode="lines", name=package
            )
        )
        fig.update_layout(
            title="NPM Module Download Rate Prediction",
            xaxis_title="Timeframe",
            yaxis_title="Estimated Downloads",
            template="plotly_dark",
        )
        return fig

    # def get_package_data(self, package: Union[str, List[str]], prediction_days: str):
    #     if type(package) == 'list':
    #         pass
    #     query = self.database.query(
    #     f'SELECT date, downloads FROM pypi_datasource.overall WHERE package="{package}" AND mirrors=true limit 500'
    # )
    #     overall_df = query.fetch()

    #     converted_prediction_days = convert_to_days(prediction_days)
    #     predicted_dataframe = pd.DataFrame(columns=["date", "downloads"])
    #     today = datetime.today()
    #     prediction_date = (today - timedelta(days=180)).date()
    #     for i in range(converted_prediction_days):
    #         query = self.database.query(
    #             f'SELECT date, downloads FROM mindsdb.pypi_model WHERE date="{prediction_date}"'
    #         )
    #         predicted_value = query.fetch()
    #         current_date = (today + timedelta(days=i)).date()
    #         predicted_dataframe = pd.concat([predicted_dataframe, query.fetch()], ignore_index=True)
    #     fig = go.Figure()
    #     # fig.add_trace(
    #     #     go.Scatter(
    #     #         x=overall_df["date"], y=overall_df["downloads"], mode="lines", name="Data"
    #     #     )
    #     # )
    #     fig.add_trace(
    #     go.Scatter(
    #         x=predicted_dataframe["date"],
    #         y=predicted_dataframe["downloads"],
    #         mode="lines",
    #         name=f"{package.title()}",
    #     )
    # )
    #     fig.update_layout(
    #         title="NPM Module Download Rate Prediction",
    #         xaxis_title="Timeframe",
    #         yaxis_title="Estimated Downloads",
    #         template="plotly_dark",
    #     )
    #     print(fig)
    #     return fig
    # # def get_multiple_package_data(self, packages: List[str], prediction_days: str):
    # #     fig = go.Figure()
    # #     for package in packages:
    # #         print(package)
    # #         single_fig = self.get_multiple_package_data(package, prediction_days)
    # #         fig.add