
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

# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

# 현재 파일은 pages 폴더 안에 있음
PAGE_DIR = Path(__file__).resolve().parent

# 상위 폴더로 이동
BASE_DIR = PAGE_DIR.parent

# CSV 파일은 상위 폴더에 있음
DATA_FILE = BASE_DIR / "countriesMBTI_16types (1).csv"


# ==========================================
# 3. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data(file_path):

    df = pd.read_csv(file_path)

    # 열 이름 정리
    df.columns = df.columns.str.strip()

    # 국가 이름 정리
    df["Country"] = df["Country"].astype(str).str.strip()

    # MBTI 열 추출
    mbti_columns = [
        col for col in df.columns
        if col != "Country"
    ]

    # MBTI 유형 16개 확인
    if len(mbti_columns) != 16:
        raise ValueError(
            f"MBTI 유형이 16개가 아닙니다. 현재 {len(mbti_columns)}개입니다."
        )

    # 숫자 데이터 변환
    for col in mbti_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 결측치 확인
    if df[mbti_columns].isna().any().any():
        raise ValueError(
            "MBTI 데이터에 비어 있는 값이 있습니다."
        )

    # 중복 국가 제거
    df = df.drop_duplicates(
        subset=["Country"]
    )

    # 국가 이름순 정렬
    df = df.sort_values(
        "Country"
    ).reset_index(drop=True)

    return df, mbti_columns


# ==========================================
# 4. CSV 파일 존재 여부 확인
# ==========================================

if not DATA_FILE.exists():

    st.error("❌ CSV 파일을 찾을 수 없습니다.")

    st.write("현재 파이썬 파일 위치:")
    st.code(str(PAGE_DIR))

    st.write("CSV 파일을 찾는 위치:")
    st.code(str(DATA_FILE))

    st.write("상위 폴더의 파일 목록:")

    for file in BASE_DIR.iterdir():
        st.write("📁", file.name)

    st.warning(
        "CSV 파일을 pages 폴더의 상위 폴더에 넣어주세요."
    )

    st.stop()


# ==========================================
# 5. 데이터 불러오기
# ==========================================

try:

    df, mbti_columns = load_data(str(DATA_FILE))

except Exception as e:

    st.error(f"데이터를 불러오는 중 오류 발생: {e}")
    st.stop()


# ==========================================
# 6. 화면 디자인
# ==========================================

st.markdown("""
<style>

.main-title {
    font-size: 36px;
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
# 7. 제목
# ==========================================

st.markdown(
    '<div class="main-title">🌍 세계 국가별 MBTI 탐험</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '세계 여러 나라의 MBTI 유형별 비율을 비교해 보세요!'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# 8. 국가 선택
# ==========================================

countries = df["Country"].tolist()

# 한국을 기본 선택 국가로 설정
default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "🗺️ 분석할 국가를 선택하세요!",
    options=countries,
    index=default_index
)


# ==========================================
# 9. 선택 국가 데이터 분석
# ==========================================

country_data = df[
    df["Country"] == selected_country
].iloc[0]

result = pd.DataFrame({

    "MBTI": mbti_columns,

    "비율": [
        float(country_data[mbti]) * 100
        for mbti in mbti_columns
    ]

})

# 높은 비율부터 정렬
result = result.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)


# ==========================================
# 10. 그래프 색상 설정
# ==========================================

colors = [

    "#8B5CF6",  # 1위 보라색

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

result["색상"] = colors[:len(result)]

# 1위 MBTI
top_mbti = result.iloc[0]["MBTI"]

# 1위 비율
top_rate = result.iloc[0]["비율"]


# ==========================================
# 11. 주요 정보 표시
# ==========================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "🌍 선택 국가",
    selected_country
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
# 12. MBTI 막대그래프
# ==========================================

st.subheader(
    f"📊 {selected_country}의 MBTI 비율"
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
            color=result["색상"],
            line=dict(
                color="white",
                width=1
            )
        ),

        text=[
            f"{value:.2f}%"
            for value in result["비율"]
        ],

        textposition="outside",

        cliponaxis=False,

        hovertemplate=
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"

    )

)


# 그래프 디자인
fig.update_layout(

    height=650,

    plot_bgcolor="white",

    paper_bgcolor="white",

    xaxis=dict(

        title="MBTI 비율 (%)",

        rangemode="tozero",

        showgrid=True,

        gridcolor="#EAF2F8",

        zeroline=False

    ),

    yaxis=dict(

        title="MBTI 유형",

        autorange="reversed",

        tickfont=dict(
            size=13,
            color="#334155"
        )

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


# Streamlit 화면에 그래프 표시
st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 13. MBTI 순위표
# ==========================================

with st.expander("📋 16가지 MBTI 전체 순위 확인하기"):

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
# 14. 하단 안내
# ==========================================

st.divider()

st.info(
    "💡 국가를 변경하면 해당 국가의 MBTI 비율 그래프가 자동으로 변경됩니다."
)

st.caption(
    "※ 본 자료는 제공된 CSV 데이터를 바탕으로 합니다. "
    "실제 국민 전체의 MBTI 분포를 의미하지는 않습니다."
)

st.markdown(
    "<center>🌈 세계인의 다양한 성격을 탐험해 보세요!</center>",
    unsafe_allow_html=True
)
