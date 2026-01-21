import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Coupon Cycle & Level Calculator",
    layout="wide"
)

st.title(" Coupon Cycle & Level Calculator")
st.write("Upload CSV to calculate **Cycle**, **Level**, and **Cycle_Level**")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

def calculate_cycle(coupon_cards):
    return int((coupon_cards - 1) / 40) + 1


def calculate_level(coupon_cards):
    pos = ((coupon_cards - 1) % 40) + 1

    if pos <= 5:
        return 0
    elif pos <= 11:
        return 1
    elif pos <= 17:
        return 2
    elif pos <= 23:
        return 3
    elif pos <= 29:
        return 4
    elif pos <= 39:
        return 5
    else:
        return 6


if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    required_columns = {
        "username",
        "phone_number",
        "coupon_cards"
    }

    if not required_columns.issubset(df.columns):
        st.error(f"CSV must contain columns: {', '.join(required_columns)}")
        st.stop()

    df = df[(df["coupon_cards"] >= 1) & (df["coupon_cards"] <= 1400)]

    df["cycle"] = df["coupon_cards"].apply(calculate_cycle)
    df["level"] = df["coupon_cards"].apply(calculate_level)
    df["cycle_level"] = df["cycle"].astype(str) + "-" + df["level"].astype(str)

    st.subheader(" Filters")

    min_card, max_card = st.slider(
        "Filter by Coupon Cards",
        min_value=1,
        max_value=1400,
        value=(1, 1400)
    )

    df = df[
        (df["coupon_cards"] >= min_card) &
        (df["coupon_cards"] <= max_card)
    ]

    st.subheader(" User Search")

    search_text = st.text_input(
        "Search by Username or Phone Number"
    )

    if search_text:
        df = df[
            df["username"].str.contains(search_text, case=False, na=False) |
            df["phone_number"].astype(str).str.contains(search_text, na=False)
        ]

    st.subheader(" Analytics")


    cycle_df = (
        df.groupby("cycle")["username"]
        .agg(
            user_count="nunique",
            users=lambda x: ", ".join(sorted(x.unique()))
        )
        .reset_index()
    )

    cycle_chart = alt.Chart(cycle_df).mark_bar().encode(
        x=alt.X("cycle:O", title="Cycle"),
        y=alt.Y("user_count:Q", title="Users"),
        tooltip=[
            alt.Tooltip("cycle:O", title="Cycle"),
            alt.Tooltip("user_count:Q", title="Total Users"),
            alt.Tooltip("users:N", title="Usernames")
        ]
    ).properties(height=350)

    st.altair_chart(cycle_chart, use_container_width=True)


    level_df = (
        df.groupby("level")["username"]
        .agg(
            user_count="nunique",
            users=lambda x: ", ".join(sorted(x.unique()))
        )
        .reset_index()
    )

    level_chart = alt.Chart(level_df).mark_bar().encode(
        x=alt.X("level:O", title="Level"),
        y=alt.Y("user_count:Q", title="Users"),
        tooltip=[
            alt.Tooltip("level:O", title="Level"),
            alt.Tooltip("user_count:Q", title="Total Users"),
            alt.Tooltip("users:N", title="Usernames")
        ]
    ).properties(height=350)

    st.altair_chart(level_chart, use_container_width=True)

    cl_df = (
        df.groupby("cycle_level")["username"]
        .agg(
            user_count="nunique",
            users=lambda x: ", ".join(sorted(x.unique()))
        )
        .reset_index()
    )

    cl_chart = alt.Chart(cl_df).mark_bar().encode(
        x=alt.X("cycle_level:O", title="Cycle-Level", sort=None),
        y=alt.Y("user_count:Q", title="Users"),
        tooltip=[
            alt.Tooltip("cycle_level:O", title="Cycle-Level"),
            alt.Tooltip("user_count:Q", title="Total Users"),
            alt.Tooltip("users:N", title="Usernames")
        ]
    ).properties(height=400)

    st.altair_chart(cl_chart, use_container_width=True)

    st.subheader(" Final Output")

    show_table = st.checkbox("Show / Hide Table", value=True)

    if show_table:
        st.dataframe(
            df[
                [
                    "username",
                    "phone_number",
                    "coupon_cards",
                    "cycle",
                    "level",
                    "cycle_level"
                ]
            ],
            use_container_width=True
        )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        " Download Result CSV",
        csv,
        "cycle_level_output.csv",
        "text/csv"
    )

else:
    st.info("Upload a CSV file to begin")
