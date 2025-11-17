import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim

st.set_page_config(page_title="세계 나라별 MBTI 지도", layout="wide")

st.title("🌍 나라별 가장 많은 MBTI 지도")
st.write("업로드된 MBTI 데이터로 세계 지도를 보여주는 앱입니다!")

# 파일 업로드
uploaded_file = st.file_uploader("📂 countriesMBTI_16types.csv 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # 1) 각 나라별 최댓값 MBTI 찾기
    mbti_cols = df.columns[1:]
    df["TopMBTI"] = df[mbti_cols].idxmax(axis=1)

    # 2) 나라별 위도/경도 가져오기
    geolocator = Nominatim(user_agent="mbti_map_app")
    lat_list, lon_list = [], []

    for country in df["Country"]:
        try:
            loc = geolocator.geocode(country)
            lat_list.append(loc.latitude)
            lon_list.append(loc.longitude)
        except:
            lat_list.append(0)
            lon_list.append(0)

    df["lat"] = lat_list
    df["lon"] = lon_list

    # MBTI 색 만들기
    unique_mbti = df["TopMBTI"].unique()
    color_map = {mbti: [int(hash(mbti) % 255), 100, 180] for mbti in unique_mbti}
    df["color"] = df["TopMBTI"].apply(lambda x: color_map[x])

    # 지도
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position='[lon, lat]',
        get_radius=200000,
        get_fill_color="color",
        pickable=True
    )

    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2)

    tooltip = {
        "html": "<b>국가:</b> {Country} <br/><b>Top MBTI:</b> {TopMBTI}",
        "style": {"backgroundColor": "gray", "color": "white"}
    }

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )

    st.pydeck_chart(deck)

    st.subheader("📊 데이터 미리보기")
    st.dataframe(df)
else:
    st.info("CSV 파일을 업로드하세요.")
