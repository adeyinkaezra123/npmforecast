from typing import Any
import mindsdb_sdk
import streamlit as st
from mindsdb_sdk.server import Server
from mindsdb_sdk.databases import Database
from pandas import DataFrame
from requests.exceptions import HTTPError, ConnectionError
from exceptions.auth import CredentialsError
from exceptions.connection import NetworkError
from templates.mindsdb_queries import SQL_PACKAGE_QUERY



MINDSDB_HOST = 'https://cloud.mindsdb.com'
MINDSDB_USERNAME = st.secrets['mindsdb_username']
MINDSDB_PASSWORD = st.secrets['mindsdb_password']

class MindsDB:
    """
    MindsDB manager class
    """

    def __init__(self) -> None:
    # def __init__(self, email: str, password: str) -> None:
        """
        initializer class.
        Args:
            email: MindsDB account email address (that is stored as an env var)
            password: MindsDB account password
        """
        # self.email = email
        # self.password = password

        self.is_authenticated: bool = False
        self.database: Database
        self.server = None
        if not self.is_authenticated:
            self.authenticate()

    def authenticate(self) -> None:
        """
        authorizes the email and password with MindsDB's host
        """
        try:
            self.server = mindsdb_sdk.connect('http://127.0.0.1:47334')

            # self.server = mindsdb_sdk.connect(
            #     MINDSDB_HOST,
            #     login=self.email,
            #     password=self.password,
            # )
        except HTTPError:
            raise CredentialsError('Email or password is incorrect. Make sure to enter the right credentials.')
        except ConnectionError as e:
            raise NetworkError('Make sure you have access to the internet and try again.', e)

        self.is_authenticated = True
        self.database = self.collect_database()

    def collect_database(self) -> Database:
        if self.server:
            database = self.server.get_database('pypi_datasource')
            print(database)
            return database

    # def answer(self, question: str) -> Any:
    #     """
    #     takes the question and queries then converts the response into `rich.Markdown`
    #     Args:
    #         question: the value from `ask` positional argument

    #     Returns:
    #         response from MindsDB in Markdown format
    #     """

    #     return to_data(
    #         self.database.query(
    #             SQL_ASK_QUERY.substitute(
    #                 ask=question,
    #                 user=getuser(),
    #             )
    #         ).fetch()
    #     )
    


# def get_package_data(package: Union[str, List[str]], prediction_days: str):
#     server = mindsdb_sdk.connect('https://cloud.mindsdb.com', login=MINDSDB_USERNAME, password=MINDSDB_PASSWORD)
#     databases = server.list_databases()
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
#     fig.update_layout(
#         title="PyPI Package Download Rate Prediction",
#         xaxis_title="Dates",
#         yaxis_title="Downloads",
#         template="plotly_dark",
#     )
#     return fig
