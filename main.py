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
            # "Travel",
            "Investment",
            "Help",
            "Entry",
        ],
    )

##PAGE##
st.session_state.active_page = page

if page == "Goodget":

    st.header("💰 Goodget - Personal Budget Tracker")
    st.divider()
    # """fetch all data once"""
    txn = db.fetch_all_transactions()
    bud = db.fetch_all_budget()
    inc = db.fetch_all_income()
    cats = db.fetch_category()

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

    ############ CAPTURE ALL WITH ACTUALS ######
    df_txn_grouped_actuals = df_txn_grouped_base[
        df_txn_grouped_base["category"].str.contains("actual", case=False, na=False)
    ]
    df_txn_grouped_actuals_interest = df_txn_grouped_base[
        df_txn_grouped_base["category"].str.contains("interest", case=False, na=False)
    ]

    # df_txn_grouped_actuals_interest["amount"] = (
    #     df_txn_grouped_actuals_interest["amount"] * -1
    # )

    df_txn_grouped_actuals_all = pd.concat(
        [df_txn_grouped_actuals, df_txn_grouped_actuals_interest], ignore_index=True
    )

    # df_txn_grouped_actuals = df_txn_grouped_actuals.groupby(
    #     (["category", "year_month", "year"]), as_index=False
    # ).agg(
    #     {
    #         "amount": "sum",
    #     }
    # )
    # st.dataframe(df_txn_grouped_actuals)
    # st.dataframe(df_txn_grouped_actuals_interest)
    # st.dataframe(df_txn_grouped_actuals_all)

    totat_by_cat = df_txn_grouped_actuals_all.groupby(
        (["category"]), as_index=False
    ).agg(
        {
            "amount": "sum",
        }
    )

    st.dataframe(totat_by_cat)

    "GOODS ^"

    total_of_all_with_actual = df_txn_grouped_actuals_all["amount"].sum()
    st.write(total_of_all_with_actual)

    df_cats = pd.DataFrame(cats)

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

    merged_df_presegment = pd.merge(
        df_txn_grouped,
        df_cats,
        on=(["category"]),
        how="outer",
    )

    merged_df = pd.merge(
        merged_df_presegment,
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

    # st.dataframe(merged_df_for_actual)

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

    # merged_df_actual["amount_x"] = merged_df_actual["amount_x"] * -1

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
    st.write("budget raw")
    df_rawbudget = df_rawbudget.groupby(["category"]).agg(
        {
            "amount": "sum",
        }
    )

    st.dataframe(df_rawbudget)
    st.write(df_rawbudget["amount"].sum())

    "GOODS Budget raw^"
    total_merged_df_bycat = merged_df.groupby(["category"]).agg(
        {
            "actual": "sum",
            "budget": "sum",
        }
    )

    st.dataframe(total_merged_df_bycat)

    total_merged_df = total_merged_df_bycat["actual"].sum()
    st.write(total_merged_df)

    "GOODS Actual Spend^"
    st.dataframe(total_merged_df_bycat)

    total_merged_df_budget = total_merged_df_bycat["budget"].sum()
    st.write(total_merged_df_budget)

    "GOODS Budget Spend^"
    #############################CAPTURE BANK BALANCE #####################################

    charts.balance.get_bank_balance_2(
        merged_df, df_rawbudget, totat_by_cat, merged_df, df_raw_interest
    )
    st.divider()
    st.subheader("📊 Expenses :  Budget vs Actual Analysis")
    ################## FILTER SECTION ############################

    # --- GET LATEST YEAR AND MONTH FROM DATA ---
    # Extract the latest year (assuming 'year' is numeric)
    latest_year = merged_df["year"].max()
    # Extract the latest month in format "YYYY-MM" from 'year_month' column
    latest_year_month = merged_df["year_month"].max()
    # --- YEAR FILTER ---
    year_list = sorted(merged_df["year"].dropna().unique(), reverse=True)
    year_list.insert(0, "All")

    selected_years = st.multiselect("Select Year(s)", year_list, default=[latest_year])

    # Apply year filter (if not All)
    if "All" in selected_years:
        df_year_filtered = merged_df.copy()
    else:
        df_year_filtered = merged_df[merged_df["year"].isin(selected_years)]

    # --- MONTH FILTER (DEPENDENT ON YEAR) ---
    month_list = sorted(df_year_filtered["year_month"].dropna().unique(), reverse=True)
    month_list.insert(0, "All")

    selected_months = st.multiselect(
        "Select Month(s)", month_list, default=[latest_year_month]
    )

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

    # Single selection - users pick ONE grouping level
    selected_group = st.selectbox(
        "Select View",
        # ["segment", "category", "segment,category"],  # Add combined option
        ["category"],  # Add combined option
        index=0,
    )

    # Convert string to list for groupby
    group_cols = selected_group.split(",")

    # Group by selected columns
    dynamic_table_merged_df_filtered = df_filtered.groupby(
        group_cols, as_index=False
    ).agg({"actual": "sum", "budget": "sum"})

    table_merged_df = df_filtered.groupby("category", as_index=False).agg(
        {"actual": "sum", "budget": "sum"}
    )

    table_merged_df["diff"] = table_merged_df["budget"] - table_merged_df["actual"]

    dynamic_table_merged_df_filtered["diff"] = (
        dynamic_table_merged_df_filtered["budget"]
        - dynamic_table_merged_df_filtered["actual"]
    )

    renamed_df_dynamic = dynamic_table_merged_df_filtered.rename(
        columns={
            # "category": "Expense Category",
            "actual": "Actual Spent",
            "budget": "Budgeted Amount",
            "diff": "Variance",
        }
    )
    renamed_df = table_merged_df.rename(
        columns={
            "category": "Expense Category",
            "actual": "Actual Spent",
            "budget": "Budgeted Amount",
            "diff": "Variance",
        }
    )

    ###################### METRICS #####################

    import diagnostics

    # diagnostics.diagnose_totals_mismatch(df_filtered)

    import charts.balance

    charts.balance.metric_sections(renamed_df_dynamic)

    ############### TABLE CHART ############################

    import charts.dataframe_table

    charts.dataframe_table.generate_table(renamed_df_dynamic)

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


# elif page == "Travel":
#     import entry_form
#     import database as db
#     import charts.barchart_travel

#     st.header("💰 Travel Expense - Analyzer")
#     st.divider()

#     ####FETCH ALL TRIPS DATA #############

#     trips_actual = db.fetch_travel_actual()
#     trips_budget = db.fetch_travel_budget()

#     df_trips_budget = pd.DataFrame(trips_budget)
#     df_trips_actual = pd.DataFrame(trips_actual)

#     unique_trips = df_trips_budget["trip"].unique()
#     unique_remarks = df_trips_budget["remarks"].unique()
#     unique_remarks = df_trips_budget["remarks"].notna()

#     ############# Basic Cleanup travel budget #######################
#     df_trips_budget["date"] = pd.to_datetime(df_trips_budget["date"])
#     df_trips_budget_grouped = df_trips_budget.groupby(
#         (["category", "trip", "remarks"]), as_index=False
#     ).agg(
#         {
#             "budget_sgd": "sum",
#             "budget_local": "sum",
#         }
#     )
#     ############# Basic Cleanup travel actual #######################
#     df_trips_actual["date"] = pd.to_datetime(df_trips_actual["date"])
#     df_trips_actual_grouped = df_trips_actual.groupby(
#         (["category", "trip", "remarks"]), as_index=False
#     ).agg(
#         {
#             "actual_sgd": "sum",
#             "actual_local": "sum",
#         }
#     )

#     #################JOIN TXN + BUDGET  #################

#     merged_df_travel = pd.merge(
#         df_trips_actual_grouped,
#         df_trips_budget_grouped,
#         on=(["category", "trip", "remarks"]),
#         how="outer",
#     )

#     #################### some basic cleanup #############
#     merged_df_travel["category"] = merged_df_travel["category"].str.capitalize()
#     merged_df_travel["diff"] = (
#         merged_df_travel["budget_sgd"] - merged_df_travel["actual_sgd"]
#     )
#     merged_df_travel["diff_local"] = (
#         merged_df_travel["budget_local"] - merged_df_travel["actual_local"]
#     )
#     ################## FILTER SECTION ############################
#     st.subheader("📊 Travel Expenses :  Budget vs Actual Analysis")
#     # --- Trip FILTER ---
#     trip_list = sorted(merged_df_travel["trip"].dropna().unique(), reverse=True)
#     trip_list.insert(0, "All")

#     selected_trip = st.multiselect("Select Trip", trip_list, default=["All"])

#     # Apply year filter (if not All)
#     if "All" in selected_trip:
#         df_trip_filtered = merged_df_travel.copy()
#     else:
#         df_trip_filtered = merged_df_travel[
#             merged_df_travel["trip"].isin(selected_trip)
#         ]

#     ################### CHARTS SECTION ###################
#     charts.balance.metric_sections_travel(df_trip_filtered)

#     # Get numeric columns
#     numeric_columns = df_trip_filtered.select_dtypes(
#         include=["int64", "float64"]
#     ).columns

#     # Create format dictionary for all numeric columns
#     format_dict = {col: "{:,.0f}" for col in numeric_columns}

#     st.dataframe(df_trip_filtered.style.format(format_dict), use_container_width=True)

#     charts.barchart_travel.create_budget_vs_actual_charts(df_trip_filtered)

#     trip_name = st.selectbox(
#         "Trip",
#         sorted(unique_trips),
#         index=0,
#         placeholder="Select Trip",
#         key="trip",
#     )

#     trip_remarks = st.selectbox(
#         "Remarks",
#         sorted(unique_remarks),
#         index=0,
#         placeholder="Remarks",
#         key="remarks",
#     )

#     entry_form.travel_form(trip_name)
#     with st.expander("Travel Budget Setup"):
#         entry_form.travel_budget_form()


if page == "Investment":

    txn = db.fetch_all_transactions()

    df_tnx = pd.DataFrame(txn)

    cats_to_keep = ["Investment", "Cushion Actual"]
    df_inv = df_tnx[df_tnx["category"].isin(cats_to_keep)]
    sum_inv = df_tnx["amount"].sum()

    st.dataframe(df_inv)
    st.write(f"Sum of investment {sum_inv}")

    ########## HARD CODE ##################

    assets_data = [
        {"Asset": "Real Estate Athena", "Amount": 29002.69},
        {"Asset": "Real Estate Pasong Buaya", "Amount": 15557.89},
        {"Asset": "Mutual Fund PH", "Amount": 2217.17},
        {"Asset": "STOCKS", "Amount": 2700.00},
        {"Asset": "ETF", "Amount": 22735.00},
        {"Asset": "Crypto", "Amount": 903.19},
    ]
    df_assets = pd.DataFrame(assets_data)
    st.dataframe(df_assets)
