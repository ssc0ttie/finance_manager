import streamlit as st
import numpy as np
import pandas as pd


def metric_sections_old(data):
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    grand_total_act = f"${data['actual'].sum():,.0f}"
    grand_total_bud = f"${data['budget'].sum():,.0f}"
    grand_total_diff = f"${data['diff'].sum():,.0f}"

    col1.metric(
        "Actual",
        value=grand_total_act,
        label_visibility="visible",
        border=True,
    )

    col2.metric(
        "Budget",
        value=grand_total_bud,
        label_visibility="visible",
        border=True,
    )

    col3.metric(
        "Diff",
        value=grand_total_diff,
        label_visibility="visible",
        border=True,
    )


def metric_sections(data):
    # 'data' is the RENAMED dataframe (after renaming)
    # Make sure the column names match what you renamed them to
    col1, col2, col3 = st.columns(3)

    grand_total_act = f"${data['Actual Spent'].sum():,.0f}"
    grand_total_bud = f"${data['Budgeted Amount'].sum():,.0f}"
    grand_total_diff = f"${data['Variance'].sum():,.0f}"

    diff_value = data["Variance"].sum()

    col1.metric(
        "Actual Spent",
        value=grand_total_act,
        label_visibility="visible",
        border=True,
    )

    col2.metric(
        "Budgeted Amount",
        value=grand_total_bud,
        label_visibility="visible",
        border=True,
    )

    col3.metric(
        "Variance",
        value=grand_total_diff,
        delta=f"{diff_value:,.0f}",
        delta_color="inverse" if diff_value < 0 else "normal",
        label_visibility="visible",
        border=True,
    )
