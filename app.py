import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ------------------------------------------------------------
# AGRIMITRA - Farmer Market Price Assistant
# Demonstration project. The included CSV contains SAMPLE data.
# Replace it with verified market records before real-world use.
# ------------------------------------------------------------

st.set_page_config(
    page_title="AgriMitra | Farmer Market Price Assistant",
    page_icon="🌾",
    layout="wide"
)

DATA_FILE = Path(__file__).parent / "market_prices.csv"
CATALOG_FILE = Path(__file__).parent / "crop_catalog.csv"

st.title("🌾 AgriMitra – Farmer Market Price Assistant")
st.caption("Agricultural market information • Price comparison • Historical trends • Selling-value estimate")

st.warning(
    "DEMO MODE: The bundled market_prices.csv contains illustrative SAMPLE prices, "
    "not current mandi rates. Verify prices with the market before making a sale."
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["Minimum Price", "Maximum Price", "Modal Price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

@st.cache_data
def load_catalog():
    return pd.read_csv(CATALOG_FILE)

try:
    df = load_data()
    catalog = load_catalog()
except Exception as exc:
    st.error(f"Could not load project CSV files: {exc}")
    st.stop()

# Optional upload lets the team test a verified dataset without editing Python.
with st.expander("📂 Use your own market-price CSV"):
    st.write(
        "Upload a CSV with these columns: State, District, Market, Commodity, "
        "Variety, Date, Minimum Price, Maximum Price, Modal Price, Unit, Source. "
        "The uploaded file is used for this session only."
    )
    uploaded = st.file_uploader("Upload market-price CSV", type=["csv"])
    if uploaded is not None:
        try:
            uploaded_df = pd.read_csv(uploaded)
            required = [
                "State", "District", "Market", "Commodity", "Date",
                "Minimum Price", "Maximum Price", "Modal Price", "Unit", "Source"
            ]
            missing = [c for c in required if c not in uploaded_df.columns]
            if missing:
                st.error("Missing columns: " + ", ".join(missing))
            else:
                df = uploaded_df.copy()
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                for col in ["Minimum Price", "Maximum Price", "Modal Price"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                if "Variety" not in df.columns:
                    df["Variety"] = "Not specified"
                if "Data Status" not in df.columns:
                    df["Data Status"] = "UPLOADED — verify source"
                st.success("Uploaded dataset loaded for this session.")
        except Exception as exc:
            st.error(f"Unable to read uploaded CSV: {exc}")

# Sidebar filters
st.sidebar.header("🔎 Find crop market prices")
all_crops = sorted(catalog["Commodity"].dropna().unique().tolist())
crop = st.sidebar.selectbox("Select crop / vegetable", all_crops)

crop_rows = df[df["Commodity"].astype(str).str.casefold() == crop.casefold()]
state_options = sorted(crop_rows["State"].dropna().astype(str).unique().tolist())
if not state_options:
    st.info(f"No market records are currently available for {crop}. Upload a verified CSV containing this commodity.")
    st.stop()

state = st.sidebar.selectbox("Select state", state_options)
state_rows = crop_rows[crop_rows["State"] == state]
district_options = sorted(state_rows["District"].dropna().astype(str).unique().tolist())
district = st.sidebar.selectbox("Select district", district_options)
district_rows = state_rows[state_rows["District"] == district]
market_options = sorted(district_rows["Market"].dropna().astype(str).unique().tolist())
market = st.sidebar.selectbox("Select market", market_options)

filtered = district_rows[district_rows["Market"] == market].copy()
filtered = filtered.dropna(subset=["Date", "Minimum Price", "Maximum Price", "Modal Price"])
if filtered.empty:
    st.warning("No complete price records found for the selected filters.")
    st.stop()

latest_date = filtered["Date"].max()
latest = filtered[filtered["Date"] == latest_date].sort_values("Modal Price", ascending=False)
record = latest.iloc[0]
unit = str(record.get("Unit", "unit not specified"))

st.subheader("📍 Selected market")
st.write(f"**Crop:** {crop}  |  **State:** {state}  |  **District:** {district}  |  **Market:** {market}")
st.caption(f"Latest reporting date in this dataset: {latest_date.strftime('%d %b %Y')}")

c1, c2, c3 = st.columns(3)
c1.metric("Minimum price", f"₹{record['Minimum Price']:,.2f}", help=unit)
c2.metric("Maximum price", f"₹{record['Maximum Price']:,.2f}", help=unit)
c3.metric("Modal price", f"₹{record['Modal Price']:,.2f}", help=unit)
st.caption(f"Price unit: {unit} • Source: {record.get('Source', 'Not provided')}")

if "Data Status" in record.index:
    st.info(f"Data status: {record['Data Status']}")

st.divider()
st.subheader("📊 Compare prices across available markets")
compare = crop_rows.copy()
compare["Date"] = pd.to_datetime(compare["Date"], errors="coerce")
compare = compare.dropna(subset=["Date", "Modal Price"])
if not compare.empty:
    compare_date = st.selectbox(
        "Choose reporting date for comparison",
        sorted(compare["Date"].dropna().unique(), reverse=True),
        format_func=lambda x: pd.Timestamp(x).strftime("%d %b %Y")
    )
    comparison = compare[compare["Date"] == pd.Timestamp(compare_date)]
    if not comparison.empty:
        fig = px.bar(
            comparison, x="Market", y="Modal Price", color="State",
            hover_data=["District", "Minimum Price", "Maximum Price", "Unit", "Source"],
            title=f"{crop}: modal price comparison ({pd.Timestamp(compare_date).date()})"
        )
        fig.update_layout(xaxis_title="Market", yaxis_title="Modal price (₹ as reported)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            comparison[["State", "District", "Market", "Date", "Minimum Price",
                        "Maximum Price", "Modal Price", "Unit", "Source"]],
            use_container_width=True, hide_index=True
        )

st.divider()
st.subheader("📈 Historical price trend")
trend = filtered.sort_values("Date")
if len(trend) > 1:
    fig_line = px.line(
        trend, x="Date", y=["Minimum Price", "Maximum Price", "Modal Price"],
        markers=True, title=f"{crop} price history — {market}"
    )
    fig_line.update_layout(xaxis_title="Reporting date", yaxis_title="Price (₹ as reported)")
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("More dated records are needed to show a historical trend.")

st.divider()
st.subheader("🧮 Selling-value calculator")
st.write("Enter your quantity and expenses. The result is an estimate based on the selected modal price.")
col_a, col_b, col_c = st.columns(3)
with col_a:
    quantity = st.number_input("Quantity (in the dataset's price unit)", min_value=0.0, value=1.0, step=1.0)
with col_b:
    transport = st.number_input("Transport expenses (₹)", min_value=0.0, value=0.0, step=50.0)
with col_c:
    other = st.number_input("Other expenses (₹)", min_value=0.0, value=0.0, step=50.0)

gross = quantity * float(record["Modal Price"])
net = gross - transport - other
m1, m2 = st.columns(2)
m1.metric("Estimated gross value", f"₹{gross:,.2f}")
m2.metric("Estimated value after entered expenses", f"₹{net:,.2f}")
st.caption(
    "This is an illustrative calculation, not a guaranteed return. It excludes any costs "
    "you have not entered and may not reflect quality deductions, commissions, taxes or local fees."
)

st.divider()
with st.expander("🌱 Crop and vegetable catalogue included in AgriMitra"):
    st.dataframe(catalog, use_container_width=True, hide_index=True)
    st.caption(f"{catalog['Commodity'].nunique()} commonly cultivated crop/commodity names are included. "
               "This is a broad student-project catalogue, not an exhaustive list of every Indian variety.")

st.subheader("ℹ️ Responsible use")
st.write(
    "Market prices can change by date, market, variety, quality and quantity. Always check the "
    "reporting date, unit and source, and confirm the current rate with the relevant market "
    "before making a transaction. AgriMitra is an information aid and does not guarantee profit."
)
