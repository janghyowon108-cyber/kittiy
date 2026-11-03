
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 기본 설정
# ==========================================
st.set_page_config(
    page_title="세계 국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

DATA_FILE = Path(__file__).parent / "countriesMBTI_16types (1).csv"

# 1위는 보라색, 나머지는 하늘색 그라데이션
COLORS = [
    "#8B5CF6",
    "#78CFFF",
    "#83D4FF",
    "#8ED9FF",
    "#99DEFF",
    "#A4E3FF",
    "#AFE8FF",
    "#BAEDFF",
    "#C5F0FF",
    "#CFF3FF",
    "#D8F5FF",
    "#DFF7FF",
    "#E5F9FF",
    "#EAFBFF",
    "#F0FCFF",
    "#F5FDFF"
]

# ==========================================
# 2. 데이터 불러오기
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)

    df.columns = df.columns.str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()

    mbti_columns = [
        col for col in df.columns if col != "Country"
    ]

    if len(mbti_columns) != 16:
        raise ValueError("MBTI 데이터 열이 16개가 아닙니다.")

    for col in mbti_columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    if df[mbti_columns].isna().any().any():
        raise ValueError("MBTI 데이터에 잘못된 값이 있습니다.")

    df = df.drop_duplicates(
        subset=["Country"]
    )

    return df.sort_values("Country"), mbti_columns


# ==========================================
# 3. 화면 디자인
# ==========================================
st.markdown("""
<style>
.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #334155;
    margin-bottom: 5px;
}

.sub-title {
    font-size: 16px;
    color: #64748b;
    margin-bottom: 25px;
}

div[data-testid="stMetric"] {
    background-color: #F5FAFF;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #E0F0FF;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 4. 제목
# ==========================================
st.markdown(
    '<div class="main-title">🌍 세계 국가별 MBTI 탐험</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">국가별 MBTI 성격 유형을 그래프로 비교해 보세요!</div>',
    unsafe_allow_html=True
)


# ==========================================
# 5. CSV 파일 확인 및 데이터 로딩
# ==========================================
if not DATA_FILE.exists():
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "app.py와 CSV 파일을 같은 폴더에 넣어주세요."
    )
    st.stop()

try:
    df, mbti_columns = load_data()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# ==========================================
# 6. 국가 선택
# ==========================================
countries = df["Country"].tolist()

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

country = st.selectbox(
    "🗺️ 국가를 선택하세요!",
    countries,
    index=default_index
)


# ==========================================
# 7. 선택한 국가 데이터 분석
# ==========================================
country_data = df[
    df["Country"] == country
].iloc[0]

result = pd.DataFrame({
    "MBTI": mbti_columns,
    "비율": [
        country_data[mbti] * 100
        for mbti in mbti_columns
    ]
})

# 높은 비율부터 정렬
result = result.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)

# 순위별 색상 지정
result["색상"] = COLORS[:len(result)]

# 1위 정보
top_mbti = result.iloc[0]["MBTI"]
top_rate = result.iloc[0]["비율"]


# ==========================================
# 8. 주요 정보 표시
# ==========================================
col1, col2, col3 = st.columns(3)

col1.metric(
    "🌍 선택 국가",
    country
)

col2.metric(
    "🏆 MBTI 1위",
    top_mbti
)

col3.metric(
    "📊 1위 비율",
    f"{top_rate:.2f}%"
)


st.divider()


# ==========================================
# 9. MBTI 막대그래프
# ==========================================
st.subheader(
    f"📊 {country}의 MBTI 비율"
)

st.caption(
    "🥇 1위는 보라색 / 나머지는 하늘색 그라데이션"
)

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=result["비율"],
        y=result["MBTI"],
        orientation="h",

        marker=dict(
            color=result["색상"]
        ),

        text=[
            f"{v:.2f}%"
            for v in result["비율"]
        ],

        textposition="outside",

        hovertemplate=(
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    height=650,

    plot_bgcolor="white",
    paper_bgcolor="white",

    xaxis=dict(
        title="MBTI 비율 (%)",
        rangemode="tozero",
        showgrid=True,
        gridcolor="#EAF2F8"
    ),

    yaxis=dict(
        title="MBTI 유형",
        autorange="reversed"
    ),

    margin=dict(
        l=40,
        r=80,
        t=30,
        b=40
    ),

    showlegend=False,

    bargap=0.3
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 10. MBTI 순위표
# ==========================================
with st.expander("📋 MBTI 전체 순위 확인하기"):

    ranking = result[
        ["MBTI", "비율"]
    ].copy()

    ranking.insert(
        0,
        "순위",
        range(1, 17)
    )

    ranking["비율"] = ranking["비율"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 11. 안내 문구
# ==========================================
st.divider()

st.caption(
    "※ 본 서비스는 제공된 CSV 데이터를 시각화합니다. "
    "실제 국민 전체의 MBTI 분포를 의미하지는 않습니다."
)

st.markdown(
    "<center>🌈 나와 비슷한 성격을 가진 세계인은 누구일까요?</center>",
    unsafe_allow_html=True
)
