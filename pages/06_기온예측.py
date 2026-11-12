
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")
st.write("과거 기온 데이터를 분석하고 선형회귀 알고리즘으로 미래 기온을 예측합니다.")


# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

# 현재 PY 파일은 pages 폴더에 있음
# CSV 파일은 pages의 상위 폴더에 있음

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "temperature.csv"

if not CSV_PATH.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.write(f"확인한 경로: {CSV_PATH}")
    st.stop()


# ==========================================
# 3. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(path):
    for encoding in ["cp949", "utf-8-sig", "utf-8", "euc-kr"]:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해주세요.")


try:
    df = load_data(str(CSV_PATH))
except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()


# ==========================================
# 4. 데이터 전처리
# ==========================================

required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일에 '일시', '평균기온(℃)' 열이 필요합니다.")
    st.stop()

# 날짜 변환
df["날짜"] = pd.to_datetime(
    df["일시"].astype(str).str.strip(),
    format="%b-%y",
    errors="coerce"
)

# 평균기온 숫자 변환
df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

# 결측값 제거
df = df.dropna(
    subset=["날짜", "평균기온(℃)"]
).copy()

# 연도와 월 분리
df["연도"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month

if df.empty:
    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()


# ==========================================
# 5. 월 선택 및 예측 연도 입력
# ==========================================

st.subheader("🔎 분석 조건 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

col1, col2 = st.columns(2)

with col1:
    selected_month_name = st.selectbox(
        "📅 분석할 월을 선택하세요",
        list(month_names.values())
    )

selected_month = [
    k for k, v in month_names.items()
    if v == selected_month_name
][0]

latest_year = int(df["연도"].max())

with col2:
    forecast_year = st.number_input(
        "🔮 예측할 연도를 입력하세요",
        min_value=latest_year + 1,
        max_value=2100,
        value=max(latest_year + 1, 2030),
        step=1
    )

forecast_year = int(forecast_year)


# ==========================================
# 6. 선택한 월의 데이터 추출
# ==========================================

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

# 같은 연도에 여러 데이터가 있으면 평균 계산
month_df = (
    month_df.groupby("연도", as_index=False)
    ["평균기온(℃)"].mean()
)

if len(month_df) < 2:
    st.error("선택한 월의 데이터가 2개 미만입니다.")
    st.stop()


# ==========================================
# 7. 선형회귀 알고리즘 학습
# ==========================================

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

model = LinearRegression()

# 과거 데이터를 이용한 학습
model.fit(X, y)

# 미래 기온 예측
future_data = pd.DataFrame({
    "연도": [forecast_year]
})

predicted_temperature = float(
    model.predict(future_data)[0]
)

# 회귀식의 기울기와 절편
slope = float(model.coef_[0])
intercept = float(model.intercept_)

# 결정계수
r_squared = float(model.score(X, y))


# ==========================================
# 8. 회귀선 데이터 만들기
# ==========================================

line_years = list(
    range(
        int(month_df["연도"].min()),
        forecast_year + 1
    )
)

line_df = pd.DataFrame({
    "연도": line_years
})

line_df["회귀선 기온"] = model.predict(
    line_df[["연도"]]
)


# ==========================================
# 9. 예측 결과 표시
# ==========================================

st.divider()

st.subheader(
    f"📊 {selected_month_name} 평균기온 분석 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "예측 연도",
        f"{forecast_year}년"
    )

with col2:
    st.metric(
        "예측 평균기온",
        f"{predicted_temperature:.1f}℃"
    )

with col3:
    st.metric(
        "결정계수 R²",
        f"{r_squared:.3f}"
    )


# ==========================================
# 10. 그래프 그리기
# ==========================================

fig = go.Figure()

# 실제 기온 데이터
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#2878B5",
            size=9
        ),
        hovertemplate=
        "%{x}년<br>실제 기온: %{y:.1f}℃<extra></extra>"
    )
)

# 선형회귀 추세선
fig.add_trace(
    go.Scatter(
        x=line_df["연도"],
        y=line_df["회귀선 기온"],
        mode="lines",
        name="선형회귀 추세선",
        line=dict(
            color="#E87524",
            width=3,
            dash="dash"
        ),
        hovertemplate=
        "%{x}년<br>회귀선 기온: %{y:.1f}℃<extra></extra>"
    )
)

# 미래 예측값
fig.add_trace(
    go.Scatter(
        x=[forecast_year],
        y=[predicted_temperature],
        mode="markers",
        name="미래 예측 기온",
        marker=dict(
            color="red",
            size=17,
            symbol="star"
        ),
        hovertemplate=
        "%{x}년<br>예측 기온: %{y:.1f}℃<extra></extra>"
    )
)

# 예측값 설명 표시
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

st.plotly_chart(
    fig,
    use_container_width=True
)

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
### 선형회귀란?

선형회귀(Linear Regression)는 과거 데이터의 관계를
가장 잘 나타내는 직선을 찾아 미래의 값을 예측하는 알고리즘입니다.

이번 프로그램에서는 다음과 같은 순서로 작동합니다.

**① 데이터 수집**

CSV 파일에서 선택한 월의 과거 평균기온을 가져옵니다.

**② 데이터 학습**

연도와 평균기온 사이의 관계를 분석합니다.

**③ 최적의 직선 찾기**

실제 기온 데이터와 직선 사이의 오차 제곱합이
가장 작아지는 직선을 찾습니다.

**④ 미래 기온 예측**

학습한 직선에 사용자가 입력한 미래 연도를 넣어
예상 평균기온을 계산합니다.
""")

st.markdown("### 선형회귀의 기본 수식")

st.latex(r"y = ax + b")

st.markdown("""
- x : 연도
- y : 예측 평균기온
- a : 기울기
- b : y절편

기울기 a가 양수이면 기온이 상승하는 추세이고,
음수이면 하락하는 추세입니다.
""")

# 실제 계산값
st.markdown("### 📐 이번 분석의 선형회귀 계산 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "기울기 (a)",
        f"{slope:.4f} ℃/년"
    )

with col2:
    st.metric(
        "y절편 (b)",
        f"{intercept:.2f}"
    )

with col3:
    st.metric(
        "결정계수 (R²)",
        f"{r_squared:.3f}"
    )

st.markdown(
    f"**이번 분석의 회귀식:** "
    f"`y = {slope:.4f}x + {intercept:.2f}`"
)

if slope > 0:
    st.success(
        f"📈 {selected_month_name} 평균기온은 "
        f"과거 데이터에서 1년에 약 {slope:.3f}℃ 상승하는 추세입니다."
    )

elif slope < 0:
    st.info(
        f"📉 {selected_month_name} 평균기온은 "
        f"과거 데이터에서 1년에 약 {abs(slope):.3f}℃ 하락하는 추세입니다."
    )

else:
    st.info("기온의 뚜렷한 상승 또는 하락 추세가 거의 없습니다.")

st.markdown("""
### 결정계수(R²)란?

결정계수는 회귀선이 과거 기온 데이터의 변화를
얼마나 잘 설명하는지 나타내는 값입니다.

- 1에 가까울수록 과거 데이터의 변화를 잘 설명합니다.
- 0에 가까울수록 직선으로 설명하기 어렵습니다.

단, 결정계수가 높더라도 미래 예측이 반드시 정확하다는 뜻은 아닙니다.

⚠️ **주의사항**

이 프로그램은 과거 기온의 직선 추세가 미래에도 이어진다고 가정합니다.
실제 기온은 기후변화와 다양한 자연적 요인의 영향을 받으므로
예측 결과는 참고용으로 활용해야 합니다.
""")


# ==========================================
# 12. 실제 학습 데이터 확인
# ==========================================

with st.expander("📋 선형회귀 학습에 사용한 데이터 확인"):

    display_df = month_df.copy()

    display_df["평균기온(℃)"] = (
        display_df["평균기온(℃)"].round(1)
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

st.caption("데이터 출처: temperature.csv")
