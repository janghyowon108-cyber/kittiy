hovertemplate="%{x}년<br>예측 기온: %{y:.1f}℃<extra></extra>"
    )
)

fig.add_annotation(
    x=forecast_year,
    y=predicted_temperature,
    text=f"{forecast_year}년 예측<br>{predicted_temperature:.1f}℃",
    showarrow=True,
    arrowhead=2,
    ax=45,
    ay=-45
)

fig.update_layout(
    title=f"{selected_month_name} 연도별 평균기온 및 미래 예측",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    hovermode="x unified",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "🔵 파란 점: 실제 기온 | "
    "🟠 주황색 점선: 선형회귀 추세선 | "
    "🔴 빨간 별: 미래 예측 기온"
)

# ==========================================
# 11. 선형회귀 알고리즘 설명
# ==========================================
st.divider()
st.subheader("🧠 선형회귀 알고리즘 알아보기")

st.markdown("""
**선형회귀(Linear Regression)**는 과거 데이터의 관계를
가장 잘 나타내는 직선을 찾아 미래의 값을 예측하는 알고리즘입니다.

이번 프로그램의 작동 과정은 다음과 같습니다.

1. **데이터 수집:** CSV에서 선택한 월의 연도별 평균기온을 가져옵니다.
2. **데이터 학습:** 연도와 평균기온 사이의 관계를 분석합니다.
3. **최적의 직선 찾기:** 실제 기온과 직선 사이의 오차 제곱합이 최소가 되도록 기울기와 절편을 계산합니다.
4. **미래 예측:** 계산한 직선에 사용자가 입력한 미래 연도를 넣어 예상 기온을 구합니다.
""")

st.latex(r"y = ax + b")

st.markdown("""
- **x:** 연도
- **y:** 예측 평균기온
- **a:** 기울기 (연도가 1년 증가할 때 기온이 변하는 정도)
- **b:** y절편 (직선의 위치를 결정하는 값)
""")

st.subheader("📐 이번 분석의 선형회귀 계산 결과")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.metric("기울기 (a)", f"{slope:.4f}℃/년")

with info_col2:
    st.metric("y절편 (b)", f"{intercept:.2f}")

with info_col3:
    st.metric("결정계수 (R²)", f"{r_squared:.3f}")

st.markdown(
    f"**이번 분석의 회귀식:** "
    f"`y = {slope:.4f} × x + ({intercept:.2f})`"
)

if slope > 0:
    st.success(
        f"📈 {selected_month_name} 평균기온은 과거 데이터에서 "
        f"연평균 약 {slope:.3f}℃ 상승하는 추세입니다."
    )
elif slope < 0:
    st.info(
        f"📉 {selected_month_name} 평균기온은 과거 데이터에서 "
        f"연평균 약 {abs(slope):.3f}℃ 하락하는 추세입니다."
    )
else:
    st.info("과거 데이터에서 뚜렷한 상승 또는 하락 추세가 거의 없습니다.")

st.markdown("""
### 결정계수(R²)란?

결정계수는 회귀선이 과거 기온 데이터의 변화를 얼마나 설명하는지 나타냅니다.

- 1에 가까울수록 회귀선이 과거 데이터의 변화를 잘 설명합니다.
- 0에 가까울수록 직선으로 설명하기 어렵습니다.

단, 결정계수가 높더라도 미래 예측이 반드시 정확하다는 뜻은 아닙니다.

⚠️ 이 프로그램은 과거 기온의 직선 추세가 미래에도 이어진다고 가정합니다.
실제 기온은 기후변화와 자연적 요인 등 다양한 영향을 받으므로
예측 결과는 참고용으로 활용해주세요.
""")

# ==========================================
# 12. 학습에 사용한 데이터 확인
# ==========================================
with st.expander("📋 선형회귀 학습에 사용한 실제 데이터 확인"):

    display_df = month_df.copy()
    display_df["평균기온(℃)"] = display_df["평균기온(℃)"].round(1)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

st.caption("데이터 출처: temperature.csv")
