import streamlit as st
import pandas as pd
import random
import io

st.set_page_config("저녁 레시피 통합 추천기", layout="centered")

# ---------------------------
# 레시피 데이터 (자세한 계량 + 단계 + 시간)
# ---------------------------
RECIPES = [
    {
        "name": "김치찌개",
        "cuisine": "한식",
        "time_min": 35,
        "cost": "저렴",
        "ingredients": [
            ("묵은김치", "300g"),
            ("돼지고기(목살)", "200g"),
            ("두부", "1/2모"),
            ("양파", "1/2개"),
            ("대파", "1대"),
            ("다진마늘", "1큰술"),
            ("고춧가루", "1큰술"),
            ("멸치육수 또는 물", "500ml"),
            ("식용유", "1큰술"),
            ("소금/설탕(간)", "약간")
        ],
        "steps": [
            {"step": "돼지고기는 한입 크기로 썰고, 김치는 먹기 좋게 자른다.", "est_min": 5},
            {"step": "냄비에 식용유를 두르고 돼지고기를 볶아 겉면이 익으면 다진마늘을 넣고 향을 낸다.", "est_min": 3},
            {"step": "김치를 넣고 함께 3~4분 정도 더 볶아 김치의 신맛을 약간 날린다.", "est_min": 4},
            {"step": "멸치육수(또는 물) 500ml를 붓고 끓인다.", "est_min": 2},
            {"step": "중불로 줄이고 15분 정도 끓여 재료 맛을 우려낸다.", "est_min": 15},
            {"step": "두부와 대파를 넣고 3분 정도 더 끓인 뒤 필요하면 소금/설탕으로 간을 맞춘다.", "est_min": 3}
        ]
    },
    {
        "name": "된장찌개",
        "cuisine": "한식",
        "time_min": 25,
        "cost": "저렴",
        "ingredients": [
            ("된장", "2큰술"),
            ("멸치(국물용)", "6마리"),
            ("감자", "1개"),
            ("애호박", "1/2개"),
            ("양파", "1/2개"),
            ("두부", "1/2모"),
            ("대파", "1/2대"),
            ("다진마늘", "1/2작은술"),
            ("물", "600ml")
        ],
        "steps": [
            {"step": "감자, 애호박, 양파는 한입 크기로 썬다. 두부는 깍둑썰기.", "est_min": 5},
            {"step": "냄비에 물과 멸치를 넣고 5분간 끓여 육수를 만든 후 멸치는 건진다.", "est_min": 5},
            {"step": "감자를 먼저 넣고 끓이다가 된장을 체에 풀어 넣는다.", "est_min": 3},
            {"step": "애호박과 양파를 넣고 5~7분 끓인다.", "est_min": 7},
            {"step": "두부와 대파, 다진마늘을 넣고 1~2분 더 끓여 간을 맞춘다.", "est_min": 2}
        ]
    },
    {
        "name": "스파게티 알리오 올리오",
        "cuisine": "이탈리아식",
        "time_min": 20,
        "cost": "저렴",
        "ingredients": [
            ("스파게티면", "100g (1인분)"),
            ("올리브오일", "4큰술"),
            ("마늘(슬라이스)", "4쪽"),
            ("페페론치노(말린 고추)", "약간"),
            ("파슬리(선택)", "약간"),
            ("소금", "면 삶을 때"),
            ("후추", "약간")
        ],
        "steps": [
            {"step": "끓는 물에 소금을 넣고 스파게티면을 포장지 표기 시간보다 1분 덜 삶는다.", "est_min": 8},
            {"step": "팬에 올리브오일을 두르고 중약불에서 마늘을 천천히 볶아 향을 낸다.", "est_min": 3},
            {"step": "페페론치노를 넣고 불을 끈 뒤 삶은 면과 면수 1/4컵을 팬에 넣고 재빨리 버무린다.", "est_min": 2},
            {"step": "파슬리와 후추를 뿌려 마무리한다.", "est_min": 1}
        ]
    },
    {
        "name": "두부야채볶음(간단 비건)",
        "cuisine": "중식",
        "time_min": 15,
        "cost": "저렴",
        "ingredients": [
            ("두부", "1모"),
            ("양파", "1/2개"),
            ("파프리카", "1/2개"),
            ("간장", "1큰술"),
            ("다진마늘", "1작은술"),
            ("참기름", "1작은술"),
            ("식용유", "1큰술")
        ],
        "steps": [
            {"step": "두부는 물기를 제거해 깍둑썰기 후 팬에 노릇하게 굽거나 튀겨둔다.", "est_min": 6},
            {"step": "팬에 식용유를 두르고 양파, 파프리카를 볶다가 다진마늘과 간장을 넣어 간을 한다.", "est_min": 4},
            {"step": "구운 두부를 넣고 재빨리 섞은 뒤 참기름을 둘러 마무리한다.", "est_min": 2}
        ]
    }
]

# ---------------------------
# 헬퍼: DataFrame 생성
# ---------------------------
df = pd.DataFrame([{"name": r["name"], "cuisine": r["cuisine"], "time_min": r["time_min"], "cost": r["cost"]} for r in RECIPES])

# ---------------------------
# UI: 헤더 / 사이드바 필터
# ---------------------------
st.title("🍽 저녁 메뉴 추천 + 실제 조리 레시피")
st.write("메뉴를 선택하면 아래에 재료와 단계별 조리법(예상 시간 포함)이 나타납니다. 재료 체크 후 장보기 버튼으로 다운로드 가능.")

st.sidebar.header("필터")
cuisine_choice = st.sidebar.selectbox("요리 스타일", options=["전체"] + sorted(df["cuisine"].unique().tolist()))
max_time = st.sidebar.slider("최대 조리 시간(분)", min_value=5, max_value=60, value=40, step=5)
cost_choice = st.sidebar.selectbox("예산", options=["전체", "저렴", "중간", "비쌈"])

# ---------------------------
# 필터 적용 및 메뉴 선택
# ---------------------------
filtered_df = df.copy()
if cuisine_choice != "전체":
    filtered_df = filtered_df[filtered_df["cuisine"] == cuisine_choice]
filtered_df = filtered_df[filtered_df["time_min"] <= max_time]
if cost_choice != "전체":
    filtered_df = filtered_df[filtered_df["cost"] == cost_choice]

st.subheader("추천 메뉴 목록")
if filtered_df.empty:
    st.info("조건에 맞는 메뉴가 없습니다. 필터를 조정해 보세요.")
else:
    # 메뉴 선택 UI: 라디오 + 'Surprise me' 버튼
    menu_names = filtered_df["name"].tolist()
    col1, col2 = st.columns([3,1])
    with col1:
        selected = st.radio("메뉴 선택", options=menu_names, index=0)
    with col2:
        if st.button("🎲 Surprise me"):
            selected = random.choice(menu_names)
            # set as session so below content updates
            st.session_state["_selected_temp"] = selected

    # if Surprise me set session flag, read it
    if "_selected_temp" in st.session_state:
        selected = st.session_state.pop("_selected_temp")

    # 찾은 레시피 객체
    recipe = next((r for r in RECIPES if r["name"] == selected), None)

    # ---------------------------
    # 레시피 표시 영역
    # ---------------------------
    if recipe:
        st.markdown(f"## {recipe['name']}  —  {recipe['cuisine']}  •  {recipe['time_min']}분  •  {recipe['cost']}")
        st.markdown("### 🧾 재료")
        # 재료 체크박스 (장보기용)
        ingredient_checks = []
        for idx, (ing, qty) in enumerate(recipe["ingredients"]):
            key = f"ing_{recipe['name']}_{idx}"
            checked = st.checkbox(f"{ing} — {qty}", key=key)
            ingredient_checks.append((ing, qty, checked))

        # 장보기 리스트 다운로드
        if st.button("🛒 장보기 목록으로 저장"):
            lines = [f"{ing} — {qty}" for ing, qty, checked in ingredient_checks if not checked]
            if not lines:
                st.info("체크된 재료가 없습니다 — 비워두고 다운로드를 원하면 '장보기 목록 생성' 버튼을 눌러주세요.")
            text = "\n".join(lines) if lines else "\n(체크된 모든 재료가 선택됨)"
            b = io.BytesIO(text.encode("utf-8"))
            st.download_button("다운로드 (ingredients.txt)", data=b, file_name=f"{recipe['name']}_ingredients.txt", mime="text/plain")

        st.markdown("---")
        st.markdown("### 👩‍🍳 조리 단계 (예상 시간 포함)")
        # 단계별 체크박스 (완료 표시)
        total_est = 0
        for i, s in enumerate(recipe["steps"], start=1):
            total_est += s.get("est_min", 0)
            step_key = f"step_{recipe['name']}_{i}"
            cols = st.columns([8,2])
            with cols[0]:
                st.markdown(f"**Step {i}.** {s['step']}")
            with cols[1]:
                done = st.checkbox(f"{s.get('est_min',0)}분", key=step_key)
        st.markdown(f"**예상 총 조리 시간(단계 합):** {total_est} 분 (참고용)")

        # 요리 시작 버튼(단계 리셋)
        if st.button("✅ 단계 완료 표시 초기화"):
            # 모든 step and ingredient keys related to this recipe -> reset
            for i in range(len(recipe["ingredients"])):
                key = f"ing_{recipe['name']}_{i}"
                if key in st.session_state:
                    st.session_state[key] = False
            for i in range(len(recipe["steps"])):
                key = f"step_{recipe['name']}_{i+1}"
                if key in st.session_state:
                    st.session_state[key] = False
            st.experimental_rerun()

    else:
        st.error("선택한 메뉴의 레시피를 찾을 수 없습니다.")

# ---------------------------
# 메뉴 추가 (사용자)
# ---------------------------
st.markdown("---")
with st.expander("✍️ 새 레시피 추가하기 (사용자 저장은 세션에만 저장됩니다)"):
    with st.form("add_recipe_form"):
        name = st.text_input("메뉴 이름")
        cuisine_new = st.selectbox("요리 스타일", ["한식","중식","일식","이탈리아식","기타"])
        time_new = st.number_input("예상 소요 시간(분)", min_value=5, max_value=240, value=20)
        cost_new = st.selectbox("예산", ["저렴","중간","비쌈"])
        # 재료 입력: 한 줄에 '재료 — 수량' 또는 '재료,수량' 형식 권장
        ing_text = st.text_area("재료 (한 줄에 하나씩 — 예: 두부,200g)", height=120)
        steps_text = st.text_area("단계별 조리법 (한 줄에 하나의 단계와 예상 분 수를 같이 적어주세요. 예: '팬을 달군다|2')", height=160)
        submit_new = st.form_submit_button("저장")

        if submit_new:
            if not name.strip() or not ing_text.strip() or not steps_text.strip():
                st.error("모든 필드를 채워 주세요.")
            else:
                # 파싱
                ing_lines = [l.strip() for l in ing_text.splitlines() if l.strip()]
                ingreds = []
                for line in ing_lines:
                    if "," in line:
                        a,b = line.split(",",1)
                        ingreds.append((a.strip(), b.strip()))
                    elif "—" in line:
                        a,b = line.split("—",1)
                        ingreds.append((a.strip(), b.strip()))
                    else:
                        ingreds.append((line.strip(), "적당량"))
                step_lines = [l.strip() for l in steps_text.splitlines() if l.strip()]
                steps_parsed = []
                for line in step_lines:
                    if "|" in line:
                        txt, mm = line.split("|",1)
                        try:
                            est = int(mm.strip())
                        except:
                            est = 0
                        steps_parsed.append({"step": txt.strip(), "est_min": est})
                    else:
                        steps_parsed.append({"step": line, "est_min": 0})

                new_recipe = {
                    "name": name.strip(),
                    "cuisine": cuisine_new,
                    "time_min": int(time_new),
                    "cost": cost_new,
                    "ingredients": ingreds,
                    "steps": steps_parsed
                }
                # 세션에 추가
                RECIPES.append(new_recipe)
                df = pd.concat([df, pd.DataFrame([{"name": new_recipe["name"], "cuisine": new_recipe["cuisine"],
                                                  "time_min": new_recipe["time_min"], "cost": new_recipe.get("cost","저렴")}])], ignore_index=True)
                st.success(f"'{new_recipe['name']}' 레시피가 추가되었습니다. 페이지 상단의 메뉴에서 선택해 보세요.")
