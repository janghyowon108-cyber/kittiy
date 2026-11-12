
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="서울 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 분석 및 예측")
st.markdown("""
과거 서울의 기온 데이터를 분석하고,
**선형회귀 알고리즘**을 이용해 미래의 평균기온을 예측해 봅니다.
""")

# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "temperature.csv"

# ==========================================
# 3. 데이터 불러오기
# ==========================================
@st.cache_data
def load_data(file_path):

    encodings = ["cp949", "utf-8-sig", "utf-8", "euc-kr"]
    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 파일의 인코딩을 확인해주세요.")

    required_columns = ["일시", "평균기온(℃)"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"CSV 파일에 '{column}' 열이 없습니다."
            )

    # 날짜 변환
    df["일시"] = pd.to_datetime(
        df["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 기온을 숫자로 변환
    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"],
        errors="coerce"
    )

    # 잘못된 데이터 제거
    df = df.dropna(
        subset=["일시", "평균기온(℃)"]
    ).copy()

    # 연도와 월 추출
    df["연도"] = df["일시"].dt.year
    df["월"] = df["일시"].dt.month

    return df


# ==========================================
# 4. 파일 존재 여부 확인
# ==========================================
if not CSV_PATH.exists():

    st.error("temperature.csv 파일을 찾을 수 없습니다.")

    st.info(
        "temperature.csv 파일을 프로젝트의 최상위 폴더에 "
        "넣어주세요."
    )

    st.stop()


# ==========================================
# 5. 데이터 불러오기 오류 처리
# ==========================================
try:
    df = load_data(CSV_PATH)

except Exception as error:

    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {error}")
    st.stop()


if df.empty:
    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()


# ==========================================
# 6. 사용자 입력
# ==========================================
st.divider()
st.subheader("📅 분석 조건 선택")

col1, col2 = st.columns(2)

month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

with col1:

    selected_month = st.selectbox(
        "분석하고 싶은 월을 선택하세요.",
        list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:

    latest_year = int(df["연도"].max())

    forecast_year = st.number_input(
        "예측하고 싶은 연도를 입력하세요.",
        min_value=latest_year + 1,
        max_value=2100,
        value=max(latest_year + 1, 2030),
        step=1
    )

selected_month_name = month_names[selected_month]


# ==========================================
# 7. 선택한 월의 데이터 정리
# ==========================================
month_df = df[
    df["월"] == selected_month
].copy()

month_df = (
    month_df
    .groupby("연도", as_index=False)["평균기온(℃)"]
    .mean()
    .sort_values("연도")
    .reset_index(drop=True)
)

if len(month_df) < 2:

    st.warning(
        "선택한 월의 데이터가 2개 연도 이상 있어야 "
        "선형회귀 분석을 할 수 있습니다."
    )

    st.stop()


# ==========================================
# 8. 선형회귀 알고리즘 계산
# ==========================================
x_values = month_df["연도"].astype(float).tolist()

y_values = month_df["평균기온(℃)"].astype(float).tolist()

# 평균 계산
x_mean = sum(x_values) / len(x_values)
y_mean = sum(y_values) / len(y_values)

# 기울기 계산
numerator = sum(
    (x - x_mean) * (y - y_mean)
    for x, y in zip(x_values, y_values)
)

denominator = sum(
    (x - x_mean) ** 2
    for x in x_values
)

if denominator == 0:

    st.error("선형회귀 계산에 필요한 연도 데이터가 부족합니다.")
    st.stop()

slope = numerator / denominator

# y절편 계산
intercept = y_mean - slope * x_mean

# 미래 기온 예측
predicted_temperature = (
    slope * forecast_year + intercept
)


# ==========================================
# 9. 결정계수 R² 계산
# ==========================================
fitted_values = [
    slope * x + intercept
    for x in x_values
]

ss_res = sum(
    (actual - predicted) ** 2
    for actual, predicted in zip(y_values, fitted_values)
)

ss_tot = sum(
    (actual - y_mean) ** 2
    for actual in y_values
)

if ss_tot != 0:
    r_squared = 1 - (ss_res / ss_tot)
else:
    r_squared = 0


# ==========================================
# 10. 회귀선 데이터 만들기
# ==========================================
start_year = int(month_df["연도"].min())

line_years = list(
    range(start_year, int(forecast_year) + 1)
)

line_temperatures = [
    slope * year + intercept
    for year in line_years
]

line_df = pd.DataFrame({
    "연도": line_years,
    "회귀선 기온": line_temperatures
})


# ==========================================
# 11. 예측 결과 표시
# ==========================================
st.divider()
st.subheader("🔮 미래 기온 예측 결과")

result_col1, result_col2, result_col3 = st.columns(3)

with result_col1:

    st.metric(
        "선택한 월",
        selected_month_name
    )

with result_col2:

    st.metric(
        "예측 연도",
        f"{int(forecast_year)}년"
    )

with result_col3:

    st.metric(
        "예측 평균기온",
        f"{predicted_temperature:.1f}℃"
    )

# ==========================================
# 12. 그래프 그리기
# ==========================================
st.divider()
st.subheader("📊 과거 기온과 미래 예측 그래프")

fig = go.Figure()

# 실제 기온 데이터
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="royalblue",
            size=9
        ),
        hovertemplate=(
            "%{x}년<br>"
            "실제 기온: %{y:.1f}℃"
            "<extra></extra>"
        )
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
            color="orange",
            width=3,
            dash="dash"
        ),
        hovertemplate=(
            "%{x}년<br>"
            "예측 기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

# 미래 예측 지점
fig.add_trace(
    go.Scatter(
        x=[forecast_year],
        y=[predicted_temperature],
        mode="markers",
        name="미래 예측 기온",
        marker=dict(
            color="red",
            size=16,
            symbol="star"
        ),
        hovertemplate=(
            "%{x}년<br>"
            "예측 기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

# 예측 지점 설명
fig.add_annotation(
    x=forecast_year,
    y=predicted_temperature,
    text=(
        f"{int(forecast_year)}년 예측<br>"
        f"{predicted_temperature:.1f}℃"
    ),
    showarrow=True,
    arrowhead=2,
    ax=45,
    ay=-45
)

# 그래프 모양 설정
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
# 13. 선형회귀 알고리즘 설명
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

# 회귀 결과
st.subheader("📐 이번 분석의 선형회귀 계산 결과")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:

    st.metric(
        "기울기 (a)",
        f"{slope:.4f}℃/년"
    )

with info_col2:

    st.metric(
        "y절편 (b)",
        f"{intercept:.2f}"
    )

with info_col3:

    st.metric(
        "결정계수 (R²)",
        f"{r_squared:.3f}"
    )

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

    st.info(
        "과거 데이터에서 뚜렷한 상승 또는 하락 추세가 거의 없습니다."
    )


# ==========================================
# 14. 결정계수 설명
# ==========================================
st.markdown("""
### 📊 결정계수(R²)란?

결정계수는 회귀선이 과거 기온 데이터의 변화를
얼마나 설명하는지 나타내는 값입니다.

- **1에 가까울수록:** 회귀선이 과거 데이터의 변화를 잘 설명합니다.
- **0에 가까울수록:** 직선으로 설명하기 어렵습니다.

단, 결정계수가 높더라도 미래 예측이 반드시 정확하다는 뜻은 아닙니다.

⚠️ 이 프로그램은 과거 기온의 직선 추세가 미래에도 이어진다고 가정합니다.

실제 기온은 기후변화와 자연적 요인 등 다양한 영향을 받으므로
예측 결과는 참고용으로 활용해주세요.
""")


# ==========================================
# 15. 학습 데이터 확인
# ==========================================
with st.expander("📋 선형회귀 학습에 사용한 실제 데이터 확인"):

    display_df = month_df.copy()

    display_df["평균기온(℃)"] = (
        display_df["평균기온(℃)"].round(1)
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 16. 데이터 출처
# ==========================================
st.caption("데이터 출처: temperature.csv")
