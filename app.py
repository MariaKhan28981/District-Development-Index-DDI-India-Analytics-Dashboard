import streamlit as st
import pandas as pd
import plotly.express as px


# -------------------------
# Page Config
# -------------------------

st.set_page_config(
    page_title="District Development Index",
    page_icon="📊",
    layout="wide"
)


# -------------------------
# Load Data
# -------------------------

@st.cache_data
def load_data():

    district = pd.read_csv(
        "data/processed/district_development_index.csv"
    )

    state = pd.read_csv(
        "data/processed/state_summary.csv"
    )

    return district, state


df, state_df = load_data()


# -------------------------
# Title
# -------------------------

st.title(
    "🇮🇳 District Development Index (DDI)"
)

st.markdown(
    """
    ### Data-driven district development analysis dashboard
    GDP + Growth based development scoring
    """
)


# -------------------------
# KPI Cards
# -------------------------

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "States Covered",
    df["State"].nunique()
)

col2.metric(
    "Districts Covered",
    df["District"].nunique()
)

col3.metric(
    "Years",
    df["Year"].nunique()
)

col4.metric(
    "Total Records",
    len(df)
)



# -------------------------
# Sidebar
# -------------------------

st.sidebar.header("Filters")


selected_state = st.sidebar.selectbox(
    "Select State",
    sorted(df["State"].unique())
)


state_data = df[
    df["State"] == selected_state
]


selected_district = st.sidebar.selectbox(
    "Select District",
    sorted(state_data["District"].unique())
)


district_data = state_data[
    state_data["District"] == selected_district
]



# -------------------------
# District Analysis
# -------------------------

st.header(
    f"📍 {selected_district}, {selected_state}"
)


c1,c2,c3 = st.columns(3)


c1.metric(
    "Latest GDP",
    round(
        district_data.iloc[-1]["GDP"],
        2
    )
)


c2.metric(
    "Latest Growth %",
    round(
        district_data.iloc[-1]["GrowthRate"],
        2
    )
)


c3.metric(
    "DDI Score",
    round(
        district_data.iloc[-1]["DDI"],
        3
    )
)



# GDP trend

fig = px.line(
    district_data,
    x="Year",
    y="GDP",
    title="GDP Trend"
)

st.plotly_chart(fig, use_container_width=True)



# Growth trend

fig2 = px.line(
    district_data,
    x="Year",
    y="GrowthRate",
    title="Growth Rate Trend"
)

st.plotly_chart(fig2, use_container_width=True)



# -------------------------
# State Ranking
# -------------------------

st.header("🏆 State Performance Ranking")


fig3 = px.bar(
    state_df.sort_values(
        "Avg_DDI",
        ascending=False
    ),
    x="State",
    y="Avg_DDI",
    title="Average Development Index by State"
)


st.plotly_chart(
    fig3,
    use_container_width=True
)


st.dataframe(
    state_df.sort_values(
        "Avg_DDI",
        ascending=False
    ),
    use_container_width=True
)