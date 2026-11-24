import streamlit as st
import pandas as pd
import plotly.express as px
import random
import re
from pathlib import Path

# =========================================================
# 1. 페이지 설정
# =========================================================
st.set_page_config(
    page_title="빵집 탐험대 🥐",
    page_icon="🥐",
    layout="wide"
)

# =========================================================
# 2. 데이터 불러오기
# CSV 파일은 pages 폴더의 상위 폴더에 위치
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "식품_제과점영업 (1).csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV_PATH, encoding="cp949", low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", low_memory=False)

    # 날짜 변환
    df["인허가일자"] = pd.to_datetime(
        df["인허가일자"], errors="coerce"
    )

    df["폐업일자"] = pd.to_datetime(
        df["폐업일자"], errors="coerce"
    )

    # 면적 숫자로 변환
    df["소재지면적"] = pd.to_numeric(
        df["소재지면적"], errors="coerce"
    )

    # 서울 구 이름 추출
    address = df["도로명주소"].fillna("")

    districts = [
        "종로구", "중구", "용산구", "성동구", "광진구",
        "동대문구", "중랑구", "성북구", "강북구", "도봉구",
        "노원구", "은평구", "서대문구", "마포구", "양천구",
        "강서구", "구로구", "금천구", "영등포구", "동작구",
        "관악구", "서초구", "강남구", "송파구", "강동구"
    ]

    def extract_district(addr):
        for district in districts:
            if district in addr:
                return district
        return "기타 지역"

    df["지역"] = address.apply(extract_district)

    # 영업 상태 정리
    df["상태"] = df["영업상태명"].fillna("정보 없음")

    df["영업여부"] = df["상태"].apply(
        lambda x: "영업 중" if "영업" in str(x) else "폐업"
    )

    # 인허가 연도
    df["인허가연도"] = df["인허가일자"].dt.year

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info(
        "식품_제과점영업 (1).csv 파일을 프로젝트 상위 폴더에 넣어주세요."
    )
    st.stop()


# =========================================================
# 3. 제목 및 소개
# =========================================================
st.title("🥐 빵집 탐험대")
st.subheader("서울의 빵집 데이터를 탐험해 보자!")

st.markdown("""
빵집 데이터를 분석하면서 서울에서 빵집이 많은 지역,
영업 중인 빵집, 폐업한 빵집, 새로운 빵집의 탄생까지 알아보자!
""")

st.divider()


# =========================================================
# 4. 전체 통계
# =========================================================
total_count = len(df)

active_count = len(
    df[df["영업여부"] == "영업 중"]
)

closed_count = len(
    df[df["영업여부"] == "폐업"]
)

active_rate = (
    active_count / total_count * 100
    if total_count > 0 else 0
)

closed_rate = (
    closed_count / total_count * 100
    if total_count > 0 else 0
)


# =========================================================
# 5. 재미있는 레벨 시스템
# =========================================================
st.header("🎮 빵집 탐험 레벨")

st.markdown("""
오늘의 탐험 미션은 서울의 빵집 데이터를 분석하는 것!
데이터를 확인하면서 빵집 탐험가가 되어 보자.
""")

level = min(total_count // 10000 + 1, 10)

st.progress(level / 10)

st.success(f"🥐 빵집 탐험가 레벨 {level}")

st.caption(
    f"현재 {total_count:,}개의 빵집 데이터를 탐험하고 있어!"
)

st.divider()


# =========================================================
# 6. 핵심 통계 카드
# =========================================================
st.header("📊 서울 빵집 현황")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "전체 빵집 데이터",
    f"{total_count:,}개"
)

col2.metric(
    "영업 중",
    f"{active_count:,}개",
    f"{active_rate:.1f}%"
)

col3.metric(
    "폐업",
    f"{closed_count:,}개",
    f"{closed_rate:.1f}%"
)

col4.metric(
    "분석 가능한 지역",
    f"{df['지역'].nunique()}개"
)

st.divider()


# =========================================================
# 7. 빵집 영업 상태 원형 그래프
# =========================================================
st.header("🥐 빵집 영업 상태")

status_df = pd.DataFrame({
    "상태": ["영업 중", "폐업"],
    "매장 수": [active_count, closed_count]
})

fig_status = px.pie(
    status_df,
    names="상태",
    values="매장 수",
    title="서울 제과점 영업 상태",
    hole=0.45,
    color="상태",
    color_discrete_map={
        "영업 중": "#FFB347",
        "폐업": "#B0B0B0"
    }
)

fig_status.update_traces(
    textinfo="label+percent",
    textposition="inside"
)

st.plotly_chart(
    fig_status,
    use_container_width=True
)

st.info(
    "💡 이 데이터는 과거 폐업한 매장도 포함한 누적 데이터이므로 "
    "현재 서울의 실제 빵집 수와는 다를 수 있어."
)


# =========================================================
# 8. 지역별 빵집 랭킹
# =========================================================
st.header("🏆 빵집이 가장 많은 지역 TOP 10")

district_df = df[
    df["지역"] != "기타 지역"
]

district_counts = (
    district_df.groupby("지역")
    .size()
    .reset_index(name="매장 수")
    .sort_values("매장 수", ascending=False)
)

top10 = district_counts.head(10)

fig_top10 = px.bar(
    top10,
    x="지역",
    y="매장 수",
    text="매장 수",
    title="서울 구별 제과점 데이터 순위",
    color="매장 수",
    color_continuous_scale="Oranges"
)

fig_top10.update_traces(
    textposition="outside"
)

fig_top10.update_layout(
    xaxis_title="지역",
    yaxis_title="제과점 수",
    coloraxis_showscale=False
)

st.plotly_chart(
    fig_top10,
    use_container_width=True
)

if len(top10) > 0:
    first_district = top10.iloc[0]["지역"]
    first_count = top10.iloc[0]["매장 수"]

    st.success(
        f"🏆 데이터상 제과점이 가장 많은 지역은 "
        f"{first_district}! ({first_count:,}개)"
    )


# =========================================================
# 9. 빵집 탐정
# =========================================================
st.header("🔍 빵집 탐정")

st.markdown(
    "지역을 선택하고 그 지역의 빵집 영업 현황을 조사해 보자!"
)

district_options = sorted(
    district_df["지역"].unique().tolist()
)

selected_district = st.selectbox(
    "🔎 조사할 지역을 선택하세요",
    district_options
)

selected_df = district_df[
    district_df["지역"] == selected_district
]

selected_active = selected_df[
    selected_df["영업여부"] == "영업 중"
]

selected_closed = selected_df[
    selected_df["영업여부"] == "폐업"
]

district_total = len(selected_df)

district_active = len(selected_active)

district_closed = len(selected_closed)

district_closed_rate = (
    district_closed / district_total * 100
    if district_total > 0 else 0
)

col1, col2, col3 = st.columns(3)

col1.metric(
    f"{selected_district} 전체",
    f"{district_total:,}개"
)

col2.metric(
    "영업 중",
    f"{district_active:,}개"
)

col3.metric(
    "폐업",
    f"{district_closed:,}개"
)

st.markdown(
    f"### 🕵️ {selected_district} 빵집 탐정 결과"
)

st.write(
    f"이 지역의 데이터 중 폐업 매장 비율은 "
    f"**{district_closed_rate:.1f}%**야."
)

district_status = pd.DataFrame({
    "영업 상태": ["영업 중", "폐업"],
    "매장 수": [district_active, district_closed]
})

fig_district = px.bar(
    district_status,
    x="영업 상태",
    y="매장 수",
    color="영업 상태",
    text="매장 수",
    title=f"{selected_district} 빵집 영업 현황",
    color_discrete_map={
        "영업 중": "#FFB347",
        "폐업": "#B0B0B0"
    }
)

fig_district.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig_district,
    use_container_width=True
)


# =========================================================
# 10. 빵집 타임머신
# =========================================================
st.header("⏰ 빵집 타임머신")

st.markdown("""
원하는 연도를 선택해서 그해에 새롭게 인허가된 빵집을 살펴보자!
""")

valid_years = df["인허가연도"].dropna()

if len(valid_years) > 0:

    year_options = sorted(
        valid_years.astype(int).unique().tolist()
    )

    selected_year = st.selectbox(
        "📅 탐험할 연도",
        year_options,
        index=len(year_options) - 1
    )

    year_df = df[
        df["인허가연도"] == selected_year
    ]

    year_count = len(year_df)

    st.metric(
        f"{selected_year}년 인허가 빵집",
        f"{year_count:,}개"
    )

    year_district = (
        year_df.groupby("지역")
        .size()
        .reset_index(name="매장 수")
        .sort_values("매장 수", ascending=False)
    )

    year_district = year_district[
        year_district["지역"] != "기타 지역"
    ]

    if len(year_district) > 0:

        fig_year = px.bar(
            year_district,
            x="지역",
            y="매장 수",
            title=f"{selected_year}년 지역별 인허가 빵집",
            color="매장 수",
            color_continuous_scale="Reds"
        )

        st.plotly_chart(
            fig_year,
            use_container_width=True
        )

    st.caption(
        "※ 인허가일자 기준이며 실제 영업 시작일이나 현재 영업 여부와 다를 수 있어."
    )


# =========================================================
# 11. 빵집 면적 분석
# =========================================================
st.header("📐 빵집 크기 분석")

area_df = df[
    df["소재지면적"].notna()
    & (df["소재지면적"] > 0)
]

if len(area_df) > 0:

    mean_area = area_df["소재지면적"].mean()

    median_area = area_df["소재지면적"].median()

    col1, col2 = st.columns(2)

    col1.metric(
        "평균 매장 면적",
        f"{mean_area:.2f}"
    )

    col2.metric(
        "중앙값 매장 면적",
        f"{median_area:.2f}"
    )

    # 이상치에 의해 그래프가 지나치게 길어지는 것을 방지
    area_limit = area_df["소재지면적"].quantile(0.95)

    chart_area_df = area_df[
        area_df["소재지면적"] <= area_limit
    ]

    fig_area = px.histogram(
        chart_area_df,
        x="소재지면적",
        nbins=30,
        title="제과점 면적 분포 (상위 5% 이상값 제외)",
        color_discrete_sequence=["#F4A261"]
    )

    fig_area.update_layout(
        xaxis_title="매장 면적",
        yaxis_title="매장 수"
    )

    st.plotly_chart(
        fig_area,
        use_container_width=True
    )

    st.caption(
        "※ 그래프는 분포를 보기 위해 면적 상위 5%의 큰 값은 제외했어. "
        "평균과 중앙값은 전체 면적 데이터로 계산했어."
    )


# =========================================================
# 12. 랜덤 빵집 뽑기
# =========================================================
st.header("🎲 오늘의 랜덤 빵집")

st.markdown("""
버튼을 눌러 서울의 빵집 데이터 중 하나를 랜덤으로 뽑아보자!
""")

if st.button("🥐 랜덤 빵집 뽑기", use_container_width=True):

    random_store = df.sample(1).iloc[0]

    st.balloons()

    st.markdown("## 🎉 오늘 발견한 빵집!")

    st.markdown(
        f"### 🏪 {random_store['사업장명']}"
    )

    st.write(
        f"📍 지역: {random_store['지역']}"
    )

    st.write(
        f"📌 주소: {random_store['도로명주소']}"
    )

    st.write(
        f"🚦 영업 상태: {random_store['영업상태명']}"
    )

    if pd.notna(random_store["인허가일자"]):
        st.write(
            f"📅 인허가일자: "
            f"{random_store['인허가일자'].strftime('%Y-%m-%d')}"
        )

    if pd.notna(random_store["소재지면적"]):
        st.write(
            f"📐 매장 면적: {random_store['소재지면적']}"
        )

    st.info(
        "이 기능은 데이터에서 랜덤으로 매장을 선택하는 기능이야. "
        "실제 맛집 추천이나 현재 영업 확인 기능은 아니야."
    )


# =========================================================
# 13. 빵집 검색
# =========================================================
st.header("🔎 빵집 검색")

search_name = st.text_input(
    "찾고 싶은 빵집 이름을 입력하세요",
    placeholder="예: 파리바게뜨, 뚜레쥬르, 베이커리"
)

search_district = st.selectbox(
    "지역 필터",
    ["전체"] + district_options
)

search_status = st.selectbox(
    "영업 상태",
    ["전체", "영업 중", "폐업"]
)

search_df = df.copy()

if search_name:
    search_df = search_df[
        search_df["사업장명"].fillna("")
        .str.contains(search_name, case=False, regex=False)
    ]

if search_district != "전체":
    search_df = search_df[
        search_df["지역"] == search_district
    ]

if search_status != "전체":
    search_df = search_df[
        search_df["영업여부"] == search_status
    ]

st.write(
    f"🔍 검색 결과: {len(search_df):,}개"
)

display_columns = [
    "사업장명",
    "영업상태명",
    "인허가일자",
    "폐업일자",
    "지역",
    "도로명주소",
    "소재지면적"
]

available_columns = [
    col for col in display_columns
    if col in search_df.columns
]

st.dataframe(
    search_df[available_columns],
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 14. 검색 데이터 다운로드
# =========================================================
if len(search_df) > 0:

    csv_data = search_df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 검색 결과 CSV 다운로드",
        data=csv_data,
        file_name="빵집_검색결과.csv",
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# 15. 빵 상식 퀴즈
# =========================================================
st.header("🧠 빵집 데이터 퀴즈")

st.markdown("""
데이터를 분석한 내용을 바탕으로 퀴즈를 풀어보자!
""")

quiz_answer = st.radio(
    "현재 데이터에서 가장 많은 상태는 무엇일까?",
    [
        "영업 중인 빵집",
        "폐업한 빵집",
        "두 상태의 수가 같다"
    ],
    key="bakery_quiz"
)

if st.button("정답 확인하기 🧐"):

    if quiz_answer == "폐업한 빵집":
        st.success(
            f"🎉 정답! 폐업 데이터는 {closed_count:,}개로 "
            f"영업 중 데이터 {active_count:,}개보다 많아."
        )

        st.balloons()

    else:
        st.warning(
            f"아쉽지만 정답은 폐업한 빵집이야! "
            f"폐업 {closed_count:,}개, "
            f"영업 중 {active_count:,}개."
        )


# =========================================================
# 16. 데이터 분석 마무리
# =========================================================
st.divider()

st.header("🎓 오늘의 탐험 결과")

st.markdown("""
오늘 우리는 서울 제과점 데이터를 이용해서 다음 내용을 분석했어.

- 서울 제과점의 전체 데이터 수
- 영업 중인 빵집과 폐업한 빵집
- 제과점이 많은 지역 TOP 10
- 지역별 빵집 영업 현황
- 연도별 신규 인허가 빵집
- 매장 면적 분포
- 랜덤 빵집 탐험
- 빵집 이름 검색

데이터를 통해 재미있는 사실을 발견할 수 있지만,
이 데이터는 과거 기록을 포함하므로 실제 현재 매장 현황과 다를 수 있다는 점도 기억하자!
""")

st.success("🥐 빵집 탐험 완료! 데이터 분석가로 한 걸음 성장했어!")
