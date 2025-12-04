# db.py
import streamlit as st
from supabase import create_client, Client
import os


# Try to get credentials from Streamlit secrets or environment
def get_supabase_client():
    try:
        # First try Streamlit secrets
        url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
        key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY"))

        if not url or not key:
            st.error(
                "❌ Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets."
            )
            return None

        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Failed to create Supabase client: {e}")
        return None


# Initialize supabase client
supabase = get_supabase_client()


# Initialize connection to Supabase
@st.cache_resource
def init_connection():
    try:
        supabase_url: str = st.secrets["supabase"]["url"]
        supabase_key: str = st.secrets["supabase"]["service_key"]
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


supabase = init_connection()
