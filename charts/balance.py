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
        # delta=f"{diff_value:,.0f}",
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

def get_bank_balance_2(
    merged_df,
    merged_df_budgeted,
    merged_df_actual,
    renamed_df_with_diff,
    df_raw_interest,
    df_income_grouped,
):
    """
    Calculate bank balance using:
    1. Budgeted amounts (current year)
    2. Historical hardcoded 2024 amounts
    3. Actual amounts (current year)
    4. Plus the diff/variance from main calculation
    """
    st.subheader("📊 Balances")
    sum_by_cat_budget = (
        merged_df_budgeted.groupby("category").agg({"amount": "sum"}).reset_index()
    )
    sum_by_cat_actual = merged_df_actual.copy()

    total_budgeted = sum_by_cat_budget["amount"].sum()

    # st.write(f"sum budget by cat{total_budgeted}")


    sum_by_cat_actual_interest = df_raw_interest[
        df_raw_interest["category"] == "Interest"
    ]

    sum_by_cat_actual_interest = (
        sum_by_cat_actual_interest.groupby("category")
        .agg({"amount": "sum"})
        .reset_index()
    )
    total_interest = sum_by_cat_actual_interest["amount"].sum() * -1

#### INCOME  ##########
    sum_by_cat_income = (
        df_income_grouped.groupby("category")
        .agg({"amount": "sum"})
        .reset_index()
    )

    total_income = sum_by_cat_income["amount"].sum()


#### SPEND  ##########
    sum_by_cat_spend = (
        merged_df.groupby("category")
        .agg({"actual": "sum"})
        .reset_index()
    )

    total_spend = sum_by_cat_spend["actual"].sum()


    sum_by_cat_actual = (
        sum_by_cat_actual.groupby("category").agg({"amount": "sum"}).reset_index()
    )
    # sum_by_cat_actual = sum_by_cat_actual.rename(columns={"amount": "amount"})

    sum_by_cat_actual_for_table = sum_by_cat_actual.copy()

    sum_by_cat_actual_for_table["amount"] = sum_by_cat_actual_for_table["amount"] * -1
    # st.dataframe(sum_by_cat_actual_for_table)


    total_actual = sum_by_cat_actual["amount"].sum()

    #### GET VARIANCE #####

    # # sum_by_cat_var = merged_df[merged_df["year"] == max_year]

    sum_by_cat_var = merged_df.groupby(["category"], as_index=False).agg(
        {"actual": "sum", "budget": "sum"}
    )
    sum_by_cat_var["diff"] = sum_by_cat_var["budget"] - sum_by_cat_var["actual"]

    ### HARDCODED BUDGET FROM 2024 ####
    df_from_2024 = pd.DataFrame(
        {
            "Tax budgeted": [1361.00],
            "Emergency budgeted": [13502.00],
            "Cushion budgeted": [17181.00],
            "Travel budgeted": [3496.00],
            "ETF budgeted": [0.00],
            "Interest budgeted": [0.00],
            "Investment budgeted": [0.00],
        }
    )
    df_from_2024 = df_from_2024.melt(var_name="category", value_name="amount")

    total_df_from_2024 = df_from_2024["amount"].sum()

    # Combine: 2024 historical + current budgeted + current actual
    combined_accrual_df = pd.concat(
        [sum_by_cat_budget,df_from_2024,sum_by_cat_actual_for_table ], axis=0, ignore_index=True
    )

    # Split category into name and type (e.g., "ETF budgeted" -> "ETF", "budgeted") 
    combined_accrual_df["category"] = (
    combined_accrual_df["category"].str.split().str[0]
)

    # Group by category and sum amounts
    combined_accrual_df = (
        combined_accrual_df.groupby("category").agg({"amount": "sum"}).reset_index()
    )



    total_diff = total_income - total_spend
    # Final bank balance = base_sum + total_diff
    final_balance = (total_df_from_2024 + total_budgeted - total_actual ) +(total_income - total_spend) 

######## DEBUG SECTION 10 Jan 2025 ###########

    # st.write(f"total actuals : {total_actual}")
    # st.write(f"total from 2024 : {total_df_from_2024} = 35,540")
    # st.write(f"total actuals : {total_actual} = 48,695.39")
    # st.write(f"total var : {total_income - total_spend} = -1,262")
    # st.write(f"total budgeted : {total_budgeted} = 55,460")
    # st.write(f"total int : {total_interest} = -2,262.05")
    # st.write(f"total income : {total_income} = 108,755")    
    # st.write(f"total spend : {total_spend} = 110,017 ")
    # st.write(f"semi final balance : {(total_df_from_2024 + total_budgeted - total_actual)} = 42,305")
    # st.write(f"final balance : {final_balance} = 41,047")

    # st.dataframe(combined_accrual_df)

    balance = f"${final_balance:,.0f}"

    # Display with delta showing the diff contribution
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Bank Balance",
            value=balance,
            delta=f"${total_diff:,.0f} under / over budget",
            delta_color="inverse" if total_diff < 0 else "normal",
            label_visibility="visible",
            border=True,
        )



        with st.expander("View Detailed Acrual"):
            st.dataframe(
                combined_accrual_df,
                use_container_width=True,
            )

        with col2:
            # Format amounts for display
            formatted_amounts = [
                f"${x:,.2f}" for x in combined_accrual_df["amount"]
            ]

            # 3. Donut chart for balance distribution
            fig3 = go.Figure(
                data=[
                    go.Pie(
                        labels=combined_accrual_df["category"],
                        values=combined_accrual_df["amount"],
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

    return final_balance





def metric_sections_travel(data):
    # 'data' is the RENAMED dataframe (after renaming)
    # Make sure the column names match what you renamed them to
    col1, col2, col3 = st.columns(3)

    grand_total_act = f"${data['actual_sgd'].sum():,.0f}"
    grand_total_bud = f"${data['budget_sgd'].sum():,.0f}"
    grand_total_diff = f"${data['diff'].sum():,.0f}"

    diff_value = data["diff"].sum()

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
        # delta=f"{diff_value:,.0f}",
        delta_color="inverse" if diff_value < 0 else "normal",
        label_visibility="visible",
        border=True,
    )
