
# ----------------------------------
# 8. KNN 알고리즘 작동 원리 설명
# ----------------------------------

st.divider()

st.subheader("🤖 KNN 알고리즘은 어떻게 작동할까요?")

st.write("""
KNN(K-Nearest Neighbors)은
가장 가까운 이웃 데이터를 이용하여
새로운 데이터의 품종을 예측하는 분류 알고리즘입니다.
""")

st.markdown("### ① 사용자 입력값 확인")

st.info(
    f"꽃잎 길이: {petal_length:.1f}cm / "
    f"꽃잎 너비: {petal_width:.1f}cm"
)

st.markdown("### ② 가까운 이웃 5개 찾기")

st.write("""
AI는 기존 붓꽃 데이터 150개와 사용자가 입력한 값 사이의
거리를 계산합니다.

이번 프로그램은 StandardScaler를 사용하여
꽃잎 길이와 너비의 크기 차이를 표준화한 후
거리를 계산합니다.
""")

# 가장 가까운 데이터 5개 확인
scaler = model.named_steps["scaler"]
knn = model.named_steps["knn"]

scaled_input = scaler.transform(input_data)
scaled_data = scaler.transform(X)

distances, indices = knn.kneighbors(scaled_input)

neighbors = df.iloc[indices[0]].copy()
neighbors["거리"] = distances[0]
neighbors["순위"] = range(1, 6)

st.dataframe(
    neighbors[
        ["순위", "꽃잎 길이", "꽃잎 너비", "품종", "거리"]
    ].round(3),
    use_container_width=True,
    hide_index=True
)

st.markdown("### ③ 주변 이웃의 품종 확인")

vote_counts = neighbors["품종"].value_counts()

st.write("가장 가까운 5개 데이터의 품종별 투표 결과입니다.")

st.bar_chart(vote_counts)

st.markdown("### ④ 최종 품종 예측")

winner = vote_counts.idxmax()

st.success(
    f"가장 많은 투표를 받은 품종은 "
    f"{species_names[winner]}입니다."
)

st.write(
    "가까운 이웃 5개 중 가장 많이 등장한 품종을 "
    "최종 예측 결과로 선택합니다."
)

st.caption(
    "참고: 동점이 발생하면 KNN의 내부 결정 규칙에 따라 "
    "결과가 선택될 수 있습니다."
)

# ----------------------------------
# 9. 데이터 정보
# ----------------------------------
