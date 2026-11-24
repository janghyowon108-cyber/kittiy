import streamlit as st
import pandas as pd
import plotly.express as px
import random
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
# 2. CSV 파일 자동 찾기
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

possible_paths = [
    BASE_DIR / "식품_제과점영업 (1).csv",
    BASE_DIR / "식품_제과점영업.csv",
    BASE_DIR / "식품_제과점영업(1).csv",
    BASE_DIR / "pages" / "식품_제과점영업 (1).csv",
    BASE_DIR / "pages" / "식품_제과점영업.csv",
]

CSV_PATH = None

for path in possible_paths:
    if path.exists():
        CSV_PATH = path
        break

# 파일명이 조금 달라도 자동 탐색
if CSV_PATH is None:
    csv_files = list(BASE_DIR.glob("*제과점영업*.csv"))

    if not csv_files:
        csv_files = list(BASE_DIR.glob("**/*제과점영업*.csv"))

    if csv_files:
        CSV_PATH = csv_files[0]


# =========================================================
# 3. 데이터 불러오기
# =========================================================
@st.cache_data
def load_data(file_path):

    # 인코딩 자동 시도
    encodings = ["cp949", "utf-8-sig", "utf-8"]

    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                low_memory=False
            )
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 파일 인코딩을 확인할 수 없습니다.")

    # -----------------------------------------------------
    # 컬럼이 없을 때 오류 방지
    # -----------------------------------------------------
    required_columns = [
        "사업장명",
        "영업상태명",
        "인허가일자",
        "폐업일자",
        "소재지면적",
        "도로명주소",
        "지번주소"
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    # -----------------------------------------------------
    # 날짜 변환
    # -----------------------------------------------------
    df["인허가일자"] = pd.to_datetime(
        df["인허가일자"],
        errors="coerce"
    )

    df["폐업일자"] = pd.to_datetime(
        df["폐업일자"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # 면적 숫자 변환
    # -----------------------------------------------------
    df["소재지면적"] = pd.to_numeric(
        df["소재지면적"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # 지역 추출
    # -----------------------------------------------------
    districts = [
        "종로구", "중구", "용산구", "성동구", "광진구",
        "동대문구", "중랑구", "성북구", "강북구", "도봉구",
        "노원구", "은평구", "서대문구", "마포구", "양천구",
        "강서구", "구로구", "금천구", "영등포구", "동작구",
        "관악구", "서초구", "강남구", "송파구", "강동구"
    ]

    # 주소가 도로명주소 또는 지번주소에 있을 수 있음
    road_address = df["도로명주소"].fillna("").astype(str)
    lot_address = df["지번주소"].fillna("").astype(str)

    address = road_address + " " + lot_address

    def extract_district(addr):

        for district in districts:
            if district in str(addr):
                return district

        return "기타 지역"

    df["지역"] = address.apply(extract_district)

    # -----------------------------------------------------
    # 영업 상태 정리
    # -----------------------------------------------------
    df["영업상태명"] = df["영업상태명"].fillna("정보 없음")

    def classify_status(status):

        status = str(status)

        if "영업" in status:
            return "영업 중"

        elif "폐업" in status:
            return "폐업"

        else:
            return "정보 없음"

    df["영업여부"] = df["영업상태명"].apply(classify_status)

    # -----------------------------------------------------
    # 인허가 연도
    # -----------------------------------------------------
    df["인허가연도"] = df["인허가일자"].dt.year

    return df


# =========================================================
# 4. 데이터 로딩
# =========================================================
if CSV_PATH is None:

    st.error("🚨 CSV 파일을 찾을 수 없습니다.")

    st.write("현재 검색한 폴더:")
    st.code(str(BASE_DIR))

    st.write("현재 폴더에 있는 파일:")

    try:
        for file in BASE_DIR.iterdir():
            st.write(file.name)

    except Exception as e:
        st.write(e)

    st.info(
        "GitHub 저장소의 최상위 폴더에 "
        "식품_제과점영업 (1).csv 파일을 넣어주세요."
    )

    st.stop()


try:

    df = load_data(str(CSV_PATH))

except Exception as e:

    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()


# =========================================================
# 5. 제목
# =========================================================
st.title("🥐 빵집 탐험대")

st.markdown("""
### 서울의 빵집 데이터를 탐험해 보자! 🔍

서울에는 얼마나 많은 빵집이 있을까?

어떤 지역에 빵집이 많을까?

과거에는 어떤 빵집이 새롭게 생겼을까?

데이터를 이용해서 재미있는 사실을 발견해 보자!
""")

st.divider()


# =========================================================
# 6. 데이터 통계
# =========================================================
total_count = len(df)

active_count = len(
    df[df["영업여부"] == "영업 중"]
)

closed_count = len(
    df[df["영업여부"] == "폐업"]
)

unknown_count = len(
    df[df["영업여부"] == "정보 없음"]
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
# 7. 탐험 레벨
# =========================================================
st.header("🎮 빵집 탐험 레벨")

level = min(total_count // 10000 + 1, 10)

st.progress(level / 10)

st.success(f"🥐 빵집 데이터 탐험가 레벨 {level}")

st.write(
    f"현재 **{total_count:,}개**의 데이터를 탐험 중이야!"
)

st.caption(
    "데이터를 확인하고 분석하면서 빵집 탐험가가 되어 보자."
)

st.divider()


# =========================================================
# 8. 핵심 통계 카드
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
    "정보 없음",
    f"{unknown_count:,}개"
)


# =========================================================
# 9. 영업 상태 그래프
# =========================================================
st.header("🥐 빵집 영업 상태")

status_df = pd.DataFrame({
    "상태": ["영업 중", "폐업", "정보 없음"],
    "매장 수": [
        active_count,
        closed_count,
        unknown_count
    ]
})

fig_status = px.pie(
    status_df,
    names="상태",
    values="매장 수",
    title="빵집 영업 상태",
    hole=0.45,
    color="상태",
    color_discrete_map={
        "영업 중": "#FFB347",
        "폐업": "#AAAAAA",
        "정보 없음": "#80BFFF"
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
    "💡 이 데이터에는 과거 폐업한 빵집도 포함되어 있어. "
    "따라서 전체 데이터 수가 실제 현재 영업 중인 빵집 수와 같지는 않아."
)


# =========================================================
# 10. 지역별 빵집 랭킹
# =========================================================
st.header("🏆 빵집이 많은 지역 TOP 10")

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

if len(top10) > 0:

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

    first_district = top10.iloc[0]["지역"]
    first_count = top10.iloc[0]["매장 수"]

    st.success(
        f"🏆 데이터상 제과점이 가장 많은 지역은 "
        f"{first_district}! ({first_count:,}개)"
    )

else:

    st.warning("지역 데이터를 분석할 수 없습니다.")


# =========================================================
# 11. 빵집 탐정
# =========================================================
st.header("🔍 빵집 탐정")

st.markdown(
    "지역을 선택하고 해당 지역의 빵집 영업 현황을 조사해 보자!"
)

district_options = sorted(
    district_df["지역"].unique().tolist()
)

if len(district_options) > 0:

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

    selected_unknown = selected_df[
        selected_df["영업여부"] == "정보 없음"
    ]

    district_total = len(selected_df)

    district_active = len(selected_active)

    district_closed = len(selected_closed)

    district_unknown = len(selected_unknown)

    district_closed_rate = (
        district_closed / district_total * 100
        if district_total > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "전체",
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

    col4.metric(
        "정보 없음",
        f"{district_unknown:,}개"
    )

    st.markdown(
        f"### 🕵️ {selected_district} 탐정 분석 결과"
    )

    st.write(
        f"폐업 데이터 비율은 **{district_closed_rate:.1f}%**야."
    )

    district_status = pd.DataFrame({
        "영업 상태": ["영업 중", "폐업", "정보 없음"],
        "매장 수": [
            district_active,
            district_closed,
            district_unknown
        ]
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
            "폐업": "#AAAAAA",
            "정보 없음": "#80BFFF"
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
# 12. 빵집 타임머신
# =========================================================
st.header("⏰ 빵집 타임머신")

st.markdown("""
연도를 선택하면 그해 인허가된 빵집 데이터를 확인할 수 있어!
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
        "※ 인허가일자 기준이므로 실제 영업 시작일이나 현재 영업 여부와 다를 수 있어."
    )

else:

    st.warning("인허가일자 데이터가 없습니다.")


# =========================================================
# 13. 빵집 면적 분석
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
        f"{mean_area:,.2f}"
    )

    col2.metric(
        "중앙값 매장 면적",
        f"{median_area:,.2f}"
    )

    # 큰 이상값 때문에 그래프가 왜곡되는 것을 방지
    area_limit = area_df["소재지면적"].quantile(0.95)

    chart_area_df = area_df[
        area_df["소재지면적"] <= area_limit
    ]

    fig_area = px.histogram(
        chart_area_df,
        x="소재지면적",
        nbins=30,
        title="빵집 면적 분포 (상위 5% 이상값 제외)",
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
        "※ 그래프는 면적 상위 5%의 큰 값을 제외해 분포를 보기 쉽게 했어. "
        "평균과 중앙값은 전체 데이터를 이용했어."
    )

else:

    st.warning("면적 데이터가 없습니다.")


# =========================================================
# 14. 랜덤 빵집 뽑기
# =========================================================
st.header("🎲 오늘의 랜덤 빵집")

st.markdown("""
버튼을 누르면 데이터 속 빵집 하나를 랜덤으로 뽑아줘!
""")

if st.button(
    "🥐 랜덤 빵집 뽑기",
    use_container_width=True
):

    random_store = df.sample(1).iloc[0]

    st.balloons()

    st.markdown("## 🎉 오늘 발견한 빵집!")

    store_name = random_store["사업장명"]

    if pd.isna(store_name):
        store_name = "이름 정보 없음"

    st.markdown(
        f"### 🏪 {store_name}"
    )

    st.write(
        f"📍 지역: {random_store['지역']}"
    )

    road_address = random_store["도로명주소"]

    lot_address = random_store["지번주소"]

    if pd.notna(road_address) and str(road_address).strip():
        st.write(f"📌 도로명주소: {road_address}")

    elif pd.notna(lot_address) and str(lot_address).strip():
        st.write(f"📌 지번주소: {lot_address}")

    else:
        st.write("📌 주소 정보 없음")

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
        "랜덤으로 선택된 매장이야! "
        "맛집 추천이나 실시간 영업 확인은 아니야."
    )


# =========================================================
# 15. 빵집 검색
# =========================================================
st.header("🔎 빵집 검색")

search_name = st.text_input(
    "찾고 싶은 빵집 이름",
    placeholder="예: 파리바게뜨, 뚜레쥬르"
)

search_district = st.selectbox(
    "지역 필터",
    ["전체"] + district_options
)

search_status = st.selectbox(
    "영업 상태 필터",
    ["전체", "영업 중", "폐업", "정보 없음"]
)

search_df = df.copy()

# 이름 검색
if search_name:

    search_df = search_df[
        search_df["사업장명"]
        .fillna("")
        .astype(str)
        .str.contains(
            search_name,
            case=False,
            regex=False
        )
    ]

# 지역 필터
if search_district != "전체":

    search_df = search_df[
        search_df["지역"] == search_district
    ]

# 상태 필터
if search_status != "전체":

    search_df = search_df[
        search_df["영업여부"] == search_status
    ]

st.write(
    f"🔍 검색 결과: **{len(search_df):,}개**"
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
# 16. CSV 다운로드
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
# 17. 빵집 데이터 퀴즈
# =========================================================
st.header("🧠 빵집 데이터 퀴즈")

st.markdown("""
데이터 분석 결과를 바탕으로 퀴즈를 풀어보자!
""")

if active_count > closed_count:

    correct_answer = "영업 중인 빵집"

elif closed_count > active_count:

    correct_answer = "폐업한 빵집"

else:

    correct_answer = "두 상태의 수가 같다"


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

    if quiz_answer == correct_answer:

        st.success(
            f"🎉 정답! 영업 중 {active_count:,}개, "
            f"폐업 {closed_count:,}개야."
        )

        st.balloons()

    else:

        st.warning(
            f"아쉽지만 정답은 **{correct_answer}**야! "
            f"영업 중 {active_count:,}개, "
            f"폐업 {closed_count:,}개."
        )


# =========================================================
# 18. 데이터 분석 마무리
# =========================================================
st.divider()

st.header("🎓 오늘의 탐험 결과")

st.markdown("""
오늘 우리는 서울 제과점 데이터를 이용해서 다음 내용을 분석했어.

🥐 전체 제과점 데이터 수

📊 영업 중인 빵집과 폐업한 빵집

🏆 제과점이 많은 지역 TOP 10

🔍 지역별 영업 현황

⏰ 연도별 신규 인허가 빵집

📐 매장 면적 분포

🎲 랜덤 빵집 탐험

🔎 빵집 이름 검색

🧠 데이터 분석 퀴즈

데이터를 통해 재미있는 사실을 발견할 수 있지만,
이 데이터는 과거 기록을 포함하므로 실제 현재 매장 현황과 다를 수 있다는 점도 기억하자!
""")

st.success(
    "🥐 빵집 탐험 완료! 데이터 분석가로 한 걸음 성장했어!"
)
