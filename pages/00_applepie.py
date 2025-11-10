import streamlit as st
import pandas as pd
import random

# -------------------------------
# 기본 메뉴 데이터
# -------------------------------
BASE_MENUS = [
    {
        "name": "김치찌개",
        "cuisine": "한식",
        "diet": "일반식",
        "time_min": 25,
        "cost_tier": "저렴",
        "ingredients": ["김치", "돼지고기", "두부"],
        "recipe": "1. 냄비에 돼지고기를 볶다가 김치를 넣고 함께 볶습니다.\n"
                  "2. 물을 붓고 끓입니다.\n"
                  "3. 두부를 넣고 5분 정도 더 끓이면 완성!",
    },
    {
        "name": "된장찌개",
        "cuisine": "한식",
        "diet": "일반식",
        "time_min": 20,
        "cost_tier": "저렴",
        "ingredients": ["된장", "애호박", "두부"],
        "recipe": "1. 냄비에 물을 끓이고 된장을 풉니다.\n"
                  "2. 애호박과 두부를 넣고 10분간 끓입니다.\n"
                  "3. 마지막에 고추와 마늘을 넣고 간 맞추면 완성!",
    },
    {
        "name": "파스타",
        "cuisine": "양식",
        "diet": "일반식",
        "time_min": 30,
        "cost_tier": "중간",
        "ingredients": ["스파게티면", "토마토소스"],
        "recipe": "1. 면을 삶습니다.\n"
                  "2. 팬에 토마토소스를 끓이고 면을 넣어 섞습니다.\n"
                  "3. 올리브유와 후추를 넣고 완성!",
    },
    {
        "name": "샐러드",
        "cuisine": "다이어트식",
        "diet": "채식",
        "time_min": 10,
        "cost_tier": "저렴",
        "ingredients": ["채소", "드레싱"],
        "recipe": "1. 채소를 깨끗이 씻고 물기를 제거합니다.\n"
                  "2. 원하는 드레싱을 넣어 가볍게 버무립니다.",
    },
]

# -------------------------------
# 세션 데이터 초기화
# -------------------------------
if "DF" not in st.session_state:
    st.session_state["DF"] = pd.DataFrame(BASE_MENUS)

DF = st.session_state["DF"]

# -------------------------------
# UI 시작
# -------------------------------
st.title("🍽 오늘 저녁 뭐 먹지?")
st.caption("Streamlit으로 만든 저녁 메뉴 & 레시피 추천 사이트")

# --- 필터 섹션 ---
st.sidebar.header("🔍 필터 옵션")
cuisine = st.sidebar.selectbox("요리 종류", ["전체", "한식", "양식", "중식", "일식", "다이어트식"])
max_time = st.sidebar.slider("최대 조리 시간 (분)", 5, 60, 30)
cost = st.sidebar.selectbox("비용대", ["전체", "저렴", "중간", "비쌈"])

# --- 필터 적용 ---
filtered = DF.copy()
if cuisine != "전체":
    filtered = filtered[filtered["cuisine"] == cuisine]
filtered = filtered[filtered["time_min"] <= max_time]
if cost != "전체":
    filtered = filtered[filtered["cost_tier"] == cost]

# -------------------------------
# 메뉴 추천 리스트
# -------------------------------
st.subheader("🍱 추천 메뉴")
if filtered.empty:
    st.info("조건에 맞는 메뉴가 없습니다. 필터를 조정해보세요.")
else:
    for _, row in filtered.iterrows():
        with st.expander(f"{row['name']} ({row['cuisine']}) — {row['time_min']}분 / {row['cost_tier']}"):
            st.markdown(f"**식단:** {row['diet']}")
            st.markdown(f"**재료:** {', '.join(row['ingredients'])}")
            st.markdown("### 🥣 레시피")
            st.text(row["recipe"])

# -------------------------------
# 랜덤 메뉴 추천
# -------------------------------
st.markdown("---")
st.subheader("🎲 랜덤 추천")
if st.button("오늘 뭐 먹지?"):
    choice = random.choice(DF["name"].to_list())
    chosen_row = DF[DF["name"] == choice].iloc[0]
    st.success(f"오늘의 추천 메뉴는 **{choice}** 입니다! 🍴")
    st.write(f"요리 분류: {chosen_row['cuisine']} / 조리시간: {chosen_row['time_min']}분 / 비용: {chosen_row['cost_tier']}")
    st.markdown("**재료:** " + ", ".join(chosen_row["ingredients"]))
    st.markdown("### 🥣 레시피")
    st.text(chosen_row["recipe"])

# -------------------------------
# 나만의 메뉴 추가
# -------------------------------
st.markdown("---")
st.header("🍳 나만의 메뉴 추가하기")

with st.form("add_menu"):
    n = st.text_input("메뉴 이름")
    c = st.selectbox("요리 종류", ["한식", "양식", "중식", "일식", "다이어트식", "기타"])
    d = st.selectbox("식단 유형", ["일반식", "채식"])
    t = st.number_input("조리 시간 (분)", min_value=5, max_value=120, value=20)
    cost = st.selectbox("비용대", ["저렴", "중간", "비쌈"])
    ings = st.text_area("재료 (쉼표로 구분)")
    recipe = st.text_area("레시피 (줄바꿈으로 단계 구분)")
    submitted = st.form_submit_button("추가하기")

    if submitted:
        if not n or not ings or not recipe:
            st.error("모든 필드를 입력해주세요.")
        else:
            new = {
                "name": n,
                "cuisine": c,
                "diet": d,
                "time_min": int(t),
                "cost_tier": cost,
                "ingredients": [s.strip() for s in ings.split(",") if s.strip()],
                "recipe": recipe.strip(),
            }
            st.session_state["DF"] = pd.concat([st.session_state["DF"], pd.DataFrame([new])], ignore_index=True)
            st.success(f"'{n}' 메뉴가 추가되었습니다! 🎉")

# -------------------------------
# 푸터
# -------------------------------
st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")
