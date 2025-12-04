import streamlit as st
import database as db
import pandas as pd


st.set_page_config(
    page_title="Finance Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


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

    """fetch all data once"""
    txn = db.fetch_all_transactions()
    bud = db.fetch_all_budget()
    inc = db.fetch_all_income()

    ############# Basic Cleanup TXN #######################
    df_txn = pd.DataFrame(txn)
    df_txn["date"] = pd.to_datetime(df_txn["date"])
    df_txn["year_month"] = df_txn["date"].dt.to_period("M")

    df_txn_grouped = df_txn.groupby((["category", "year_month"]), as_index=False).agg(
        {
            "amount": "sum",
        }
    )

    ############# Basic Cleanup BUD #######################
    df_bud = pd.DataFrame(bud)
    df_bud["date"] = pd.to_datetime(df_bud["date"])
    df_bud["year_month"] = df_bud["date"].dt.to_period("M")

    df_bud_grouped = df_bud.groupby((["category", "year_month"]), as_index=False).agg(
        {
            "amount": "sum",
        }
    )

    #################JOIN TXN + BUDGET  #################

    merged_df = pd.merge(
        df_txn_grouped, df_bud_grouped, on=(["category", "year_month"]), how="outer"
    )

    merged_df = merged_df[
        ~merged_df["category"].isin(
            ["ETF Actual", "Travel Actual", "Tax Actual", "Cushion Actual", 0]
        )
    ]  # filter non running activity

    #################### some basic cleanup #############
    merged_df = merged_df.rename(columns={"amount_x": "actual", "amount_y": "budget"})
    # merged_df["diff"] = merged_df["budget"] - merged_df["actual"]
    merged_df["category"] = merged_df["category"].str.capitalize()

    # merged_df["amount_formatted"] = merged_df["actual"].apply(lambda x: f"${x:,.2f}")

    ########JOIN Actual and Budget ###

    ################## FILTER SECTION ############################
    month = sorted(merged_df["year_month"].dropna().unique(), reverse=True)
    month.insert(0, "All")
    selected_month = st.multiselect("Select Month(s)", month, default=["All"])

    if not selected_month or "All" in selected_month:
        merged_df = merged_df
    else:
        merged_df = merged_df[merged_df["year_month"].isin(selected_month)]

    table_merged_df = merged_df.groupby((["category"]), as_index=False).agg(
        {
            "actual": "sum",
            "budget": "sum",
        }
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
