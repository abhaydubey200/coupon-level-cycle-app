import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Coupon Level & Cycle Distribution",
    page_icon="",
    layout="wide"
)

# ==================================================
# HEADER
# ==================================================
st.title(" Coupon Level & Cycle Distribution System")
st.markdown(
    "Upload a CSV or Excel file and automatically assign **Cycle** and **Level** "
    "based on coupon card logic."
)

# ==================================================
# BUSINESS LOGIC
# ==================================================
def calculate_cycle(coupon: int):
    """
    Cycle logic:
    - Coupons < 41 → NA
    - Every 41 coupons form a new cycle
    """
    if coupon < 41:
        return "NA"
    return ((coupon - 1) // 41) + 1


def calculate_level(coupon: int):
    """
    Level logic (repeats in every cycle):
    1–5   → 0
    6–11  → 1
    12–17 → 2
    18–23 → 3
    24–29 → 4
    30–39 → 5
    40    → 6
    """
    position = coupon % 41
    if position == 0:
        position = 41

    if position <= 5:
        return 0
    elif position <= 11:
        return 1
    elif position <= 17:
        return 2
    elif position <= 23:
        return 3
    elif position <= 29:
        return 4
    elif position <= 39:
        return 5
    else:
        return 6

# ==================================================
# FILE UPLOAD
# ==================================================
uploaded_file = st.file_uploader(
    " Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.info("Upload a file to continue.")
    st.stop()

# ==================================================
# READ FILE
# ==================================================
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

# ==================================================
# VALIDATE DATA
# ==================================================
REQUIRED_COLUMNS = {
    "user_id",
    "username",
    "phone_number",
    "coupon_cards"
}

if not REQUIRED_COLUMNS.issubset(df.columns):
    st.error(
        f"Dataset must contain these columns:\n{', '.join(REQUIRED_COLUMNS)}"
    )
    st.stop()

df = df.copy()

# ==================================================
# RAW DATA PREVIEW
# ==================================================
with st.expander(" Preview Raw Data"):
    st.dataframe(df.head(100))

# ==================================================
# FILTER SECTION
# ==================================================
st.subheader(" Filter Coupon Cards")

min_coupon = int(df["coupon_cards"].min())
max_coupon = int(df["coupon_cards"].max())

coupon_range = st.slider(
    "Select coupon card range",
    min_value=min_coupon,
    max_value=max_coupon,
    value=(min_coupon, max_coupon)
)

filtered_df = df[
    (df["coupon_cards"] >= coupon_range[0]) &
    (df["coupon_cards"] <= coupon_range[1])
].copy()

# ==================================================
# APPLY LOGIC
# ==================================================
filtered_df["Cycle"] = filtered_df["coupon_cards"].apply(calculate_cycle)
filtered_df["Level"] = filtered_df["coupon_cards"].apply(calculate_level)

# ==================================================
# KPI METRICS
# ==================================================
st.subheader(" Summary Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Users", len(filtered_df))
col2.metric("Min Coupons", filtered_df["coupon_cards"].min())
col3.metric("Max Coupons", filtered_df["coupon_cards"].max())
col4.metric("Max Level", filtered_df["Level"].max())

# ==================================================
# RESULT TABLE
# ==================================================
st.subheader(" Final Output")

st.dataframe(filtered_df, use_container_width=True)

# ==================================================
# DOWNLOAD
# ==================================================
st.subheader(" Download Result")

output_csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download CSV",
    data=output_csv,
    file_name="coupon_level_cycle_output.csv",
    mime="text/csv"
)

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.caption("Production-ready Streamlit app for Coupon / Loyalty Systems")
