import streamlit as st
import datetime as dt
import database as db
import pandas as pd


def entry_form():
    cat = db.fetch_category()
    df_cat = pd.DataFrame(cat)
    unique_cat = df_cat["category"].unique()
    today = dt.date.today()

    with st.form("entry", clear_on_submit=True, border=True):
        # Activity list
        exp_type = st.selectbox(
            "Type",
            sorted(
                [
                    "Travel",
                    "Regular",
                    "Shared Expense",
                ],
            ),
            index=0,
            placeholder="Select Type",
            key="type",
        )
        expense = st.selectbox(
            "Expense",
            sorted(unique_cat),
            # ),
            index=None,
            placeholder="Select Expense",
            key="expense",
        )
        exp_date = st.date_input("Select a date", value=today, key="date")

        desc = st.text_area(
            "Description", placeholder="describe is this expense", key="desc"
        )

        exp_amount = st.number_input("Insert $Amount")

        submitted_exp = st.form_submit_button("Submit Expense", type="primary")

        if submitted_exp:
            new_log = [
                exp_type,
                expense,
                exp_date,
                desc,
                exp_amount,
            ]

            # store for reference
            st.session_state["pending_log"] = new_log

            # Insert into database
            result = db.add_expense(
                exp_type,
                expense,
                exp_date.isoformat(),  # must be string for JSON
                desc,
                exp_amount,
            )

            if result:
                st.success("✅ Your expense was successfully recorded!")
                st.write(result)
                st.balloons()
            else:
                st.error("Something went wrong while saving the expense.")


def budget_form():
    cat = db.fetch_category()
    df_cat = pd.DataFrame(cat)
    unique_cat = df_cat["category"].unique()
    today = dt.date.today()

    # df_txn["date"] = pd.to_datetime(df_txn["date"])
    # df_txn["year_month"] = df_txn["date"].dt.to_period("M")

    ############# DEFAULT BUDGET ######################

    # --- Your predefined dataframe ---
    default_bud_df = pd.DataFrame(
        {
            "amount": [
                450.00,
                700.00,
                120.00,
                85.00,
                120.00,
                200.00,
                130.00,
                220.00,
                50.00,
                50.00,
                100.00,
                55.00,
                400.00,
                800.00,
                500.00,
                20.00,
            ],
            "category": [
                "Food",
                "Home",
                "Transportation",
                "Utilities",
                "Insurance",
                "Tax",
                "Gifts",
                "Pinas",
                "Entertainment",
                "Sports / Health",
                "Eat out",
                "Others",
                "Travel",
                "ETF",
                "Cushion",
                "Education",
            ],
        }
    )

    cat = db.fetch_category()  # Your category list from DB
    df_cat = pd.DataFrame(cat)
    unique_cat = df_cat["category"].unique()

    with st.form("edit_entries_form"):
        edited_df = st.data_editor(
            default_bud_df,
            column_config={
                "category": st.column_config.SelectboxColumn(
                    "Expense Category",
                    options=sorted(unique_cat),
                    help="Select or change the category",
                ),
                "amount": st.column_config.NumberColumn(
                    "Amount ($)",
                    min_value=0.0,
                    step=1.0,
                    format="%.2f",
                    help="Budgeted amount for this month",
                ),
            },
            use_container_width=True,
            num_rows="dynamic",  # allow adding/removing rows
        )

        submitted = st.form_submit_button("💾 Submit Budget")

        if submitted:
            # Insert each row into Supabase ─ one per budget line
            for _, row in edited_df.iterrows():
                db.add_budget(
                    expense=row["category"],
                    date=dt.date.today().replace(day=1).isoformat(),  # or full ISO date
                    amount=float(row["amount"]),
                )

            st.success("✅ Monthly budget has been updated successfully!")
            st.balloons()


def travel_form(trip):
    cat = db.fetch_category()
    df_cat = pd.DataFrame(cat)
    unique_cat = df_cat["category"].unique()
    today = dt.date.today()

    # --- Your predefined dataframe ---
    default_bud_df = pd.DataFrame(
        {
            "category": [
                "Food",
                "Airfare",
                "Transportation",
                "Others",
                "Shopping",
                "Accoms",
                "Insurance",
                "Roaming",
                "Activity",
                "Ski",
                "Emergency",
                "Miscellaneous",
            ],
        }
    )

    default_payment_df = pd.DataFrame(
        {
            "payment": [
                "YouTrip",
                "Scott CC",
                "Chona CC",
                "Cash",
            ],
        }
    )

    unique_cat = default_bud_df["category"].unique()
    unique_payment = default_payment_df["payment"].unique()

    ###DEFINE TRIP####
    # travel_budget = db.fetch_travel_budget()
    # trip_df = pd.DataFrame(travel_budget)
    # # budgetted_trip = sorted(trip_df["category"].unique())

    with st.form("entry", clear_on_submit=True, border=True):
        st.write("Enter Actual Expense Here:")
        # Activity list
        exp = st.selectbox(
            "Expense",
            sorted(unique_cat),
            index=0,
            placeholder="Select Type",
            key="type",
        )
        exp_date = st.date_input("Select a date", value=today, key="date")

        desc = st.text_area(
            "Description", placeholder="describe is this expense", key="desc"
        )
        exp_payment = st.selectbox(
            "Payment Type",
            sorted(unique_payment),
            index=0,
            placeholder="Select Type",
            key="payment_type",
        )

        exp_amount = st.number_input("Insert $Amount *Convert to SGD ")

        submitted_exp = st.form_submit_button("Submit Expense", type="primary")

        if submitted_exp:
            new_log = [
                trip,
                exp,
                exp_date,
                desc,
                exp_amount,
                exp_payment,
            ]

            # store for reference
            st.session_state["pending_log"] = new_log

            # Insert into database
            result = db.add_travel_expense(
                trip,
                exp,
                exp_date.isoformat(),  # must be string for JSON
                desc,
                exp_amount,
                exp_payment,
            )

            if result:
                st.success("✅ Your expense was successfully recorded!")
                st.write(result)
                st.balloons()
            else:
                st.error("Something went wrong while saving the expense.")


def travel_budget_form():

    ############# DEFAULT BUDGET ######################

    # --- Your predefined dataframe ---
    default_travel_bud_df = pd.DataFrame(
        {
            "amount": [
                0.00,
                0.00,
                0.00,
                0.00,
                0.00,
                0.00,
                0.00,
                0.00,
                0.00,
                0.00,
                0.00,
                0.00,
                0.00,
            ],
            "category": [
                "Food",
                "Airfare",
                "Transportation",
                "Others",
                "Shopping",
                "Accoms",
                "Insurance",
                "Roaming",
                "Activity",
                "Ski",
                "Emergency",
                "Miscellaneous",
                "Gift",
            ],
        }
    )

    unique_cat = default_travel_bud_df["category"].unique()

    with st.form("edit_entries_form"):
        trip_name = st.text_input("Trip:", "Type Trip Here")
        edited_df = st.data_editor(
            default_travel_bud_df,
            column_config={
                "category": st.column_config.SelectboxColumn(
                    "Travel Expense Category",
                    options=sorted(unique_cat),
                    help="Select or change the category",
                ),
                "amount": st.column_config.NumberColumn(
                    "Amount ($):",
                    min_value=0.0,
                    step=1.0,
                    format="%.2f",
                    help="Budgeted amount for this trip",
                ),
                # "trip": st.column_config.TextColumn(
                #     "Trip Name",
                #     help="Name of the trip",
                #     default=trip_input,  # Use the text input value as default
                # ),
            },
            use_container_width=True,
            num_rows="dynamic",  # allow adding/removing rows
        )

        submitted = st.form_submit_button("💾 Submit Travel Budget")

        if submitted:
            # Insert each row into Supabase ─ one per budget line
            if trip_name and trip_name != "Type Trip Here":
                for _, row in edited_df.iterrows():
                    db.add_travel_budget(
                        trip=trip_name,
                        expense=row["category"],
                        date=dt.date.today()
                        .replace(day=1)
                        .isoformat(),  # or full ISO date
                        amount=float(row["amount"]),
                    )

                st.success("✅ Monthly budget has been updated successfully!")
                st.balloons()
            else:
                st.error("Please enter a valid trip name!")
