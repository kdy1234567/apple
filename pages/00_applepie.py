import streamlit as st
import pandas as pd
import random

# -------------------------------
# 기본 메뉴 데이터 (조리법 포함)
# -------------------------------
BASE_MENUS = [
    {
        "name": "김치찌개",
        "cuisine": "한식",
        "diet": "일반식",
        "time_min": 30,
        "cost_tier": "저렴",
        "ingredients": ["김치 ¼포기","돼지고기 목살 300g","두부 ½모","양파 ¼개","대파 1대","청양고추 1개","다진마늘 1큰술","참치액젓 1큰술","고춧가루 2큰술","설탕 1작은술"],
        "recipe": (
            "1. 돼지고기를 먹기 좋은 크기로 썰고, 김치는 한입 크기로 썬다.\n"
            "2. 냄비에 식용유를 두르고 돼지고기를 중불로 볶아 겉면이 익으면 다진마늘과 참치액젓을 넣고 볶는다.\n"
            "3. 김치와 김치국물(약 100mL)을 넣고 물 400mL를 부은 후 강불로 끓인다.\n"
            "4. 양파, 대파, 청양고추를 넣고 중불로 줄여 20분간 끓인다.\n"
            "5. 두부를 넣고 5분간 더 끓인다. 필요하면 소금이나 국간장으로 간을 맞춘다.\n"
            "6. 마지막에 후추 약간 뿌려서 완성한다."
        ),
    },
    {
        "name": "된장찌개",
        "cuisine": "한식",
        "diet": "일반식",
        "time_min": 25,
        "cost_tier": "저렴",
        "ingredients": ["시판 된장 2큰술","쌀뜨물 또는 생수 2컵","애호박 ½개","양파 ¼개","감자 ½개","두부 ½모","대파 ¼대","청양고추 1개","멸치 4마리","다진마늘 ½작은술"],
        "recipe": (
            "1. 애호박, 양파, 감자, 두부는 먹기 좋은 크기로 썬다. 청양고추와 대파는 어슷 썬다.\n"
            "2. 냄비에 멸치를 넣고 약불에서 2~3분간 볶다가 쌀뜨물 또는 생수 400mL를 붓고 육수를 낸다.\n"
            "3. 감자를 먼저 넣고 1분간 끓인 뒤 애호박, 양파, 다진마늘, 된장을 넣고 5분간 끓인다.\n"
            "4. 대파, 청양고추, 두부를 넣고 약 1분 더 끓이면 완성된다.\n"
            "5. 필요하면 소금이나 국간장으로 간을 맞춘다."
        ),
    },
    # 다른 메뉴들도 동일 패턴으로 추가 가능
]

if "DF" not in st.session_state:
    st.session_state["DF"] = pd.DataFrame(BASE_MENUS)

DF = st.session_state["DF"]

# -------------------------------
# UI 시작
# -------------------------------
st.title("🍽 오늘 저녁 뭐 먹지?")
st.caption("메뉴 추천 + 실제 조리법까지 한 번에")

# 필터
st.sidebar.header("🔍 필터 옵션")
cuisine = st.sidebar.selectbox("요리 종류", ["전체", "한식", "양식", "중식", "일식", "다이어트식"])
max_time = st.sidebar.slider("최대 조리 시간 (분)", 5, 60, 30)
cost = st.sidebar.selectbox("비용대", ["전체", "저렴", "중간", "비쌈"])

# 필터 적용
filtered = DF.copy()
if cuisine != "전체":
    filtered = filtered[filtered["cuisine"] == cuisine]
filtered = filtered[filtered["time_min"] <= max_time]
if cost != "전체":
    filtered = filtered[filtered["cost_tier"] == cost]

# 추천 메뉴 표시 + 레시피 보기
st.subheader("🍱 추천 메뉴 & 레시피")
if filtered.empty:
    st.info("조건에 맞는 메뉴가 없습니다. 필터를 조정해보세요.")
else:
    for _, row in filtered.iterrows():
        with st.expander(f"{row['name']} ({row['cuisine']}) — {row['time_min']}분 / {row['cost_tier']}"):
            st.markdown(f"**재료:** {', '.join(row['ingredients'])}")
            st.markdown("### 🥣 조리법")
            st.text(row["recipe"])

# 랜덤 추천
st.markdown("---")
st.subheader("🎲 랜덤 메뉴 + 레시피")
if st.button("오늘 뭐 먹지?"):
    choice = random.choice(DF["name"].to_list())
    chosen = DF[DF["name"] == choice].iloc[0]
    st.success(f"오늘의 추천 메뉴는 **{choice}** 입니다! 🍴")
    st.write(f"요리 종류: {chosen['cuisine']} / 조리시간: {chosen['time_min']}분 / 비용대: {chosen['cost_tier']}")
    st.markdown(f"**재료:** {', '.join(chosen['ingredients'])}")
    st.markdown("### 🥣 조리법")
    st.text(chosen["recipe"])

# 메뉴 추가 기능
st.markdown("---")
st.header("🍳 나만의 메뉴 추가하기")
with st.form("add_menu"):
    n = st.text_input("메뉴 이름")
    c = st.selectbox("요리 종류", ["한식", "양식", "중식", "일식", "다이어트식", "기타"])
    d = st.selectbox("식단 유형", ["일반식", "채식"])
    t = st.number_input("조리 시간 (분)", min_value=5, max_value=120, value=20)
    cost_new = st.selectbox("비용대", ["저렴", "중간", "비쌈"])
    ings = st.text_area("재료 (쉼표로 구분)")
    recipe_new = st.text_area("조리법 (줄바꿈으로 단계 구분)")
    submitted = st.form_submit_button("추가하기")
    if submitted:
        if not n or not ings or not recipe_new:
            st.error("메뉴 이름, 재료, 조리법을 모두 입력해주세요.")
        else:
            new = {
                "name": n,
                "cuisine": c,
                "diet": d,
                "time_min": int(t),
                "cost_tier": cost_new,
                "ingredients": [s.strip() for s in ings.split(",") if s.strip()],
                "recipe": recipe_new.strip(),
            }
            st.session_state["DF"] = pd.concat([st.session_state["DF"], pd.DataFrame([new])], ignore_index=True)
            st.success(f"'{n}' 메뉴가 추가되었습니다! 🎉")

# 푸터
st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")
