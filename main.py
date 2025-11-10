import streamlit as st
st.subheader("추천 메뉴")
filtered = filter_dishes(DF)


if filtered.empty:
    st.info("해당 조건에 맞는 메뉴가 없습니다. 필터를 줄이거나 'Surprise me'를 눌러보세요.")
else:
# Show top 5
to_show = filtered.sample(n=min(5, len(filtered)), random_state=42)
for idx, row in to_show.iterrows():
with st.expander(f"{row['name']} — {row['cuisine']} ({row['time_min']}분)"):
st.markdown(f"**식단:** {row['diet']}")
st.markdown(f"**비용:** {row['cost_tier']}")
st.markdown("**재료:** " + ", ".join(row['ingredients']))
st.markdown(f"[레시피 바로가기]({row['recipe']})")


with col2:
st.subheader("빠른 선택")
if st.button("Surprise me 🎲"):
candidate = filter_dishes(DF)
if candidate.empty:
st.warning("조건에 맞는 메뉴가 없습니다. 필터를 확인하세요.")
else:
choice = candidate.sample(n=1).iloc[0]
st.success(f"오늘의 추천: {choice['name']} ({choice['cuisine']})")
st.write(f"재료: {', '.join(choice['ingredients'])}")
st.write(f"시간: {choice['time_min']}분 — 비용: {choice['cost_tier']}")
st.markdown(f"[레시피]({choice['recipe']})")


st.markdown('---')
st.subheader("추가 기능")
if st.button("Generate 7-day meal plan"):
pool = filter_dishes(DF)
if len(pool) < 1:
st.warning("충분한 메뉴가 없어 주간 계획을 만들 수 없습니다.")
else:
plan = pool.sample(n=min(7, len(pool)), replace=(len(pool) < 7)).reset_index(drop=True)
for i, r in plan.iterrows():
st.write(f"**Day {i+1}:** {r['name']} — {r['time_min']}분 — {r['cuisine']}")


# --- Add custom dish ---
st.markdown('---')
st.header('메뉴 추가하기')
with st.form('add_dish'):
n = st.text_input('메뉴 이름')
c = st.selectbox('Cuisine', options=['Korean','Italian','Japanese','Chinese','Indian','American','Other'])
d = st.selectbox('Diet', options=['non-vegetarian','vegetarian','vegan','pescatarian'])
t = st.number_input('Prep time (minutes)', min_value=5, max_value=300, value=30)
cost = st.selectbox('Cost tier', options=['low','medium','high'])
ings = st.text_area('Ingredients (comma separated)')
recipe = st.text_input('Recipe URL (optional)')
submitted = st.form_submit_button('추가')
if submitted:
if not n or not ings:
st.error('이름과 재료는 필수입니다.')
else:
new = {
'name': n,
'cuisine': c,
'diet': d,
'time_min': int(t),
'cost_tier': cost,
'ingredients': [s.strip() for s in ings.split(',') if s.strip()],
'recipe': recipe or ''
}
# append to dataframe stored in session state
if 'user_dishes' not in st.session_state:
st.session_state['user_dishes'] = []
st.session_state['user_dishes'].append(new)
st.success(f"{n}이(가) 추가되었습니다!")


# Merge user dishes for filtering
if 'user_dishes' in st.session_state and st.session_state['user_dishes']:
user_df = pd.DataFrame(st.session_state['user_dishes'])
# ensure same columns
for col in ['cuisine','diet','time_min','cost_tier','ingredients','recipe','name']:
if col not in user_df.columns:
user_df[col] = ''
DF = pd.concat([DF, user_df], ignore_index=True)


st.sidebar.markdown('\n---\nMade with ❤️ using Streamlit')


# Footer: tips
st.markdown('\n---\n**Tip:**** 필터를 조합해서 재료 냉장고 상황에 맞는 메뉴를 찾아보세요. GitHub에 올리고 Streamlit Cloud로 배포하면 URL로 바로 공유할 수 있습니다.')
