import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Coupon Cycle & Level Calculator",
    page_icon=" ",
    layout="wide"
)

st.title(" Coupon Cycle & Level Calculator")
st.write("Upload your dataset to calculate **Cycle** and **Level** based on coupon cards.")

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

def calculate_cycle(coupon_cards):
    if coupon_cards <= 40:
        return "N/A"
    return int((coupon_cards - 1) / 40) + 1


def calculate_level(coupon_cards):
    if coupon_cards <= 40:
        return int((coupon_cards - 1) / 6)
    return int(((coupon_cards - 1) % 40) / 6)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = {
            "user_id",
            "username",
            "phone_number",
            "coupon_cards"
        }

        if not required_columns.issubset(df.columns):
            st.error(
                f"CSV must contain columns: {', '.join(required_columns)}"
            )
        else:
            df = df[
                (df["coupon_cards"] >= 1) &
                (df["coupon_cards"] <= 1400)
            ]

            df["cycle"] = df["coupon_cards"].apply(calculate_cycle)
            df["level"] = df["coupon_cards"].apply(calculate_level)

            min_card, max_card = st.slider(
                "Filter by Coupon Cards",
                min_value=1,
                max_value=1400,
                value=(1, 1400)
            )

            filtered_df = df[
                (df["coupon_cards"] >= min_card) &
                (df["coupon_cards"] <= max_card)
            ]

            st.subheader("Final Output")

            st.dataframe(
                filtered_df[
                    [
                        "username",
                        "phone_number",
                        "coupon_cards",
                        "cycle",
                        "level"
                    ]
                ],
                use_container_width=True
            )

            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=" Download Result CSV",
                data=csv,
                file_name="cycle_level_output.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("👆 Upload a CSV file to get started.")
