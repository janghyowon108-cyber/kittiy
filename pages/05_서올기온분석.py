

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from pathlib import Path

# =========================================
# 1. 페이지 설정
# =========================================
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌈",
    layout="wide"
)

st.title("🌈 월별 기온분석")
st.write("월을 선택하면 연도별 최고기온과 최저기온을 확인할 수 있어요!")

# =========================================
# 2. CSV 파일 경로
# CSV는 프로젝트 최상위 폴더에 있음
# PY 파일은 pages 폴더 안에 있음
# =========================================
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "temperature.csv"

# =========================================
# 3. CSV 파일 불러오기
# =========================================
@st.cache_data
def load_data(file_path):
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

if not CSV_PATH.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.write("찾는 위치:", str(CSV_PATH))
    st.stop()

try:
    df = load_data(str(CSV_PATH))
except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# =========================================
# 4. 필요한 열 확인
# =========================================
required_columns = [
    "일시",
    "최고기온(℃)",
    "최저기온(℃)"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error("CSV 파일에 필요한 열이 없습니다.")
    st.write("없는 열:", missing_columns)
    st.write("현재 CSV 열 이름:", df.columns.tolist())
    st.stop()

# =========================================
# 5. 날짜에서 월과 연도 추출
# 예: Oct-07 → 1907년 10월
# =========================================
month_map = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

def parse_date(value):
    try:
        month_text, year_text = str(value).strip().split("-")

        month = month_map[month_text.title()]
        year = int(year_text)

        return month, year

    except (ValueError, KeyError, AttributeError):
        return None, None

parsed_dates = df["일시"].apply(parse_date)

df["월"] = parsed_dates.apply(lambda x: x[0])
year_values = parsed_dates.apply(lambda x: x[1])

# =========================================
# 6. 두 자리 연도를 네 자리 연도로 변환
# 1907~1999 → 2000~2026
# =========================================
years = []
century = 1900
previous_year = None

for value in year_values:
    if pd.isna(value):
        years.append(None)
        continue

    value = int(value)

    if value >= 1000:
        full_year = value
    else:
        if (
            previous_year is not None
            and value < previous_year
        ):
            century += 100

        full_year = century + value
        previous_year = value

    years.append(full_year)

df["연도"] = years

# =========================================
# 7. 기온 데이터 숫자로 변환
# =========================================
df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"],
    errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=["월", "연도"]
).copy()

df["월"] = df["월"].astype(int)
df["연도"] = df["연도"].astype(int)

# =========================================
# 8. 월 선택 메뉴
# =========================================
st.sidebar.header("📅 월 선택")

selected_month = st.sidebar.selectbox(
    "분석할 월을 선택하세요.",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월"
)

# =========================================
# 9. 선택한 월의 데이터 가져오기
# =========================================
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if month_df.empty:
    st.warning("선택한 월의 데이터가 없습니다.")
    st.stop()

# =========================================
# 10. 그래프 생성
# =========================================
fig = go.Figure()

# -----------------------------------------
# 최고기온: 무지개색 선
# -----------------------------------------
valid_max = month_df.dropna(
    subset=["최고기온(℃)"]
).sort_values("연도")

x_values = valid_max["연도"].tolist()
y_values = valid_max["최고기온(℃)"].tolist()

segment_count = max(len(x_values) - 1, 1)

rainbow_colors = sample_colorscale(
    "Rainbow",
    [
        i / max(segment_count - 1, 1)
        for i in range(segment_count)
    ]
)

if len(x_values) == 1:
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines+markers",
            name="최고기온",
            line=dict(color=rainbow_colors[0], width=3),
            marker=dict(color=rainbow_colors[0], size=9)
        )
    )

else:
    for i in range(len(x_values) - 1):
        fig.add_trace(
            go.Scatter(
                x=[x_values[i], x_values[i + 1]],
                y=[y_values[i], y_values[i + 1]],
                mode="lines",
                name="최고기온",
                legendgroup="최고기온",
                showlegend=(i == 0),
                line=dict(
                    color=rainbow_colors[i],
                    width=3
                ),
                hovertemplate=(
                    "연도: %{x}년<br>"
                    "최고기온: %{y}℃<extra></extra>"
                )
            )
        )

    # 최고기온 점 표시
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="markers",
            name="최고기온 점",
            showlegend=False,
            marker=dict(
                color=rainbow_colors[
                    :len(x_values)
                ] if len(rainbow_colors) >= len(x_values)
                else rainbow_colors + [rainbow_colors[-1]],
                size=8
            ),
            hovertemplate=(
                "연도: %{x}년<br>"
                "최고기온: %{y}℃<extra></extra>"
            )
        )
    )

# -----------------------------------------
# 최저기온: 천상색 선
# -----------------------------------------
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(
            color="#54B8E0",
            width=3
        ),
        marker=dict(
            color="#A7E6FF",
            size=8
        ),
        connectgaps=False,
        hovertemplate=(
            "연도: %{x}년<br>"
            "최저기온: %{y}℃<extra></extra>"
        )
    )
)

# =========================================
# 11. 그래프 디자인
# =========================================
fig.update_layout(
    title={
        "text": "월별 기온분석",
        "x": 0.5,
        "xanchor": "center"
    },
    xaxis_title="연도",
    yaxis_title="온도 (℃)",
    legend_title="기온 범례",
    hovermode="x unified",
    template="plotly_white",
    height=600
)

fig.update_xaxes(
    showgrid=True,
    dtick=10
)

fig.update_yaxes(
    showgrid=True,
    zeroline=True
)

# =========================================
# 12. 그래프 화면에 출력
# =========================================
st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================
# 13. 데이터 표 출력
# =========================================
st.subheader(f"📊 {selected_month}월 기온 데이터")

display_df = month_df[
    ["연도", "최고기온(℃)", "최저기온(℃)"]
].copy()

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# =========================================
# 14. CSV 다운로드
# =========================================
csv_data = display_df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 기온 데이터 다운로드",
    data=csv_data,
    file_name=f"{selected_month}월_기온분석.csv",
    mime="text/csv"
)

st.success("기온 분석이 완료되었습니다! 🌈")
