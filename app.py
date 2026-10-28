import streamlit as st
import pandas as pd
import plotly.express as px

# ========================================
# REAL ESTATE BUYER INTELLIGENCE
# ========================================
st.set_page_config(
    page_title=" Real Estate Buyer Intelligence",
    page_icon="🏢",
    layout="wide"
)

# -------------------- DESIGN --------------------
st.markdown("""
<style>
.stApp { background-color: #FAF7F8; color: #39323B; }
[data-testid="stSidebar"] { background-color: #F0E8F0; }
[data-testid="stMetric"] {
    background-color: #FFFFFF; border: 1px solid #E8DCE5;
    border-radius: 14px; padding: 15px 16px;
}
h1, h2, h3 { color: #493849; }
div[data-testid="stPlotlyChart"] {
    background-color: #FFFFFF; border: 1px solid #EEE3E9;
    border-radius: 14px; padding: 8px;
}
</style>
""", unsafe_allow_html=True)

PINK = "#D9A3B5"
LAVENDER = "#B9AEDB"
PEACH = "#EBC6A8"
GREEN = "#A9C9B6"
BLUE = "#AFC9E8"
PALETTE = [PINK, LAVENDER, PEACH, GREEN, BLUE]

# These are the segment names agreed for the four trained cluster IDs.
CLUSTER_NAMES = {
    0: "Emerging Investors",
    1: "Low-Satisfaction Buyers",
    2: "Established Buyers",
    3: "Emerging Buyers",
}

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_data():
    properties = pd.read_csv("buyer_property.csv")
    clustered = pd.read_csv("property_cluster.csv")

    # Bring the existing K-Means cluster labels into the full property data.
    cluster_info = clustered[["listing_id", "Cluster"]].drop_duplicates("listing_id")
    data = properties.merge(cluster_info, on="listing_id", how="left")

    for column in ["sale_price", "floor_area_sqft", "satisfaction_score", "Cluster"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    if "transaction_date" in data.columns:
        data["transaction_date"] = pd.to_datetime(data["transaction_date"], errors="coerce")

    # Translate numeric cluster IDs into the agreed human-readable segment names.
    data["Segment"] = data["Cluster"].map(CLUSTER_NAMES)
    return data

try:
    data = load_data()
except FileNotFoundError:
    st.error(
        "CSV file not found. Keep buyer_property.csv and property_cluster.csv "
        "in the same folder as this Python file."
    )
    st.stop()
except Exception as error:
    st.error(f"The data files could not be loaded: {error}")
    st.stop()

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.title("Dashboard Filters")
st.sidebar.caption("Select filters to update the dashboard.")

country_options = ["All countries"] + sorted(data["country"].dropna().astype(str).unique().tolist())
selected_country = st.sidebar.selectbox("Country", country_options)

if selected_country == "All countries":
    country_data = data.copy()
else:
    country_data = data[data["country"].astype(str) == selected_country].copy()

region_options = ["All regions"] + sorted(country_data["region"].dropna().astype(str).unique().tolist())
selected_region = st.sidebar.selectbox("Region", region_options)

status_options = ["All statuses"] + sorted(data["listing_status"].dropna().astype(str).unique().tolist())
selected_status = st.sidebar.selectbox("Property status", status_options)

type_options = ["All property types"] + sorted(data["unit_category"].dropna().astype(str).unique().tolist())
selected_type = st.sidebar.selectbox("Property type", type_options)

client_options = ["All client types"] + sorted(data["client_type"].dropna().astype(str).unique().tolist())
selected_client = st.sidebar.selectbox("Client type", client_options)

purpose_options = ["All purposes"] + sorted(data["acquisition_purpose"].dropna().astype(str).unique().tolist())
selected_purpose = st.sidebar.selectbox("Acquisition purpose", purpose_options)

filtered = country_data.copy()
if selected_region != "All regions":
    filtered = filtered[filtered["region"].astype(str) == selected_region]
if selected_status != "All statuses":
    filtered = filtered[filtered["listing_status"].astype(str) == selected_status]
if selected_type != "All property types":
    filtered = filtered[filtered["unit_category"].astype(str) == selected_type]
if selected_client != "All client types":
    filtered = filtered[filtered["client_type"].astype(str) == selected_client]
if selected_purpose != "All purposes":
    filtered = filtered[filtered["acquisition_purpose"].astype(str) == selected_purpose]

if filtered.empty:
    st.title("Real Estate Buyer Intelligence")
    st.warning("No property records match these filters. Change one or more filters.")
    st.stop()

# Buyer-behaviour attributes and K-Means labels are available for sold records only.
sold_view = filtered[filtered["listing_status"].astype(str).str.casefold() == "sold"].copy()
clustered_view = sold_view[sold_view["Cluster"].notna()].copy()

# -------------------- HEADER --------------------
st.title("🏢 Real Estate Buyer Intelligence")
st.caption("PROPERTY MARKET  |  BUYER SEGMENTATION  |  INVESTOR BEHAVIOUR  |  GEOGRAPHY")
st.markdown("Explore property status, buyer segments, investment behaviour and geographic patterns.")

# -------------------- KPI CARDS --------------------
total_properties = len(filtered)
sold_properties = (filtered["listing_status"] == "Sold").sum()
available_properties = (filtered["listing_status"] == "Available").sum()
country_count = filtered["country"].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Property Records", f"{total_properties:,}")
k2.metric("Sold Properties", f"{sold_properties:,}")
k3.metric("Available Properties", f"{available_properties:,}")
k4.metric("Countries in View", f"{country_count:,}")
st.caption("The full dataset has 10,000 property records: 7,305 sold and 2,695 available. Filters change these figures.")

# ============================================================
# MODULE 1 — MARKET OVERVIEW
# ============================================================
st.divider()
st.subheader("01  Market Overview")
st.caption("A high-level view of property status, property types and sold-property values.")
left, right = st.columns(2)

with left:
    status_counts = filtered["listing_status"].value_counts().rename_axis("Status").reset_index(name="Properties")
    fig = px.pie(
        status_counts, names="Status", values="Properties", hole=0.60,
        color="Status", color_discrete_map={"Sold": PINK, "Available": LAVENDER},
        title="Sold vs Available"
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(t=55, b=15, l=15, r=15), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

with right:
    type_counts = filtered["unit_category"].value_counts().rename_axis("Property Type").reset_index(name="Properties")
    fig = px.bar(
        type_counts, x="Property Type", y="Properties", color="Property Type",
        text="Properties", color_discrete_sequence=PALETTE, title="Properties by Type"
    )
    fig.update_layout(showlegend=False, xaxis_title="Property type", yaxis_title="Property records",
                      margin=dict(t=55, b=15, l=15, r=15))
    st.plotly_chart(fig, use_container_width=True)

# This value chart uses sold properties only, because available records do not have sale prices.
price_by_type = sold_view.dropna(subset=["unit_category", "sale_price"]).groupby("unit_category", as_index=False)["sale_price"].mean()
if not price_by_type.empty:
    price_by_type = price_by_type.rename(columns={"unit_category": "Property Type", "sale_price": "Average Sale Price"})
    fig = px.bar(
        price_by_type, x="Property Type", y="Average Sale Price", color="Property Type",
        text_auto=".2s", color_discrete_sequence=PALETTE,
        title="Average Sale Price by Property Type (Sold Properties)"
    )
    fig.update_layout(showlegend=False, xaxis_title="Property type", yaxis_title="Average sale price",
                      margin=dict(t=55, b=15, l=15, r=15))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No sold-property price records match the current filters.")

# ============================================================
# MODULE 2 — BUYER SEGMENTATION
# ============================================================
st.divider()
st.subheader("02  Buyer Segmentation Overview")
st.caption("These names describe the K-Means cluster IDs already stored in property_cluster.csv.")

if clustered_view.empty:
    st.info("No clustered sold properties match the current filters.")
else:
    segment_order = [CLUSTER_NAMES[i] for i in sorted(CLUSTER_NAMES)]
    cluster_counts = clustered_view["Segment"].value_counts().reindex(segment_order, fill_value=0)
    cluster_counts = cluster_counts[cluster_counts > 0].rename_axis("Buyer Segment").reset_index(name="Sold Property Records")
    left, right = st.columns(2)

    with left:
        fig = px.bar(
            cluster_counts, x="Buyer Segment", y="Sold Property Records", color="Buyer Segment",
            text="Sold Property Records", color_discrete_sequence=PALETTE,
            title="Sold Records by Buyer Segment"
        )
        fig.update_layout(showlegend=False, xaxis_title="Buyer segment", yaxis_title="Sold property records",
                          margin=dict(t=55, b=15, l=15, r=15))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.pie(
            cluster_counts, names="Buyer Segment", values="Sold Property Records", hole=0.60,
            color="Buyer Segment", color_discrete_sequence=PALETTE, title="Buyer Segment Share"
        )
        fig.update_traces(textposition="inside", textinfo="percent")
        fig.update_layout(margin=dict(t=55, b=15, l=15, r=15), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)

    segment_summary = clustered_view.groupby("Segment").agg(
        Sold_Records=("listing_id", "count"),
        Average_Sale_Price=("sale_price", "mean"),
        Average_Floor_Area_Sq_Ft=("floor_area_sqft", "mean"),
        Average_Satisfaction=("satisfaction_score", "mean")
    ).reset_index().rename(columns={
        "Segment": "Buyer Segment",
        "Sold_Records": "Sold property records",
        "Average_Sale_Price": "Average sale price",
        "Average_Floor_Area_Sq_Ft": "Average floor area (sq ft)",
        "Average_Satisfaction": "Average satisfaction"
    })
    st.markdown("**Buyer segment profile**")
    st.dataframe(segment_summary.round(2), use_container_width=True, hide_index=True)

# ============================================================
# MODULE 3 — INVESTOR BEHAVIOUR
# ============================================================
st.divider()
st.subheader("03  Investor Behaviour")
st.caption("Buyer behaviour charts use sold records only, because the 2,695 available listings do not have buyer-behaviour values.")

price_col, area_col, satisfaction_col = st.columns(3)
average_price = sold_view["sale_price"].mean()
average_area = sold_view["floor_area_sqft"].mean()
average_satisfaction = sold_view["satisfaction_score"].mean()
price_col.metric("Average Sale Price (Sold)", f"${average_price:,.0f}" if pd.notna(average_price) else "N/A")
area_col.metric("Average Floor Area (Sold)", f"{average_area:,.0f} sq ft" if pd.notna(average_area) else "N/A")
satisfaction_col.metric("Average Satisfaction (Sold)", f"{average_satisfaction:.2f} / 5" if pd.notna(average_satisfaction) else "N/A")


if sold_view.empty:
    st.info("No sold records match the current filters, so buyer-behaviour charts cannot be displayed.")
else:

    # Acquisition purpose: Home and Investment, with counts from sold records only.
    purpose_data = sold_view.dropna(subset=["acquisition_purpose"])
    purpose_counts = purpose_data["acquisition_purpose"].value_counts().rename_axis("Acquisition Purpose").reset_index(name="Sold Property Records")
    left, right = st.columns(2)

    with left:
        fig = px.bar(
            purpose_counts, x="Acquisition Purpose", y="Sold Property Records",
            color="Acquisition Purpose", text="Sold Property Records",
            color_discrete_sequence=PALETTE, title="Acquisition Purpose (Sold Properties)"
        )
        fig.update_layout(showlegend=False, xaxis_title="Purpose", yaxis_title="Sold property records",
                          margin=dict(t=55, b=15, l=15, r=15))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Records with acquisition purpose recorded: {len(purpose_data):,}.")

    # Loan application: only Yes/No values, no artificial 'Not recorded' category.
    with right:
        loan_data = sold_view.dropna(subset=["loan_applied"])
        loan_counts = loan_data["loan_applied"].value_counts().rename_axis("Loan Applied").reset_index(name="Sold Property Records")
        fig = px.pie(
            loan_counts, names="Loan Applied", values="Sold Property Records", hole=0.58,
            color_discrete_sequence=[LAVENDER, PINK], title="Loan Application (Sold Properties)"
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(margin=dict(t=55, b=15, l=15, r=15), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Records with loan information recorded: {len(loan_data):,}.")

    left, right = st.columns(2)
    with left:
        client_data = sold_view.dropna(subset=["client_type"])
        client_counts = client_data["client_type"].value_counts().rename_axis("Client Type").reset_index(name="Sold Property Records")
        fig = px.bar(
            client_counts, x="Client Type", y="Sold Property Records", color="Client Type",
            text="Sold Property Records", color_discrete_sequence=PALETTE,
            title="Client Type (Sold Properties)"
        )
        fig.update_layout(showlegend=False, xaxis_title="Client type", yaxis_title="Sold property records",
                          margin=dict(t=55, b=15, l=15, r=15))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Records with client type recorded: {len(client_data):,}.")

    with right:
        referral_data = sold_view.dropna(subset=["referral_channel"])
        referral_counts = referral_data["referral_channel"].value_counts().rename_axis("Referral Channel").reset_index(name="Sold Property Records")
        fig = px.bar(
            referral_counts, x="Referral Channel", y="Sold Property Records", color="Referral Channel",
            text="Sold Property Records", color_discrete_sequence=PALETTE,
            title="Referral Channel (Sold Properties)"
        )
        fig.update_layout(showlegend=False, xaxis_title="Referral channel", yaxis_title="Sold property records",
                          margin=dict(t=55, b=15, l=15, r=15))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Records with referral channel recorded: {len(referral_data):,}.")

    # Show investment behaviour across the named clusters, not just overall totals.
    if not clustered_view.empty:
        st.markdown("**Acquisition purpose by buyer segment**")
        segment_purpose_data = clustered_view.dropna(subset=["acquisition_purpose", "Segment"])
        if not segment_purpose_data.empty:
            segment_purpose_counts = (
                segment_purpose_data.groupby(["Segment", "acquisition_purpose"]).size()
                .reset_index(name="Sold Property Records")
                .rename(columns={"Segment": "Buyer Segment", "acquisition_purpose": "Acquisition Purpose"})
            )
            fig = px.bar(
                segment_purpose_counts, x="Buyer Segment", y="Sold Property Records",
                color="Acquisition Purpose", barmode="group", text="Sold Property Records",
                color_discrete_sequence=[PINK, LAVENDER], title="Home vs Investment by Buyer Segment"
            )
            fig.update_layout(xaxis_title="Buyer segment", yaxis_title="Sold property records",
                              margin=dict(t=55, b=15, l=15, r=15))
            st.plotly_chart(fig, use_container_width=True)

   
# ============================================================
# MODULE 4 — GEOGRAPHIC ANALYSIS
# ============================================================
st.divider()
st.subheader("04  Geographic Buyer Analysis")
st.caption("The map shows property-record distribution by country; the region chart updates with the filters.")
left, right = st.columns([1.15, 1])

with left:
    country_counts = filtered.dropna(subset=["country"]).groupby("country").size().reset_index(name="Property Records")
    if country_counts.empty:
        st.info("No geographic records match the selected filters.")
    else:
        fig = px.choropleth(
            country_counts, locations="country", locationmode="country names",
            color="Property Records", hover_name="country",
            color_continuous_scale=["#F5EAF0", PINK, "#92749C"],
            title="Property Distribution by Country"
        )
        fig.update_layout(margin=dict(t=55, b=10, l=0, r=0),
                          geo=dict(showframe=False, showcoastlines=True, bgcolor="#FAF7F8"),
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

with right:
    region_counts = (
        filtered.dropna(subset=["region"]).groupby("region").size()
        .sort_values(ascending=False).head(10).reset_index(name="Property Records")
    )
    if region_counts.empty:
        st.info("No regions match the selected filters.")
    else:
        fig = px.bar(
            region_counts.sort_values("Property Records"), x="Property Records", y="region",
            orientation="h", text="Property Records", color="Property Records",
            color_continuous_scale=["#F5EAF0", PINK, "#92749C"], title="Top  Regions"
        )
        fig.update_layout(margin=dict(t=55, b=10, l=10, r=10), coloraxis_showscale=False,
                          xaxis_title="Property records", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
