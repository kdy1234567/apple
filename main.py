import streamlit as st
import pandas as pd
import random

# -------------------------------
# 기본 메뉴 데이터
# -------------------------------
BASE_MENUS = [
    {"name": "김치찌개", "cuisine": "Korean", "diet": "non-vegetarian", "time_min": 25, "cost_tier": "low", "ingredients": ["김치", "돼지고기", "두부"], "recipe": ""},
    {"name": "된장찌개", "cuisine": "Korean", "diet": "non-vegetarian", "time_min": 20, "cost_tier": "low", "ingredients": ["된장", "애호박", "두부"], "recipe": ""},
    {"name": "파스타", "cuisine": "Italian", "diet": "non-vegetarian", "time_min": 30, "cost_tier": "medium", "ingredients": ["스파게티면", "토마토소스"], "recipe": ""},
    {"name": "샐러드", "cuisine": "Other", "diet": "vegetarian", "time_min": 10, "cost_tier": "low", "ingredients": ["채소", "드레싱"], "recipe": ""},
    {"name": "초밥", "cuisine": "Japanese", "diet": "pescatarian", "time_min": 25, "cost_tier": "high", "ingredients": ["밥", "연어", "간장"], "recipe": ""},
    {"name": "짜장면", "cuisine": "Chinese", "diet": "non-vegetarian", "time_min": 20, "cost_tier": "low", "ingredients": ["면", "춘장", "돼지고기"], "recipe": ""},
]

# -------------------------------
# 데이터프레임 초기화
# -------------------------------
if "DF" not in st.session_state:
    st.session_state["DF"] = pd.DataFrame(BASE_MENUS)

DF = st.session_state["DF"]

# -------------------------------
# 필터 함수 정의
# -------------------------------
def filter_dishes(df, cuisine=None, diet=None, max_time=None, cost=None):
    result = df.copy()
    if cuisine and cuisine != "All":
        result = result[result["cuisine"] == cuisine]
    if diet and diet != "All":
        result = result[result["diet"] == diet]
    if max_time:
        result = result[result["time_min"] <= max_time]
    if cost and cost != "All":
        result = result[result["cost_tier"] == cost]
    return result

# -------------------------------
# UI 시작
# -------------------------------
st.title("🍽 오늘 저녁 뭐 먹지?")
st.caption("Streamlit으로 만든 메뉴 추천 사이트")

# 필터 선택
st.sidebar.header("🔍 필터 옵션")
cuisine = st.sidebar.selectbox("요리 종류", ["All", "Korean", "Japanese", "Chinese", "Italian", "Indian", "American", "Other"])
diet = st.sidebar.selectbox("식단 종류", ["All", "non-vegetarian", "vegetarian", "vegan", "pescatarian"])
max_time = st.sidebar.slider("최대 조리 시간 (분)", 5, 60, 30)
cost = st.sidebar.selectbox("비용대", ["All", "low", "medium", "high"])

# 필터 적용
filtered = filter_dishes(DF, cuisine, diet, max_time, cost)

# -------------------------------
# 추천 메뉴 출력
# -------------------------------
st.subheader("🍱 추천 메뉴")
if filtered.empty:
    st.info("해당 조건에 맞는 메뉴가 없습니다. 필터를 조정하거나 'Surprise me'를 눌러보세요.")
else:
    to_show = filtered.sample(n=min(5, len(filtered)), random_state=42)
    for _, row in to_show.iterrows():
        with st.expander(f"{row['name']} — {row['cuisine']} ({row['time_min']}분)"):
            st.markdown(f"**식단:** {row['diet']}")
            st.markdown(f"**비용:** {row['cost_tier']}")
            st.markdown("**재료:** " + ", ".join(row['ingredients']))
            if row["recipe"]:
                st.markdown(f"[레시피 보기]({row['recipe']})")

# -------------------------------
# 빠른 랜덤 추천
# -------------------------------
st.markdown("---")
st.subheader("🎲 빠른 추천")

if st.button("Surprise me!"):
    candidate = filter_dishes(DF, cuisine, diet, max_time, cost)
    if candidate.empty:
        st.warning("조건에 맞는 메뉴가 없습니다. 필터를 확인하세요.")
    else:
        choice = candidate.sample(n=1).iloc[0]
        st.success(f"오늘의 추천: **{choice['name']} ({choice['cuisine']})**")
        st.write(f"재료: {', '.join(choice['ingredients'])}")
        st.write(f"시간: {choice['time_min']}분 — 비용: {choice['cost_tier']}")

# -------------------------------
# 7일 식단 추천
# -------------------------------
st.markdown("---")
st.subheader("📅 7일 식단 생성")

if st.button("7일 식단 만들기"):
    pool = filter_dishes(DF, cuisine, diet, max_time, cost)
    if len(pool) < 1:
        st.warning("충분한 메뉴가 없습니다.")
    else:
        plan = pool.sample(n=min(7, len(pool)), replace=(len(pool) < 7)).reset_index(drop=True)
        for i, r in plan.iterrows():
            st.write(f"**Day {i+1}:** {r['name']} — {r['time_min']}분 — {r['cuisine']}")

# -------------------------------
# 사용자 메뉴 추가
# -------------------------------
st.markdown("---")
st.header("🍳 나만의 메뉴 추가")

with st.form("add_dish"):
    n = st.text_input("메뉴 이름")
    c = st.selectbox("Cuisine", options=["Korean", "Italian", "Japanese", "Chinese", "Indian", "American", "Other"])
    d = st.selectbox("Diet", options=["non-vegetarian", "vegetarian", "vegan", "pescatarian"])
    t = st.number_input("조리 시간 (분)", min_value=5, max_value=300, value=30)
    cost = st.selectbox("Cost tier", options=["low", "medium", "high"])
    ings = st.text_area("재료 (쉼표로 구분)")
    recipe = st.text_input("레시피 링크 (선택)")
    submitted = st.form_submit_button("추가하기")

    if submitted:
        if not n or not ings:
            st.error("이름과 재료는 필수입니다.")
        else:
            new = {
                "name": n,
                "cuisine": c,
                "diet": d,
                "time_min": int(t),
                "cost_tier": cost,
                "ingredients": [s.strip() for s in ings.split(",") if s.strip()],
                "recipe": recipe or ""
            }
            st.session_state["DF"] = pd.concat([st.session_state["DF"], pd.DataFrame([new])], ignore_index=True)
            st.success(f"'{n}' 메뉴가 추가되었습니다! 🎉")

# -------------------------------
# 푸터
# -------------------------------
st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")
