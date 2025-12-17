import streamlit as st
import pandas as pd


def diagnose_totals_mismatch(df):
    """Comprehensive diagnostic for grouping mismatches"""

    st.header("🔍 Totals Mismatch Diagnostic")

    # 1. Basic totals comparison
    total_raw = df["actual"].sum()
    total_cat = df.groupby("category")["actual"].sum().sum()
    total_seg = df.groupby("segment")["actual"].sum().sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Raw Total", f"${total_raw:,.2f}", delta=None)
    with col2:
        st.metric(
            "By Category", f"${total_cat:,.2f}", delta=f"${total_cat-total_raw:,.2f}"
        )
    with col3:
        st.metric(
            "By Segment", f"${total_seg:,.2f}", delta=f"${total_seg-total_raw:,.2f}"
        )

    # 2. Detailed analysis
    with st.expander("📈 Detailed Analysis", expanded=True):
        tab1, tab2, tab3 = st.tabs(["Missing Data", "Value Issues", "Sample Check"])

        with tab1:
            # Missing values
            missing = pd.DataFrame(
                {
                    "Column": ["category", "segment", "actual"],
                    "Null Count": df[["category", "segment", "actual"]]
                    .isna()
                    .sum()
                    .values,
                    "% Missing": (
                        df[["category", "segment", "actual"]].isna().sum()
                        / len(df)
                        * 100
                    )
                    .round(2)
                    .values,
                }
            )
            st.dataframe(missing)

            if missing["Null Count"].sum() > 0:
                st.warning(
                    f"**{missing['Null Count'].sum()} rows have missing values**"
                )
                st.write("Rows with ANY null:")
                st.dataframe(df[df.isna().any(axis=1)].head())

        with tab2:
            # Value consistency
            st.write("**Category value sample:**")
            st.write(df["category"].value_counts().head(10))

            st.write("**Segment value sample:**")
            st.write(df["segment"].value_counts().head(10))

            # Check for whitespace issues
            cat_with_spaces = df[
                df["category"].astype(str).str.contains(r"^\s+|\s+$", na=False)
            ]
            seg_with_spaces = df[
                df["segment"].astype(str).str.contains(r"^\s+|\s+$", na=False)
            ]

            if len(cat_with_spaces) > 0:
                st.warning(
                    f"{len(cat_with_spaces)} category values have leading/trailing spaces"
                )
            if len(seg_with_spaces) > 0:
                st.warning(
                    f"{len(seg_with_spaces)} segment values have leading/trailing spaces"
                )

        with tab3:
            # Sample of problem rows
            st.write("**First 10 rows of data:**")
            st.dataframe(df[["category", "segment", "actual"]].head(10))

    return total_raw, total_cat, total_seg
