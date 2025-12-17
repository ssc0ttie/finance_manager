import plotly.graph_objects as go
import plotly.express as px
import streamlit as st


def create_grouped_barchart_plotly(df):
    """
    Create grouped bar chart (actual and budget side-by-side)
    """
    fig = go.Figure()

    # Add Actual bars
    fig.add_trace(
        go.Bar(
            x=df["category"],
            y=df["actual_local"],
            name="Actual",
            marker_color="#FF6B6B",
            text=[f"${x:,.0f}" for x in df["actual_local"]],
            textposition="outside",
            width=0.4,
            offset=-0.2,  # Offset to create side-by-side effect
        )
    )

    # Add Budget bars
    fig.add_trace(
        go.Bar(
            x=df["category"],
            y=df["budget_local"],
            name="Budget",
            marker_color="#4ECDC4",
            text=[f"${x:,.0f}" for x in df["budget_local"]],
            textposition="outside",
            width=0.4,
            offset=0.2,  # Offset to create side-by-side effect
        )
    )

    # Update layout
    fig.update_layout(
        title="Actual vs Budget by Category",
        title_font_size=16,
        title_x=0.5,
        xaxis_title="Categories",
        yaxis_title="Amount ($)",
        barmode="group",
        height=500,
        hovermode="x unified",
        showlegend=True,
    )

    # Format y-axis
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")

    # Add variance line
    fig.add_trace(
        go.Scatter(
            x=df["category"],
            y=df["diff"],
            name="Variance",
            mode="markers+lines",
            line=dict(color="#FFA726", width=2, dash="dash"),
            marker=dict(size=10),
            yaxis="y2",
        )
    )

    # Add secondary y-axis for variance
    fig.update_layout(
        yaxis2=dict(
            title="Variance ($)",
            overlaying="y",
            side="right",
            tickprefix="$",
            tickformat=",.0f",
        )
    )

    return fig


def create_variance_waterfall(df):
    """
    Create waterfall chart showing variance (Actual - Budget)
    """
    # Sort by variance
    df_sorted = df.sort_values("diff")

    fig = go.Figure()

    # Add bars for each category
    colors = ["red" if x < 0 else "green" for x in df_sorted["diff"]]

    fig.add_trace(
        go.Bar(
            x=df_sorted["category"],
            y=df_sorted["diff"],
            marker_color=colors,
            text=[f"${x:+,.0f}" for x in df_sorted["diff"]],
            textposition="outside",
            name="Variance",
        )
    )

    fig.update_layout(
        title="Budget Variance by Category (Actual - Budget)",
        title_font_size=16,
        title_x=0.5,
        xaxis_title="Categories",
        yaxis_title="Variance ($)",
        height=500,
        showlegend=False,
    )

    fig.update_yaxes(tickprefix="$", tickformat=",.0f")

    # Add reference line at 0
    fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="gray")

    return fig


# Usage


def create_budget_vs_actual_charts(df):
    """
    Create multiple visualizations for budget vs actual analysis
    """
    # st.subheader("📊 Budget vs Actual Analysis")

    # 1. Grouped bar chart
    fig1 = create_grouped_barchart_plotly(df)
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # 2. Variance waterfall chart
        fig2 = create_variance_waterfall(df)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # 3. Donut chart for actual distribution
        fig3 = go.Figure(
            data=[
                go.Pie(
                    labels=df["category"],
                    values=df["actual_sgd"],
                    hole=0.3,
                    textinfo="label+percent",
                    textposition="inside",
                    marker=dict(colors=px.colors.qualitative.Set3),
                )
            ]
        )
        fig3.update_layout(title="Actual Spending Distribution")
        st.plotly_chart(fig3, use_container_width=True)
