import streamlit as st
import pandas as pd
import plotly.express as px
import json
import folium
from streamlit_folium import st_folium
import random



# ================= CONFIG =================

st.set_page_config(
    page_title="India District Development Index",
    layout="wide"
)



# ================= STYLE =================


st.markdown(
"""
<style>

.main{
background:#f6fbf7;
}


.card{

background:white;
padding:20px;
border-radius:20px;

box-shadow:
0 8px 25px rgba(0,0,0,0.12);

text-align:center;

border-top:5px solid #138808;

}


.big{

font-size:30px;
font-weight:800;

}


.small{

font-size:15px;
color:#555;

}


.title{

font-size:28px;
font-weight:800;
color:#075985;
margin-top:25px;

}


.hero{

background:
linear-gradient(
135deg,
#ff9933,
#ffffff,
#138808
);

padding:35px;
border-radius:25px;

box-shadow:
0 10px 30px rgba(0,0,0,0.15);

}



.footer{

text-align:center;
padding:20px;
color:#555;

}


</style>
""",
unsafe_allow_html=True
)




# ================= LOAD =================


@st.cache_data
def load_data():

    df=pd.read_csv(
        "data/processed/district_development_index.csv"
    )


    df["State"]=df.State.str.strip()
    df["District"]=df.District.str.strip()

    df["Year"]=df.Year.astype(int)

    return df



ddi=load_data()



@st.cache_data
def load_geojson():

    with open(
        "data/geojson/india_district.geojson",
        encoding="utf-8"
    ) as f:

        return json.load(f)



geojson=load_geojson()






# ================= HERO =================


facts=[

"India's economy is driven by unequal regional growth.",

"Large GDP districts are not always the most developed.",

"DDI combines economic size and growth behaviour.",

"District level analysis helps targeted development planning.",

"Economic progress is different across regions.",

"Growth rate shows how quickly an economy changes.",

"Development is a long term process.",

"Data helps convert observations into decisions.",

"Districts provide a closer view than state averages.",

"Balanced growth matters more than GDP alone."

]




st.markdown(
"""
<div class="hero">

<h1>🇮🇳 India District Development Index</h1>

<h3>
Interactive District-Level Economic Analytics Dashboard
</h3>


</div>

""",
unsafe_allow_html=True
)



a,b,c=st.columns(3)



with a:
    st.info(
        random.choice(facts)
    )


with b:
    st.success(
        f"""
        📍 {ddi.District.nunique()}
        
        Districts analysed
        """
    )


with c:
    st.warning(
        """
        📅 1999-2012
        
        GDP period covered
        """
    )




with st.expander("📘 How to use this dashboard"):

    st.write(
"""
1. Select a state.

2. Choose year and district.

3. Compare GDP, growth, DDI and rankings.

4. Explore charts and development map.


**Terms**

GDP:
District economic output (₹ Crore).


Growth Rate:
Year-to-year GDP change.


DDI:
Composite development score.

Higher DDI means stronger relative performance.
"""
)





# ================= FILTERS =================


st.markdown(
"<div class='title'>🎛️ Select Analysis</div>",
unsafe_allow_html=True
)



x,y,z=st.columns(3)



with x:

    state=st.selectbox(
        "Select State",
        sorted(ddi.State.unique())
    )



state_data=ddi[
    ddi.State==state
]



with y:

    years=sorted(
        state_data.Year.unique()
    )

    year=st.slider(
        "Select Year",
        min(years),
        max(years),
        max(years)
    )



year_data=state_data[
    state_data.Year==year
]



with z:

    district=st.selectbox(
        "Select District",
        sorted(
            year_data.District.unique()
        )
    )

# ================= STATE OVERVIEW =================


st.markdown(
"<div class='title'>🏛️ State Overview</div>",
unsafe_allow_html=True
)



# unique districts only
state_unique = (
    state_data
    .groupby("District")
    .agg(
        GDP=("GDP","mean"),
        GrowthRate=("GrowthRate","mean"),
        DDI=("DDI","mean")
    )
    .reset_index()
)



state_avg_gdp = state_unique.GDP.mean()

state_avg_growth = state_unique.GrowthRate.mean()

state_avg_ddi = state_unique.DDI.mean()

state_districts = state_unique.District.nunique()



s1,s2,s3,s4 = st.columns(4)



overview=[

(
"📍 Districts",
f"{state_districts}"
),

(
"💰 Avg GDP",
f"₹ {state_avg_gdp:,.0f} Cr"
),

(
"📈 Avg Growth",
f"{state_avg_growth:.2f}%"
),

(
"📊 Avg DDI",
f"{state_avg_ddi:.3f}"
)

]



for col,(title,value) in zip(
    [s1,s2,s3,s4],
    overview
):

    with col:

        st.markdown(
        f"""
        <div class="card">

        <div class="small">
        {title}
        </div>


        <div class="big">
        {value}
        </div>

        </div>
        """,
        unsafe_allow_html=True
        )






# ================= RANKING =================



selected = year_data[
    year_data.District==district
].iloc[0]



# state rank

state_rank_df=(
    year_data
    .sort_values(
        "DDI",
        ascending=False
    )
    .reset_index(drop=True)
)



state_rank_df["Rank"]=(
    state_rank_df.index+1
)



state_rank=int(
    state_rank_df[
        state_rank_df.District==district
    ].Rank.iloc[0]
)





# India rank

india_year=(
    ddi[
        ddi.Year==year
    ]
    .sort_values(
        "DDI",
        ascending=False
    )
    .reset_index(drop=True)
)



india_year["Rank"]=(
    india_year.index+1
)



india_rank=int(
    india_year[
        india_year.District==district
    ].Rank.iloc[0]
)





# category based on percentile

percentile=(
    india_year["DDI"]
    .rank(pct=True)
    .iloc[
        india_year[
            india_year.District==district
        ].index[0]
    ]
)



if percentile>=0.75:

    category="🟢 High Development"


elif percentile>=0.50:

    category="🟡 Medium Development"


else:

    category="🔴 Low Development"





# ================= DISTRICT METRICS =================



st.markdown(
"<div class='title'>📊 District Overview</div>",
unsafe_allow_html=True
)




m1,m2,m3,m4,m5=st.columns(5)



metrics=[


(
"💰 GDP",
f"₹ {selected.GDP:,.0f} Cr"
),


(
"📈 Growth",
f"{selected.GrowthRate:.2f}%"
),


(
"🏆 State Rank",
f"#{state_rank}"
),


(
"🌎 India Rank",
f"#{india_rank}"
),


(
"📊 DDI",
f"{selected.DDI:.3f}"
)

]



for col,(title,value) in zip(
    [m1,m2,m3,m4,m5],
    metrics
):

    with col:

        st.markdown(
        f"""
        <div class="card">

        <div class="small">
        {title}
        </div>

        <div class="big">
        {value}
        </div>

        </div>
        """,
        unsafe_allow_html=True
        )



st.markdown(
f"""
<div class="card">

<div class="small">
Development Category
</div>

<div class="big">
{category}
</div>

</div>

""",
unsafe_allow_html=True
)







# ================= CHARTS =================



st.markdown(
"<div class='title'>📈 Economic Performance</div>",
unsafe_allow_html=True
)



trend=ddi[
    ddi.District==district
]



g1,g2=st.columns(2)



with g1:


    fig=px.line(

        trend,

        x="Year",

        y="GDP",

        markers=True,

        title="GDP Trend (₹ Crore)"

    )


    fig.update_layout(
        height=380
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )





with g2:


    fig2=px.bar(

        trend,

        x="Year",

        y="GrowthRate",

        title="Growth Rate Trend (%)"

    )


    fig2.update_layout(
        height=380
    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )





# ================= INSIGHTS =================



st.markdown(
"<div class='title'>🧠 Automated Insights</div>",
unsafe_allow_html=True
)



old=trend.sort_values("Year").iloc[0]

new=trend.sort_values("Year").iloc[-1]



change=((new.GDP-old.GDP)/old.GDP)*100



st.info(
f"""

**{district}**

• GDP changed by **{change:.1f}%** during the available period.

• Current DDI score: **{selected.DDI:.3f}**

• State rank: **#{state_rank}**

• India rank: **#{india_rank}**

• Category: **{category}**

"""
)

# ================= GDP TABLES =================


st.markdown(
"<div class='title'>🏆 District GDP Comparison</div>",
unsafe_allow_html=True
)



top10 = (
    year_data
    .sort_values(
        "GDP",
        ascending=False
    )
    .head(10)
)



bottom10 = (
    year_data
    .sort_values(
        "GDP"
    )
    .head(10)
)



t1,t2=st.columns(2)



with t1:

    st.subheader("💰 Top 10 GDP Districts")


    st.dataframe(

        top10[
        [
        "District",
        "GDP",
        "GrowthRate",
        "DDI"
        ]
        ],

        hide_index=True,

        use_container_width=True

    )




with t2:


    st.subheader("📉 Lowest 10 GDP Districts")


    st.dataframe(

        bottom10[
        [
        "District",
        "GDP",
        "GrowthRate",
        "DDI"
        ]
        ],

        hide_index=True,

        use_container_width=True

    )






# ================= DEVELOPMENT MAP =================



st.markdown(
"<div class='title'>🗺️ India District Development Map</div>",
unsafe_allow_html=True
)



st.caption(
"Hover over districts to view DDI. Darker regions indicate higher development scores."
)



map_df = ddi[
    ddi.Year==year
].copy()



# cleaning district names

map_df["clean"] = (

    map_df.District

    .str.lower()

    .str.replace(
        " ",
        "",
        regex=False
    )

)





for feature in geojson["features"]:


    name = feature["properties"].get(
        "NAME_2",
        ""
    )


    feature["properties"]["clean"] = (

        name.lower()
        .replace(" ","")

    )






m = folium.Map(

    location=[22.5,80],

    zoom_start=4,

    tiles="CartoDB positron"

)





folium.Choropleth(

    geo_data=geojson,


    data=map_df,


    columns=[

        "clean",
        "DDI"

    ],


    key_on="feature.properties.clean",


    fill_opacity=0.85,


    line_opacity=0.3,


    legend_name=
    "District Development Index"

).add_to(m)






# highlight selected district


folium.GeoJson(

    geojson,

    style_function=lambda x:{

        "fillOpacity":0,

        "color":"orange"

    }

).add_to(m)







st_folium(

    m,

    width=1200,

    height=650

)





# ================= FOOTER =================



st.markdown(
"""
<div class="footer">

🇮🇳 India District Development Index

<br>

Built with Python • Pandas • Streamlit • Plotly • Folium

<br><br>

Economic insights from district-level data

</div>
""",

unsafe_allow_html=True
)