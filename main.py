import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="세계 나라별 MBTI 지도", layout="wide")

st.title("🌍 나라별 가장 많은 MBTI 지도")
st.write("업로드했던 MBTI 데이터를 내장해 자동으로 지도를 보여주는 버전입니다!")

# --- 1. CSV 자동 로드 ---
df = pd.read_csv("countriesMBTI_16types.csv")

# --- 2. 각 나라에서 가장 많은 MBTI 구하기 ---
mbti_cols = df.columns[1:]
df["TopMBTI"] = df[mbti_cols].idxmax(axis=1)

# --- 3. 국가별 위도/경도 DB (지연 없음, 100% 안정적) ---
country_coords = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv")
# 이 파일에는 Country Name + latitude + longitude 포함됨

merged = pd.merge(df, country_coords[["COUNTRY", "LAT", "LON"]],
                  left_on="Country", right_on="COUNTRY", how="left")

merged.rename(columns={"LAT": "lat", "LON": "lon"}, inplace=True)

# 좌표 없는 경우 0 처리
merged["lat"] = merged["lat"].fillna(0)
merged["lon"] = merged["lon"].fillna(0)

# --- 4. MBTI 색상 자동 생성 ---
unique_mbti = merged["TopMBTI"].unique()
color_map = {mbti: [int(hash(mbti) % 255), 120, 200] for mbti in unique_mbti}
merged["color"] = merged["TopMBTI"].apply(lambda x: color_map[x])

# --- 5. 지도 레이어 ---
layer = pdk.Layer(
    "ScatterplotLayer",
    merged,
    get_position='[lon, lat]',
    get_fill_color='color',
    get_radius=150000,
    pickable=True
)

view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1)

tooltip = {
    "html": "<b>국가:</b> {Country} <br/> <b>MBTI:</b> {TopMBTI}",
    "style": {"backgroundColor": "black", "color": "white"}
}

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip
)

st.pydeck_chart(deck)

st.subheader("📊 나라별 MBTI 데이터")
st.dataframe(merged[["Country", "TopMBTI"] + mbti_cols.tolist()])
