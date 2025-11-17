import streamlit as st
import pandas as pd
import pydeck as pdk
import pycountry
from geopy.geocoders import Nominatim

st.set_page_config(page_title="세계 나라별 MBTI 지도", layout="wide")

st.title("🌍 나라별 가장 많은 MBTI 지도")
st.write("업로드된 실제 MBTI 데이터 기반으로 만들어진 지도입니다!")

# CSV 파일 읽기
df = pd.read_csv("countriesMBTI_16types.csv")

# 1) 각 나라별 최댓값 MBTI 찾기
mbti_cols = df.columns[1:]
df["TopMBTI"] = df[mbti_cols].idxmax(axis=1)

# 2) 나라별 위도/경도 자동 가져오기
geolocator = Nominatim(user_agent="mbti_map_app")
lat_list = []
lon_list = []

for country in df["Country"]:
    try:
        location = geolocator.geocode(country)
        lat_list.append(location.latitude)
        lon_list.append(location.longitude)
    except:
        # 좌표 못 찾을 경우 기본값 (0,0)
        lat_list.append(0)
        lon_list.append(0)

df["lat"] = lat_list
df["lon"] = lon_list

# 3) MBTI별 색 자동 생성
unique_mbti = df["TopMBTI"].unique()
color_map = {mbti: [int(hash(mbti) % 255), 100, 180] for mbti in unique_mbti}
df["color"] = df["TopMBTI"].apply(lambda x: color_map[x])

# 4) 지도 표시
layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position='[lon, lat]',
    auto_highlight=True,
    get_radius=200000,
    get_fill_color='color',
    pickable=True
)

view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1)

tool_tip = {
    "html": "<b>Country:</b> {Country} <br/> <b>Top MBTI:</b> {TopMBTI}",
    "style": {"backgroundColor": "gray", "color": "white"}
}

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tool_tip
)

st.pydeck_chart(deck)

# 데이터 보이기
st.subheader("📊 나라별 MBTI 데이터")
st.dataframe(df)
