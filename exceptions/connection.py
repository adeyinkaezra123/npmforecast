import streamlit as st

class NetworkError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def show_toast(self):
        st.error(self.message, icon="🔌")
