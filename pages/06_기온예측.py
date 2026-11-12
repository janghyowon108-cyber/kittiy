
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor


# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="서울 기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 분석 및 예측")

st.markdown("""
과거 서울의 기온 데이터를 이용해 미래의 기온을 예측합니다.

세 가지 회귀 알고리즘을 선택하고 결과를 비교해 보세요!
""")


# ==========================================
# 2. CSV 파일 경로
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
        raise ValueError("CSV 파일 인코딩을 확인해주세요.")

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

    # 평균기온 숫자 변환
    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"],
        errors="coerce"
    )

    # 결측치 제거
    df = df.dropna(
        subset=["일시", "평균기온(℃)"]
    ).copy()

    # 연도와 월 추출
    df["연도"] = df["일시"].dt.year
    df["월"] = df["일시"].dt.month

    return df


# ==========================================
# 4. 파일 확인
# ==========================================
if not CSV_PATH.exists():

    st.error("temperature.csv 파일을 찾을 수 없습니다.")

    st.info(
        "temperature.csv 파일을 프로젝트 최상위 폴더에 "
        "넣어주세요."
    )

    st.stop()


try:

    df = load_data(CSV_PATH)

except Exception as error:

    st.error(f"데이터 불러오기 오류: {error}")
    st.stop()


if df.empty:

    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()


# ==========================================
# 5. 사용자 입력
# ==========================================
st.divider()
st.subheader("📅 분석 조건 선택")

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

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "분석할 월을 선택하세요.",
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
# 6. 회귀 알고리즘 선택
# ==========================================
st.divider()
st.subheader("🤖 예측 알고리즘 선택")

algorithm_names = {
    "선형회귀": "Linear Regression",
    "다항회귀": "Polynomial Regression",
    "랜덤 포레스트 회귀": "Random Forest Regression"
}

selected_algorithm = st.selectbox(
    "사용할 회귀 알고리즘을 선택하세요.",
    list(algorithm_names.keys())
)

st.info(
    f"현재 선택한 알고리즘: {selected_algorithm}"
)


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

if len(month_df) < 3:

    st.warning(
        "회귀 알고리즘을 비교하려면 선택한 월의 "
        "데이터가 최소 3개 연도 이상 필요합니다."
    )

    st.stop()


# ==========================================
# 8. 학습 데이터 준비
# ==========================================
X = month_df[["연도"]].astype(float).values

y = month_df["평균기온(℃)"].astype(float).values

forecast_X = [[float(forecast_year)]]


# ==========================================
# 9. 세 가지 회귀 모델 만들기
# ==========================================

# ① 선형회귀
linear_model = LinearRegression()


# ② 다항회귀
# 2차 다항식으로 곡선 형태를 학습
polynomial_model = make_pipeline(
    PolynomialFeatures(degree=2, include_bias=False),
    LinearRegression()
)


# ③ 랜덤 포레스트 회귀
random_forest_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=3,
    min_samples_leaf=2,
    random_state=42
)


# ==========================================
# 10. 모델 학습
# ==========================================
models = {
    "선형회귀": linear_model,
    "다항회귀": polynomial_model,
    "랜덤 포레스트 회귀": random_forest_model
}

forecast_results = {}
r2_results = {}

for model_name, model in models.items():

    # 과거 기온 데이터로 학습
    model.fit(X, y)

    # 미래 기온 예측
    prediction = model.predict(forecast_X)[0]

    # 결정계수 계산
    r2 = model.score(X, y)

    forecast_results[model_name] = float(prediction)
    r2_results[model_name] = float(r2)


# ==========================================
# 11. 선택한 알고리즘 결과
# ==========================================
selected_model = models[selected_algorithm]

predicted_temperature = forecast_results[selected_algorithm]

r_squared = r2_results[selected_algorithm]


st.divider()
st.subheader("🔮 선택한 알고리즘의 예측 결과")

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
# 12. 선택한 알고리즘의 그래프
# ==========================================
st.divider()
st.subheader(f"📊 {selected_algorithm} 예측 그래프")

start_year = int(month_df["연도"].min())

line_years = list(
    range(start_year, int(forecast_year) + 1)
)

line_X = pd.DataFrame({
    "연도": line_years
})

line_predictions = selected_model.predict(
    line_X[["연도"]].values
)

fig = go.Figure()


# 실제 기온
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


# 선택한 알고리즘의 예측선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_predictions,
        mode="lines",
        name=f"{selected_algorithm} 추세",
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


# 예측값 설명
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


fig.update_layout(
    title=(
        f"{selected_month_name} 연도별 평균기온 및 "
        f"{selected_algorithm} 예측"
    ),
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
    "🟠 주황색 점선: 선택한 알고리즘의 예측선 | "
    "🔴 빨간 별: 미래 예측 기온"
)


# ==========================================
# 13. 세 가지 알고리즘 예측 결과 비교
# ==========================================
st.divider()
st.subheader("⚖️ 세 가지 회귀 알고리즘 결과 비교")

st.markdown(
    f"""
    **{selected_month_name}의 {int(forecast_year)}년 평균기온 예측 결과**입니다.

    알고리즘마다 학습 방식이 다르기 때문에 예측값이 달라질 수 있습니다.
    """
)


comparison_df = pd.DataFrame({
    "알고리즘": list(forecast_results.keys()),
    "예측 평균기온(℃)": list(forecast_results.values()),
    "결정계수(R²)": [
        r2_results[name]
        for name in forecast_results.keys()
    ]
})

comparison_df["예측 평균기온(℃)"] = (
    comparison_df["예측 평균기온(℃)"].round(2)
)

comparison_df["결정계수(R²)"] = (
    comparison_df["결정계수(R²)"].round(3)
)


# 비교 표
st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# 비교 막대그래프
comparison_fig = go.Figure()

comparison_fig.add_trace(
    go.Bar(
        x=list(forecast_results.keys()),
        y=list(forecast_results.values()),
        text=[
            f"{value:.1f}℃"
            for value in forecast_results.values()
        ],
        textposition="outside",
        marker_color=[
            "mediumpurple",
            "skyblue",
            "lightseagreen"
        ],
        name="예측 기온"
    )
)

comparison_fig.update_layout(
    title=f"{int(forecast_year)}년 {selected_month_name} 알고리즘별 예측 기온",
    xaxis_title="회귀 알고리즘",
    yaxis_title="예측 평균기온 (℃)",
    template="plotly_white",
    height=450,
    showlegend=False
)

st.plotly_chart(
    comparison_fig,
    use_container_width=True
)


# ==========================================
# 14. 알고리즘별 설명
# ==========================================
st.divider()
st.subheader("🧠 회귀 알고리즘 알아보기")


if selected_algorithm == "선형회귀":

    st.markdown("""
    ### 📏 선형회귀 (Linear Regression)

    과거 데이터에 가장 잘 맞는 직선을 찾아 미래의 값을 예측합니다.

    **작동 원리**

    1. 연도와 평균기온 데이터를 모읍니다.
    2. 실제 기온과 직선 사이의 오차를 계산합니다.
    3. 오차 제곱합이 작아지도록 기울기와 절편을 찾습니다.
    4. 미래 연도를 직선에 넣어 기온을 예측합니다.

    기본 수식:

    """)
    st.latex(r"y = ax + b")

    st.markdown("""
    - x: 연도
    - y: 예측 평균기온
    - a: 기울기
    - b: y절편

    직선 형태로 기온의 장기적인 상승 또는 하락 추세를 파악하기 좋습니다.
    """)


elif selected_algorithm == "다항회귀":

    st.markdown("""
    ### 📈 다항회귀 (Polynomial Regression)

    선형회귀와 달리 곡선 형태로 데이터의 변화를 학습합니다.

    이번 프로그램에서는 2차 다항회귀를 사용합니다.

    기본 수식:
    """)

    st.latex(r"y = ax^2 + bx + c")

    st.markdown("""
    **작동 원리**

    1. 연도 데이터를 제곱하여 새로운 변수를 만듭니다.
    2. 연도와 연도의 제곱값을 함께 학습합니다.
    3. 과거 기온의 곡선 패턴을 찾습니다.
    4. 미래 연도를 넣어 예측합니다.

    직선으로 설명하기 어려운 곡선 형태의 변화를 표현할 수 있습니다.

    단, 미래로 멀리 예측하면 곡선이 급격하게 변할 수 있습니다.
    """)


elif selected_algorithm == "랜덤 포레스트 회귀":

    st.markdown("""
    ### 🌳 랜덤 포레스트 회귀 (Random Forest Regression)

    여러 개의 의사결정나무를 만들어 예측 결과를 종합하는 알고리즘입니다.

    **작동 원리**

    1. 여러 개의 학습용 데이터 조합을 만듭니다.
    2. 각각의 데이터로 여러 의사결정나무를 학습합니다.
    3. 각 나무가 미래 기온을 예측합니다.
    4. 여러 나무의 예측값을 평균 내어 최종 결과를 만듭니다.

    여러 나무의 결과를 종합하기 때문에 하나의 직선이나 곡선으로
    표현하기 어려운 데이터 패턴도 학습할 수 있습니다.

    단, 현재 프로그램처럼 연도 하나만 입력하는 경우
    학습한 연도 범위를 크게 벗어난 미래 예측에는 한계가 있습니다.
    """)


# ==========================================
# 15. 결정계수 설명
# ==========================================
st.subheader("📐 결정계수(R²)")

st.markdown(f"""
현재 선택한 **{selected_algorithm}**의 결정계수는
**{r_squared:.3f}**입니다.

결정계수는 모델이 학습에 사용한 과거 기온 데이터의 변화를
얼마나 설명하는지 나타내는 지표입니다.

- 1에 가까울수록 과거 데이터에 잘 맞습니다.
- 0에 가까울수록 과거 데이터의 변화를 설명하기 어렵습니다.

⚠️ 결정계수가 높다고 미래 예측이 반드시 정확한 것은 아닙니다.
특히 미래 예측 성능은 과거 데이터 일부를 따로 남겨두고
검증해야 더 정확하게 평가할 수 있습니다.
""")


# ==========================================
# 16. 실제 학습 데이터 확인
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
# 17. 데이터 출처
# ==========================================
st.caption("데이터 출처: temperature.csv")
