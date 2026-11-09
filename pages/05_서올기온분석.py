
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌈",
    layout="wide"
)

st.title("🌈 월별 기온분석")
st.write("월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요!")

# =====================================
# 2. CSV 파일 경로
# =====================================
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "temperature.csv"

# =====================================
# 3. CSV 불러오기
# =====================================
@st.cache_data
def load_data():
    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(
                CSV_PATH,
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일 인코딩을 확인해 주세요.")

if not CSV_PATH.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.write("파일 위치:", str(CSV_PATH))
    st.stop()

try:
    df = load_data()
except Exception as e:
    st.error(f"파일 오류: {e}")
    st.stop()

# =====================================
# 4. 필수 열 확인
# =====================================
required = [
    "일시",
    "최고기온(℃)",
    "최저기온(℃)"
]

if not all(col in df.columns for col in required):
    st.error("CSV 파일의 열 이름이 올바르지 않습니다.")
    st.write("현재 열 이름:", df.columns.tolist())
    st.stop()

# =====================================
# 5. 날짜 변환
# =====================================
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

def parse_date(value):
    try:
        month_text, year_text = str(value).strip().split("-")
        month = month_map[month_text.title()]
        year_num = int(year_text)

        return month, year_num

    except (ValueError, KeyError):
        return None, None

parsed = df["일시"].apply(parse_date)

df["월"] = parsed.apply(lambda x: x[0])
year_values = parsed.apply(lambda x: x[1])

# 연도 변환: 1907~1999, 2000~2026
years = []
century = 1900
previous = None

for value in year_values:
    if value is None:
        years.append(None)
        continue

    if value >= 1000:
        year = value
    else:
        if previous is not None and value < previous:
            century += 100

        year = century + value
        previous = value

    years.append(year)

df["연도"] = years

# =====================================
# 6. 기온 숫자 변환
# =====================================
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

# =====================================
# 7. 월 선택
# =====================================
st.sidebar.header("📅 월 선택")

selected_month = st.sidebar.selectbox(
    "분석할 월을 선택하세요.",
    list(range(1, 13)),
    format_func=lambda x: str(x) + "월"
)

# =====================================
# 8. 선택 월 데이터
# =====================================
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if month_df.empty:
    st.warning("선택한 월의 데이터가 없습니다.")
    st.stop()

# =====================================
# 9. 그래프 생성
# =====================================
fig = go.Figure()

# 최고기온: 무지개색
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(
            color="red",
            width=3,
            colorscale="Rainbow"
        ),
        marker=dict(
            color=month_df["연도"],
            colorscale="Rainbow",
            size=8,
            showscale=False
        ),
        connectgaps=False
    )
)

# 최저기온: 천상색
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
        connectgaps=False
    )
)

# =====================================
# 10. 그래프 디자인
# =====================================
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

# =====================================
# 11. 그래프 출력
# =====================================
st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================
# 12. 데이터 표
# =====================================
st.subheader(f"📊 {selected_month}월 기온 데이터")

display_df = month_df[
    ["연도", "최고기온(℃)", "최저기온(℃)"]
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# =====================================
# 13. CSV 다운로드
# =====================================
csv_data = display_df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 CSV 다운로드",
    data=csv_data,
    file_name=f"{selected_month}월_기온분석.csv",
    mime="text/csv"
)

st.success("기온 데이터 분석이 완료되었습니다! 🌈")
