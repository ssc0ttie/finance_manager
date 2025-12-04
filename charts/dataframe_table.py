import streamlit as st
import numpy as np
import pandas as pd


def generate_table(data):
    st.dataframe(
        data.style.apply(
            lambda x: ["color: red" if v < 0 else "color: green" for v in x],
            subset=["Variance"],  # Use the new column name
        ).format(
            {
                "Actual Spent": "${:,.2f}",
                "Budgeted Amount": "${:,.2f}",
                "Variance": "${:,.2f}",
            }
        ),
        use_container_width=True,
    )
