
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
st.markdown(
    "원하는 월을 선택하여 연도별 최고기온과 "
    "최저기온의 변화를 비교해 보세요! 🌤️"
)

st.divider()

# ==========================================
# 2. CSV 파일 불러오기
# ==========================================
@st.cache_data
def load_data():
    current = Path(__file__).resolve().parent

    paths = [
        current / "temperature.csv",
        current.parent / "temperature.csv"
    ]

    file_path = next(
        (p for p in paths if p.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다."
        )

    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해 주세요.")

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 불러오기 실패: {e}")
    st.stop()

# ==========================================
# 3. 데이터 전처리
# ==========================================
required_columns = [
    "일시",
    "최고기온(℃)",
    "최저기온(℃)"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

def convert_date(value):
    global_dummy = None

    try:
        month_text, year_text = str(value).strip().split("-")

        month = month_map[month_text.title()]
        year_num = int(year_text)

        return month, year_num

    except (ValueError, KeyError):
        return None, None

dates = df["일시"].apply(convert_date)

df["월"] = [x[0] for x in dates]
year_suffix = [x[1] for x in dates]

# 1907년부터 2026년까지의 연도 변환
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

# 숫자형 변환
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

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

# ==========================================
# 4. 월 선택
# ==========================================
st.sidebar.header("📅 분석 조건")

selected_month = st.sidebar.selectbox(
    "분석할 월을 선택하세요.",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월",
    index=0
)

st.sidebar.success(
    f"현재 선택: {selected_month}월"
)

# ==========================================
# 5. 선택 월 데이터 추출
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
# 6. 요약 통계
# ==========================================
col1, col2, col3 = st.columns(3)

col1.metric(
    "분석 월",
    f"{selected_month}월"
)

col2.metric(
    "평균 최고기온",
    f"{month_df['최고기온(℃)'].mean():.1f}℃"
)

col3.metric(
    "평균 최저기온",
    f"{month_df['최저기온(℃)'].mean():.1f}℃"
)

st.divider()

# ==========================================
# 7. 무지개 / 천상색 그라데이션
# ==========================================
n = len(month_df)

if n <= 1:
    positions = [0.5]
else:
    positions = [i / (n - 1) for i in range(n)]

# 최고기온: 무지개 색상
rainbow_colors = pc.sample_colorscale(
    "Rainbow",
    positions
)

# 최저기온: 천상색 (하늘색 계열)
heaven_colors = pc.sample_colorscale(
    [
        [0.0, "#DFF6FF"],
        [0.2, "#B8E7FF"],
        [0.4, "#91D8FF"],
        [0.6, "#72C8F0"],
        [0.8, "#54B8E0"],
        [1.0, "#3999D0"]
    ],
    positions
)

# ==========================================
# 8. 그래프 생성
# ==========================================
fig = go.Figure()

x = month_df["연도"].tolist()
high = month_df["최고기온(℃)"].tolist()
low = month_df["최저기온(℃)"].tolist()

# 최고기온 무지개 선
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

# 최고기온 범례용 선
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="lines+markers",
        name="최고기온 🌈",
        line=dict(
            color="#FF7043",
            width=3
        ),
        marker=dict(color="#FF7043")
    )
)

# 최고기온 데이터 점
fig.add_trace(
    go.Scatter(
        x=x,
        y=high,
        mode="markers",
        marker=dict(
            color=rainbow_colors,
            size=7,
            line=dict(width=1, color="white")
        ),
        showlegend=False,
        name="최고기온 데이터",
        hovertemplate=(
            "연도: %{x}년<br>"
            "최고기온: %{y}℃"
            "<extra></extra>"
        )
    )
)

# 최저기온 천상색 선
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

# 최저기온 범례용 선
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="lines+markers",
        name="최저기온 ☁️",
        line=dict(
            color="#54B8E0",
            width=3
        ),
        marker=dict(color="#54B8E0")
    )
)

# 최저기온 데이터 점
fig.add_trace(
    go.Scatter(
        x=x,
        y=low,
        mode="markers",
        marker=dict(
            color=heaven_colors,
            size=7,
            line=dict(width=1, color="white")
        ),
        showlegend=False,
        name="최저기온 데이터",
        hovertemplate=(
            "연도: %{x}년<br>"
            "최저기온: %{y}℃"
            "<extra></extra>"
        )
    )
)

# ==========================================
# 9. 그래프 디자인
# ==========================================
fig.update_layout(
    title=dict(
        text=f"{selected_month}월별 기온분석",
        x=0.5,
        xanchor="center",
        font=dict(size=25)
    ),

    xaxis=dict(
        title="연도",
        tickmode="linear",
        dtick=10,
        showgrid=True,
        zeroline=False
    ),

    yaxis=dict(
        title="온도 (℃)",
        showgrid=True,
        zeroline=True
    ),

    legend=dict(
        title="기온 범례",
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
# 10. 그래프 출력
# ==========================================
st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# 11. 데이터 표 출력
# ==========================================
st.divider()

st.subheader(f"📋 {selected_month}월 연도별 기온 데이터")

display_df = month_df[
    ["연도", "최고기온(℃)", "최저기온(℃)"]
].copy()

display_df["연도"] = display_df["연도"].astype(str) + "년"

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 12. 다운로드
# ==========================================
csv = month_df[
    ["연도", "월", "최고기온(℃)", "최저기온(℃)"]
].to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    "📥 선택 월 데이터 다운로드",
    data=csv,
    file_name=f"{selected_month}월_기온분석.csv",
    mime="text/csv"
)

st.divider()

st.caption(
    "🌈 Pandas와 Plotly를 활용한 월별 기온 분석 대시보드"
)
