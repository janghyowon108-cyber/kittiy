

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌈",
    layout="wide"
)

st.title("🌈 월별 기온분석")
st.markdown("""
원하는 월을 선택하면 연도별 최고기온과 최저기온을
꺾은선 그래프로 비교할 수 있습니다. 🌤️
"")

st.divider()

# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================
# 현재 파이썬 파일은 pages 폴더 안에 있음
# CSV 파일은 pages 폴더의 상위 폴더에 있음

current_dir = Path(__file__).resolve().parent
csv_path = current_dir.parent / "temperature.csv"

# ==========================================
# 3. CSV 파일 불러오기
# ==========================================
@st.cache_data
def load_data(path):
    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    for encoding in encodings:
        try:
            return pd.read_csv(
                path,
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 한글 인코딩을 확인해 주세요.")

if not csv_path.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.write("찾으려는 경로:", str(csv_path))
    st.info(
        "CSV 파일이 프로젝트 최상위 폴더에 있는지 확인해 주세요."
    )
    st.stop()

try:
    df = load_data(str(csv_path))
except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
    st.stop()

# ==========================================
# 4. 데이터 열 확인
# ==========================================
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
    st.error(f"CSV 파일에 필요한 열이 없습니다: {missing_columns}")
    st.stop()

# ==========================================
# 5. 날짜 데이터 전처리
# ==========================================
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

def convert_date(value):
    try:
        month_text, year_text = str(value).strip().split("-")
        month = month_map[month_text.title()]
        year = int(year_text)

        return month, year

    except (ValueError, KeyError):
        return None, None

dates = df["일시"].apply(convert_date)

df["월"] = [item[0] for item in dates]
year_suffix = [item[1] for item in dates]

# 1907~2026년 날짜 변환
years = []
century = 1900
previous = None

for y in year_suffix:
    if y is None:
        years.append(None)
        continue

    if y >= 1000:
        year = y
    else:
        if previous is not None and y < previous:
            century += 100

        year = century + y
        previous = y

    years.append(year)

df["연도"] = years

# 기온 숫자 변환
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

df = df.sort_values("연도")

# ==========================================
# 6. 사이드바 월 선택
# ==========================================
st.sidebar.header("📅 분석 조건")

selected_month = st.sidebar.selectbox(
    "분석할 월을 선택하세요.",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월",
    index=0
)

st.sidebar.success(
    f"선택한 월: {selected_month}월"
)

# ==========================================
# 7. 선택한 월 데이터 추출
# ==========================================
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

month_df = month_df.dropna(
    subset=["최고기온(℃)", "최저기온(℃)"],
    how="all"
)

if month_df.empty:
    st.warning("선택한 월에 데이터가 없습니다.")
    st.stop()

# ==========================================
# 8. 요약 통계
# ==========================================
st.subheader("📌 기온 분석 요약")

col1, col2, col3 = st.columns(3)

avg_high = month_df["최고기온(℃)"].mean()
avg_low = month_df["최저기온(℃)"].mean()

max_high = month_df["최고기온(℃)"].max()
min_low = month_df["최저기온(℃)"].min()

col1.metric(
    "평균 최고기온",
    f"{avg_high:.1f}℃" if pd.notna(avg_high) else "-"
)

col2.metric(
    "평균 최저기온",
    f"{avg_low:.1f}℃" if pd.notna(avg_low) else "-"
)

col3.metric(
    "분석 연도 수",
    f"{len(month_df)}개"
)

st.divider()

# ==========================================
# 9. 색상 그라데이션 설정
# ==========================================
n = len(month_df)

positions = (
    [0.5] if n == 1
    else [i / (n - 1) for i in range(n)]
)

# 최고기온: 무지개 색상
rainbow_colors = pc.sample_colorscale(
    "Rainbow",
    positions
)

# 최저기온: 천상색
heaven_colors = pc.sample_colorscale(
    [
        [0.0, "#E0F7FF"],
        [0.2, "#B8E7FF"],
        [0.4, "#91D8FF"],
        [0.6, "#72C8F0"],
        [0.8, "#54B8E0"],
        [1.0, "#3999D0"]
    ],
    positions
)

# ==========================================
# 10. 그래프 생성
# ==========================================
fig = go.Figure()

x = month_df["연도"].tolist()
high = month_df["최고기온(℃)"].tolist()
low = month_df["최저기온(℃)"].tolist()

# 최고기온 선
for i in range(n - 1):
    if pd.notna(high[i]) and pd.notna(high[i + 1]):
        fig.add_trace(
            go.Scatter(
                x=x[i:i+2],
                y=high[i:i+2],
                mode="lines",
                line=dict(
                    color=rainbow_colors[i],
                    width=3
                ),
                showlegend=False,
                hoverinfo="skip"
            )
        )

# 최고기온 범례
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="lines+markers",
        name="최고기온 🌈",
        line=dict(color="#FF7043", width=3)
    )
)

# 최고기온 점
fig.add_trace(
    go.Scatter(
        x=x,
        y=high,
        mode="markers",
        marker=dict(
            color=rainbow_colors,
            size=7
        ),
        name="최고기온 데이터",
        showlegend=False,
        hovertemplate=(
            "연도: %{x}년<br>"
            "최고기온: %{y}℃"
            "<extra></extra>"
        )
    )
)

# 최저기온 선
for i in range(n - 1):
    if pd.notna(low[i]) and pd.notna(low[i + 1]):
        fig.add_trace(
            go.Scatter(
                x=x[i:i+2],
                y=low[i:i+2],
                mode="lines",
                line=dict(
                    color=heaven_colors[i],
                    width=3
                ),
                showlegend=False,
                hoverinfo="skip"
            )
        )

# 최저기온 범례
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="lines+markers",
        name="최저기온 ☁️",
        line=dict(color="#54B8E0", width=3)
    )
)

# 최저기온 점
fig.add_trace(
    go.Scatter(
        x=x,
        y=low,
        mode="markers",
        marker=dict(
            color=heaven_colors,
            size=7
        ),
        name="최저기온 데이터",
        showlegend=False,
        hovertemplate=(
            "연도: %{x}년<br>"
            "최저기온: %{y}℃"
            "<extra></extra>"
        )
    )
)

# ==========================================
# 11. 그래프 디자인
# ==========================================
fig.update_layout(
    title=dict(
        text="월별 기온분석",
        x=0.5,
        xanchor="center",
        font=dict(size=26)
    ),

    xaxis=dict(
        title="연도",
        tickmode="linear",
        dtick=10,
        showgrid=True
    ),

    yaxis=dict(
        title="온도 (℃)",
        showgrid=True
    ),

    legend=dict(
        title="범례",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),

    hovermode="x unified",
    template="plotly_white",
    height=600
)

# ==========================================
# 12. 그래프 화면 출력
# ==========================================
st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# 13. 데이터 표
# ==========================================
st.divider()

st.subheader(
    f"📋 {selected_month}월 연도별 기온 데이터"
)

display_df = month_df[
    ["연도", "최고기온(℃)", "최저기온(℃)"]
].copy()

display_df["연도"] = (
    display_df["연도"].astype(str) + "년"
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 14. CSV 다운로드
# ==========================================
download_df = month_df[
    ["연도", "월", "최고기온(℃)", "최저기온(℃)"]
].copy()

csv_data = download_df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 분석 결과 다운로드",
    data=csv_data,
    file_name=f"{selected_month}월_기온분석.csv",
    mime="text/csv"
)

# ==========================================
# 15. 마무리
# ==========================================
st.divider()

st.markdown("""
### 🌈 월별 기온분석 완료!

- 최고기온: 무지개 색상
- 최저기온: 천상색 계열
- 가로축: 연도
- 세로축: 온도(℃)
- 범례: 최고기온 / 최저기온

원하는 월을 바꾸면 그래프가 자동으로 변경됩니다.
""")
