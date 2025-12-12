import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st


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


def metric_sections_income(data):
    # 'data' is the RENAMED dataframe (after renaming)
    # Make sure the column names match what you renamed them to
    col1, col2, col3 = st.columns(3)

    grand_total_act = f"${data['Income'].sum():,.0f}"
    # grand_total_bud = f"${data['Budgeted Amount'].sum():,.0f}"
    # grand_total_diff = f"${data['Variance'].sum():,.0f}"

    # diff_value = data["Variance"].sum()

    col1.metric(
        "Income",
        value=grand_total_act,
        label_visibility="visible",
        border=True,
    )


def get_bank_balance(merged_df, merged_df_budgeted, merged_df_actual):

    max_year = merged_df["year"].max()
    max_year_actual = merged_df_actual["year"].max()

    sum_by_cat = merged_df[merged_df["year"] == max_year]
    sum_by_cat_budget = merged_df_budgeted[merged_df_budgeted["year"] == max_year]
    sum_by_cat_actual = merged_df_actual[merged_df_actual["year"] == max_year]

    sum_by_cat_actual = (
        sum_by_cat_actual.groupby("category").agg({"amount_x": "sum"}).reset_index()
    )
    sum_by_cat_actual = sum_by_cat_actual.rename(columns={"amount_x": "amount"})

    sum_by_cat_budget = (
        sum_by_cat_budget.groupby("category").agg({"amount_x": "sum"}).reset_index()
    )
    sum_by_cat_budget = sum_by_cat_budget.rename(columns={"amount_x": "amount"})

    ### HARDCODED BUDGET FROM 2024 ####
    df_from_2024 = pd.DataFrame(
        {
            "Tax budgeted": [3074.00],
            "Emergency budgeted": [13153.00],
            "Cushion budgeted": [12387.00],
            "Travel budgeted": [2455.00],
            "ETF budgeted": [0.00],
            "Interest budgeted": [0.00],
            "Investment budgeted": [0.00],
        }
    )
    # Creates a DataFrame with one column, keys as rows

    df_from_2024 = df_from_2024.melt(var_name="category", value_name="amount")

    # print(df_from_2024.head())

    combined_budgeted = pd.concat(
        [df_from_2024, sum_by_cat_budget, sum_by_cat_actual], axis=0, ignore_index=True
    )
    combined_budgeted[["category", "type"]] = combined_budgeted["category"].str.split(
        " ", expand=True
    )

    combined_budgeted = (
        combined_budgeted.groupby("category").agg({"amount": "sum"}).reset_index()
    )

    sum_b = combined_budgeted["amount"].sum()

    balance = f"${sum_b.sum():,.0f}"

    st.metric(
        "Bank Balance",
        value=balance,
        label_visibility="visible",
        border=True,
    )


def get_bank_balance_2(
    merged_df,
    merged_df_budgeted,
    merged_df_actual,
    renamed_df_with_diff,
    df_raw_interest,
):
    """
    Calculate bank balance using:
    1. Budgeted amounts (current year)
    2. Historical hardcoded 2024 amounts
    3. Actual amounts (current year)
    4. Plus the diff/variance from main calculation
    """
    st.subheader("📊 Balances")
    max_year = merged_df["year"].max()
    max_year_actual = merged_df_actual["year"].max()

    # Get current year budgeted amounts
    sum_by_cat_budget = merged_df_budgeted[merged_df_budgeted["year"] == max_year]
    sum_by_cat_budget = (
        sum_by_cat_budget.groupby("category").agg({"amount": "sum"}).reset_index()
    )
    # sum_by_cat_budget = sum_by_cat_budget.rename(columns={"amount_x": "amount"})
    total_budgeted = sum_by_cat_budget["amount"].sum()

    # Get current year actual amounts
    sum_by_cat_actual = merged_df_actual[merged_df_actual["year"] == max_year]

    sum_by_cat_actual_interest = df_raw_interest[
        df_raw_interest["category"] == "Interest"
    ]
    sum_by_cat_actual_interest = sum_by_cat_actual_interest[
        sum_by_cat_actual_interest["year"] == max_year
    ]

    sum_by_cat_actual_interest = (
        sum_by_cat_actual_interest.groupby("category")
        .agg({"amount": "sum"})
        .reset_index()
    )
    total_interest = sum_by_cat_actual_interest["amount"].sum() * -1

    sum_by_cat_actual = (
        sum_by_cat_actual.groupby("category").agg({"amount_x": "sum"}).reset_index()
    )
    sum_by_cat_actual = sum_by_cat_actual.rename(columns={"amount_x": "amount"})

    total_actual = sum_by_cat_actual["amount"].sum()

    #### GET VARIANCE #####
    sum_by_cat_var = merged_df[merged_df["year"] == max_year]

    sum_by_cat_var = sum_by_cat_var.groupby(["category"], as_index=False).agg(
        {"actual": "sum", "budget": "sum"}
    )
    sum_by_cat_var["diff"] = sum_by_cat_var["budget"] - sum_by_cat_var["actual"]

    ### HARDCODED BUDGET FROM 2024 ####
    df_from_2024 = pd.DataFrame(
        {
            "Tax budgeted": [3074.00],
            "Emergency budgeted": [13153.00],
            "Cushion budgeted": [12387.00],
            "Travel budgeted": [2455.00],
            "ETF budgeted": [0.00],
            "Interest budgeted": [0.00],
            "Investment budgeted": [0.00],
        }
    )
    df_from_2024 = df_from_2024.melt(var_name="category", value_name="amount")

    total_df_from_2024 = df_from_2024["amount"].sum()

    # Combine: 2024 historical + current budgeted + current actual
    combined_budgeted = pd.concat(
        [df_from_2024, sum_by_cat_budget, sum_by_cat_actual], axis=0, ignore_index=True
    )

    # Split category into name and type (e.g., "ETF budgeted" -> "ETF", "budgeted")
    combined_budgeted[["category", "type"]] = combined_budgeted["category"].str.split(
        " ", expand=True
    )

    # Group by category and sum amounts
    combined_budgeted = (
        combined_budgeted.groupby("category").agg({"amount": "sum"}).reset_index()
    )
    sum_by_cat_actual_interest_beforemerge = sum_by_cat_actual_interest.copy()
    sum_by_cat_actual_interest_beforemerge["amount"] = (
        sum_by_cat_actual_interest_beforemerge["amount"] * -1
    )

    combined_budgeted_interest = pd.concat(
        [combined_budgeted, sum_by_cat_actual_interest_beforemerge],
        axis=0,
        ignore_index=True,
    )

    combined_budgeted_interest = (
        combined_budgeted_interest.groupby("category")
        .agg({"amount": "sum"})
        .reset_index()
    )
    # Get base sum (ETF budgeted + Historical 2024 - ETF Actual)
    base_sum = combined_budgeted["amount"].sum()

    # Now add the diff from main.py
    # Get the total diff/variance from renamed_df
    total_diff = sum_by_cat_var["diff"].sum()

    # Final bank balance = base_sum + total_diff
    final_balance = base_sum + total_diff + total_interest

    balance = f"${final_balance:,.0f}"

    # Display with delta showing the diff contribution
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Bank Balance",
            value=balance,
            delta=f"${total_diff:,.0f} variance",
            label_visibility="visible",
            border=True,
        )

        # Create a copy to avoid modifying original data
        display_df = combined_budgeted_interest.copy()
        display_df["amount"] = display_df["amount"].apply(lambda x: f"${x:,.2f}")

        st.dataframe(
            display_df,
            use_container_width=True,
        )
    with col2:
        # Format amounts for display
        formatted_amounts = [f"${x:,.2f}" for x in combined_budgeted_interest["amount"]]

        # 3. Donut chart for balance distribution
        fig3 = go.Figure(
            data=[
                go.Pie(
                    labels=combined_budgeted_interest["category"],
                    values=combined_budgeted_interest["amount"],
                    hole=0.3,
                    textinfo="label+value",  # Show label and raw value
                    texttemplate="%{label}<br>%{value:$,.2f}<br>(%{percent:.1%})",  # Custom format
                    textposition="inside",
                    marker=dict(colors=px.colors.qualitative.Set3),
                    hovertemplate="<b>%{label}</b><br>"
                    + "Amount: %{value:$,.2f}<br>"
                    + "Percentage: %{percent:.1%}<br>"
                    + "<extra></extra>",
                )
            ]
        )
        fig3.update_layout(title="Balances Distribution")
        st.plotly_chart(fig3, use_container_width=True)
        # """DEBUG SECTION"""

    # st.dataframe(df_from_2024)
    # st.write("Variance : ", total_diff)
    # # st.write("Total 2024 : ", total_df_from_2024)
    # # st.write("Total Budgeted : ", total_budgeted)
    # # st.write("Total Actual : ", total_actual)
    # st.write("Total Interest : ", total_interest)
    # st.write("Combined Bdget : ", total_df_from_2024 + total_budgeted)

    return final_balance


def get_bank_balance_simple(renamed_df, previous_balance=0):
    """
    Calculate bank balance based on variance (budget - actual)
    plus carryover from previous period
    """
    # Sum all variances
    total_variance = renamed_df["Variance"].sum()

    # Bank balance = Previous balance + Current variance
    bank_balance = previous_balance + total_variance

    formatted_balance = f"${bank_balance:,.2f}"

    st.metric(
        "Bank Balance",
        value=formatted_balance,
        delta=f"{total_variance:,.2f}",
        label_visibility="visible",
        border=True,
    )

    return bank_balance


# def get_travel_balances(
#     merged_df,
#     merged_df_budgeted,
#     merged_df_actual,
#     renamed_df_with_diff,
#     df_raw_interest,
# ):

#     # Display with delta showing the diff contribution
#     col1, col2 = st.columns(2)

#     with col1:
#         st.metric(
#             "Bank Balance",
#             value=balance,
#             delta=f"${total_diff:,.0f} variance",
#             label_visibility="visible",
#             border=True,
#         )

#         # Create a copy to avoid modifying original data
#         display_df = combined_budgeted_interest.copy()
#         display_df["amount"] = display_df["amount"].apply(lambda x: f"${x:,.2f}")

#         st.dataframe(
#             display_df,
#             use_container_width=True,
#         )
#     with col2:
#         # Format amounts for display
#         formatted_amounts = [f"${x:,.2f}" for x in combined_budgeted_interest["amount"]]

#         # 3. Donut chart for balance distribution
#         fig3 = go.Figure(
#             data=[
#                 go.Pie(
#                     labels=combined_budgeted_interest["category"],
#                     values=combined_budgeted_interest["amount"],
#                     hole=0.3,
#                     textinfo="label+value",  # Show label and raw value
#                     texttemplate="%{label}<br>%{value:$,.2f}<br>(%{percent:.1%})",  # Custom format
#                     textposition="inside",
#                     marker=dict(colors=px.colors.qualitative.Set3),
#                     hovertemplate="<b>%{label}</b><br>"
#                     + "Amount: %{value:$,.2f}<br>"
#                     + "Percentage: %{percent:.1%}<br>"
#                     + "<extra></extra>",
#                 )
#             ]
#         )
#         fig3.update_layout(title="Balances Distribution")
#         st.plotly_chart(fig3, use_container_width=True)
