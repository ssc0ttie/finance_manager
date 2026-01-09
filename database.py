import supabase_client
import streamlit as st


supabase = supabase_client.init_connection()
# # Initialize supabase client
# supabase = supabase_client.get_supabase_client()


def fetch_all_transactions(page_size=1000):
    all_rows = []
    start = 0

    while True:
        end = start + page_size - 1

        response = (
            supabase.table("transactions").select("*").range(start, end).execute()
        )

        batch = response.data

        # Stop when no more results
        if not batch:
            break

        all_rows.extend(batch)
        start += page_size

    return all_rows


def fetch_category():
    try:
        response = supabase.table("category").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []


def fetch_all_budget(page_size=1000):
    all_rows = []
    start = 0

    while True:
        end = start + page_size - 1

        response = supabase.table("budget").select("*").range(start, end).execute()

        batch = response.data

        # Stop when no more results
        if not batch:
            break

        all_rows.extend(batch)
        start += page_size

    return all_rows


def fetch_all_income(page_size=1000):
    all_rows = []
    start = 0

    while True:
        end = start + page_size - 1

        response = supabase.table("budget").select("*").range(start, end).execute()

        batch = response.data

        # Stop when no more results
        if not batch:
            break

        all_rows.extend(batch)
        start += page_size

    return all_rows


def fetch_travel_budget(page_size=1000):
    all_rows = []
    start = 0

    while True:
        end = start + page_size - 1

        response = (
            supabase.table("travel_budget").select("*").range(start, end).execute()
        )

        batch = response.data

        # Stop when no more results
        if not batch:
            break

        all_rows.extend(batch)
        start += page_size

    return all_rows


def fetch_travel_actual(page_size=1000):
    all_rows = []
    start = 0

    while True:
        end = start + page_size - 1

        response = (
            supabase.table("travel_actual").select("*").range(start, end).execute()
        )

        batch = response.data

        # Stop when no more results
        if not batch:
            break

        all_rows.extend(batch)
        start += page_size

    return all_rows


def add_expense(type, expense, date, desc, amount):
    try:
        expense_data = {
            "type": type,
            "category": expense,
            "date": date,
            "description": desc,
            "amount": amount,
        }
        response = supabase.table("transactions").insert(expense_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error adding expense: {e}")
        return None


def add_budget(expense, date, amount):
    try:
        # convert date to string if needed
        if hasattr(date, "isoformat"):
            date = date.isoformat()

        budget_data = {
            "category": expense,
            "date": date,
            "amount": float(amount),
        }

        response = supabase.table("budget").insert(budget_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error adding budget: {e}")
        return None


def add_travel_budget(trip, expense, date, amount):
    try:
        # convert date to string if needed
        if hasattr(date, "isoformat"):
            date = date.isoformat()

        budget_data = {
            "trip": trip,
            "category": expense,
            "date": date,
            "amount": float(amount),
        }

        response = supabase.table("travel_budget").insert(budget_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error adding budget: {e}")
        return None


def add_travel_expense(trip, expense, date, desc, amount, payment):
    try:
        expense_data = {
            "trip": trip,
            "category": expense,
            "date": date,
            "description": desc,
            "actual_sgd": amount,
            "payment": payment,
        }
        response = supabase.table("travel_actual").insert(expense_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error adding expense: {e}")
        return None
