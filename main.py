import streamlit as st
import database as db
import pandas as pd
import charts.balance


# st.set_page_config(
#     page_title="Finance Manager",
#     page_icon="💰",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )


# Initialize active page state
if "active_page" not in st.session_state:
    st.session_state.active_page = "Goodget"

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to:",
        [
            "Goodget",
            "Shared Expenses",
            "Travel",
            "Help",
            "Entry",
        ],
    )

##PAGE##
st.session_state.active_page = page

if page == "Goodget":

    st.header("💰 Goodget - Personal Budget Analyzer")
    st.divider()
    # """fetch all data once"""
    txn = db.fetch_all_transactions()
    bud = db.fetch_all_budget()
    inc = db.fetch_all_income()

    ############# Basic Cleanup TXN #######################
    df_txn = pd.DataFrame(txn)
    df_txn["date"] = pd.to_datetime(df_txn["date"])
    df_txn["year_month"] = df_txn["date"].dt.to_period("M")
    df_txn["year"] = df_txn["date"].dt.to_period("Y")

    df_txn_grouped_base = df_txn.groupby(
        (["category", "year_month", "year"]), as_index=False
    ).agg(
        {
            "amount": "sum",
        }
    )

    df_txn_grouped = df_txn_grouped_base.copy()

    df_txn_grouped = df_txn_grouped[
        ~df_txn_grouped["category"].str.contains("actual", case=False, na=False)
    ]

    ############# Basic Cleanup BUD #######################
    df_bud = pd.DataFrame(bud)
    df_bud["date"] = pd.to_datetime(df_bud["date"])
    df_bud["year_month"] = df_bud["date"].dt.to_period("M")
    df_bud["year"] = df_bud["date"].dt.to_period("Y")
    df_bud = df_bud[df_bud["year_month"].dt.year != 2021]

    df_bud_grouped = df_bud.groupby(
        (["category", "year_month", "year"]), as_index=False
    ).agg(
        {
            "amount": "sum",
        }
    )

    ############# Basic Cleanup INC #######################
    df_inc = pd.DataFrame(inc)
    df_inc["date"] = pd.to_datetime(df_inc["date"])
    df_inc["year_month"] = df_inc["date"].dt.to_period("M")
    df_inc["year"] = df_inc["date"].dt.to_period("Y")
    df_inc = df_inc[df_inc["year_month"].dt.year != 2021]

    df_inc_grouped = df_inc.groupby(
        (["category", "year_month", "year"]), as_index=False
    ).agg(
        {
            "amount": "sum",
        }
    )

    #################JOIN TXN + BUDGET  #################

    merged_df = pd.merge(
        df_txn_grouped,
        df_bud_grouped,
        on=(["category", "year_month", "year"]),
        how="outer",
    )

    merged_df_for_actual = pd.merge(
        df_txn_grouped_base,
        df_bud_grouped,
        on=(["category", "year_month", "year"]),
        how="outer",
    )

    merged_df_for_budgeted = pd.merge(
        df_txn_grouped_base,
        df_bud_grouped,
        on=(["category", "year_month", "year"]),
        how="outer",
    )

    ############### CAPTURE ALL WITH ACTUALS ###############
    merged_df_actual = merged_df_for_actual[
        merged_df_for_actual["category"].str.contains("actual", case=False, na=False)
    ]

    merged_df_actual["amount_x"] = merged_df_actual["amount_x"] * -1

    df_raw_interest = df_txn_grouped.copy()

    #################### some basic cleanup #############
    merged_df["category"] = merged_df["category"].str.capitalize()

    df_rawbudget = df_bud_grouped.copy()

    df_rawbudget["category"] = df_rawbudget["category"].str.capitalize()

    df_rawbudget = df_rawbudget.replace(
        {
            "category": {
                "Etf": "ETF budgeted",
                "Tax": "Tax budgeted",
                "Cushion": "Cushion budgeted",
                "Travel": "Travel budgeted",
            }
        }
    )

    merged_df["category"] = merged_df["category"].str.replace("Actual", "")
    merged_df["category"] = merged_df["category"].str.replace("actual", "")

    merged_df = merged_df.rename(columns={"amount_x": "actual", "amount_y": "budget"})

    merged_df = merged_df[
        ~merged_df["category"].str.contains("actual", case=False, na=False)
    ]

    merged_df = merged_df[
        ~merged_df["category"].str.contains("interest", case=False, na=False)
    ]
    ########JOIN Actual and Budget ###

    #############################CAPTURE BUDGETED #####################################
    df_rawbudget = df_rawbudget[
        df_rawbudget["category"].str.contains("budget", case=False, na=False)
    ]

    #############################CAPTURE BANK BALANCE #####################################

    charts.balance.get_bank_balance_2(
        merged_df, df_rawbudget, merged_df_actual, merged_df, df_raw_interest
    )
    st.divider()
    st.subheader("📊 Budget vs Actual Analysis")
    ################## FILTER SECTION ############################

    # --- YEAR FILTER ---
    year_list = sorted(merged_df["year"].dropna().unique(), reverse=True)
    year_list.insert(0, "All")

    selected_years = st.multiselect("Select Year(s)", year_list, default=["All"])

    # Apply year filter (if not All)
    if "All" in selected_years:
        df_year_filtered = merged_df.copy()
    else:
        df_year_filtered = merged_df[merged_df["year"].isin(selected_years)]

    # --- MONTH FILTER (DEPENDENT ON YEAR) ---
    month_list = sorted(df_year_filtered["year_month"].dropna().unique(), reverse=True)
    month_list.insert(0, "All")

    selected_months = st.multiselect("Select Month(s)", month_list, default=["All"])

    # Apply month filter (if not All)
    if "All" in selected_months:
        df_filtered = df_year_filtered.copy()
    else:
        df_filtered = df_year_filtered[
            df_year_filtered["year_month"].isin(selected_months)
        ]

    ##EXCLUDE ALL INTEREST##

    df_filtered = df_filtered[
        ~df_filtered["category"].str.contains("interest", case=False, na=False)
    ]

    # --- FINAL GROUPBY ---
    table_merged_df = df_filtered.groupby(["category"], as_index=False).agg(
        {"actual": "sum", "budget": "sum"}
    )
    table_merged_df["diff"] = table_merged_df["budget"] - table_merged_df["actual"]

    renamed_df = table_merged_df.rename(
        columns={
            "category": "Expense Category",
            "actual": "Actual Spent",
            "budget": "Budgeted Amount",
            "diff": "Variance",
        }
    )

    ###################### METRICS #####################

    import charts.balance

    charts.balance.metric_sections(renamed_df)

    ############### TABLE CHART ############################

    import charts.dataframe_table

    charts.dataframe_table.generate_table(renamed_df)

    import charts.barchart

    charts.barchart.create_budget_vs_actual_charts(table_merged_df)
    # st.plotly_chart(fig, use_container_width=True)

    import plotly.graph_objects as go
    import plotly.express as px
    import streamlit as st


elif page == "Entry":
    import entry_form

    entry_form.entry_form()
    with st.expander("📊 Monthly Budget Setup"):
        entry_form.budget_form()

    txn = db.fetch_all_transactions()

    ############# Basic Cleanup TXN #######################
    df_txn = pd.DataFrame(txn)
    df_txn["date"] = pd.to_datetime(df_txn["date"])
    df_txn["year_month"] = df_txn["date"].dt.to_period("M")
    df_txn["year"] = df_txn["date"].dt.to_period("Y")

    # df_txn_grouped_base = df_txn.groupby(
    #     (["category", "year_month", "year"]), as_index=False
    # ).agg(
    #     {
    #         "amount": "sum",
    #     }
    # )

    # df_txn_grouped = df_txn_grouped_base.copy()

    # df_txn_grouped = df_txn_grouped[
    #     ~df_txn_grouped["category"].str.contains("actual", case=False, na=False)
    # ]
    with st.expander("Transactions"):
        # Select only specific columns to display
        columns_to_show = ["date", "description", "category", "amount"]
        st.dataframe(df_txn[columns_to_show], use_container_width=True)

        # st.dataframe(df_txn)


elif page == "Travel":
    import entry_form
    import database as db

    ####TRIPS DATA #############
    trips = db.fetch_travel_budget()
    trips_df = pd.DataFrame(trips)
    unique_trips = trips_df["trip"].unique()

    trip_name = st.selectbox(
        "Trip",
        sorted(unique_trips),
        index=0,
        placeholder="Select Trip",
        key="trip",
    )

    entry_form.travel_form(trip_name)
    with st.expander("Travel Budget Setup"):
        entry_form.travel_budget_form()
