import streamlit as st
import pandas as pd
import plotly.express as px
import random
import re
from pathlib import Path  #
# CSV 파일 자동 탐색
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

possible_paths = [
    BASE_DIR / "식품_제과점영업 (1).csv",
    BASE_DIR / "식품_제과점영업.csv",
    BASE_DIR / "식품_제과점영업(1).csv",
    BASE_DIR / "식품_제과점영업.csv",
    BASE_DIR / "pages" / "식품_제과점영업 (1).csv",
    BASE_DIR / "pages" / "식품_제과점영업.csv",
]

CSV_PATH = None

for path in possible_paths:
    if path.exists():
        CSV_PATH = path
        break

# 파일 이름이 조금 다르더라도 자동 검색
if CSV_PATH is None:
    csv_files = list(BASE_DIR.glob("*제과점영업*.csv"))

    if csv_files:
        CSV_PATH = csv_files[0]

# =========================================================
# 데이터 불러오기
# =========================================================
@st.cache_data
def load_data(file_path):

    try:
        df = pd.read_csv(
            file_path,
            encoding="cp949",
            low_memory=False
        )

    except UnicodeDecodeError:
        df = pd.read_csv(
            file_path,
            encoding="utf-8-sig",
            low_memory=False
        )

    # 날짜 변환
    df["인허가일자"] = pd.to_datetime(
        df["인허가일자"],
        errors="coerce"
    )

    df["폐업일자"] = pd.to_datetime(
        df["폐업일자"],
        errors="coerce"
    )

    # 면적 숫자 변환
    df["소재지면적"] = pd.to_numeric(
        df["소재지면적"],
        errors="coerce"
    )

    # 지역 추출
    districts = [
        "종로구", "중구", "용산구", "성동구", "광진구",
        "동대문구", "중랑구", "성북구", "강북구", "도봉구",
        "노원구", "은평구", "서대문구", "마포구", "양천구",
        "강서구", "구로구", "금천구", "영등포구", "동작구",
        "관악구", "서초구", "강남구", "송파구", "강동구"
    ]

    address = df["도로명주소"].fillna("")

    def extract_district(addr):
        for district in districts:
            if district in str(addr):
                return district
        return "기타 지역"

    df["지역"] = address.apply(extract_district)

    # 영업 상태
    df["상태"] = df["영업상태명"].fillna("정보 없음")

    df["영업여부"] = df["상태"].apply(
        lambda x: "영업 중" if "영업" in str(x) else "폐업"
    )

    # 인허가 연도
    df["인허가연도"] = df["인허가일자"].dt.year

    return df


# =========================================================
# 데이터 불러오기 실행
# =========================================================
if CSV_PATH is None:

    st.error("🚨 CSV 파일을 찾을 수 없습니다.")

    st.write("현재 앱이 검색한 폴더:")
    st.code(str(BASE_DIR))

    st.write("현재 폴더에 있는 파일 목록:")

    for file in BASE_DIR.iterdir():
        st.write(file.name)

    st.info(
        "GitHub 저장소의 최상위 폴더에 "
        "식품_제과점영업 (1).csv 파일을 업로드해 주세요."
    )

    st.stop()

else:

    st.success(f"✅ CSV 파일 발견: {CSV_PATH.name}")

    df = load_data(str(CSV_PATH))
