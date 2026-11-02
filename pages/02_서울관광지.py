import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="서울 인기 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 제목
st.title("🗺️ 외국인에게 인기 있는 서울 관광지 TOP 10")
st.markdown(
    "서울을 여행하는 외국인들에게 추천하는 "
    "대표 관광지를 지도에서 확인해 보세요! 🇰🇷"
)

st.info(
    "서울의 대표 관광지를 바탕으로 구성한 추천 목록입니다. "
    "공식 방문객 순위와는 다를 수 있습니다."
)

# 관광지 데이터
places = [
    {
        "rank": 1,
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9850,
        "area": "중구",
        "description": "K-뷰티 매장, 패션 쇼핑, 길거리 음식이 유명한 서울의 대표 쇼핑 거리입니다.",
        "tip": "화장품 쇼핑과 길거리 간식을 즐겨보세요.",
        "category": "쇼핑 · 먹거리"
    },
    {
        "rank": 2,
        "name": "남산서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "area": "용산구",
        "description": "서울의 아름다운 전경과 야경을 감상할 수 있는 대표적인 전망 명소입니다.",
        "tip": "해 질 무렵 방문하면 멋진 야경을 볼 수 있습니다.",
        "category": "전망 · 야경"
    },
    {
        "rank": 3,
        "name": "코엑스 별마당도서관",
        "english": "Starfield Library",
        "lat": 37.5125,
        "lon": 127.0594,
        "area": "강남구",
        "description": "높은 책장과 아름다운 실내 공간으로 유명한 사진 명소입니다.",
        "tip": "쇼핑과 식사를 함께 즐겨보세요.",
        "category": "쇼핑 · 문화"
    },
    {
        "rank": 4,
        "name": "강남역",
        "english": "Gangnam Station",
        "lat": 37.4979,
        "lon": 127.0276,
        "area": "강남구",
        "description": "세련된 상점과 카페, 맛집이 모여 있는 서울의 대표 번화가입니다.",
        "tip": "골목에 있는 개성 있는 카페도 방문해 보세요.",
        "category": "쇼핑 · 카페"
    },
    {
        "rank": 5,
        "name": "홍대거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "area": "마포구",
        "description": "거리 공연, 음악, 패션, 개성 있는 카페가 유명한 젊음의 거리입니다.",
        "tip": "주말 거리 공연을 구경해 보세요.",
        "category": "문화 · 거리"
    },
    {
        "rank": 6,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "area": "종로구",
        "description": "조선 왕조의 대표 궁궐로 한국의 전통 역사와 문화를 경험할 수 있습니다.",
        "tip": "한복을 입고 궁궐을 둘러보는 것도 추천합니다.",
        "category": "역사 · 문화"
    },
    {
        "rank": 7,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "area": "종로구",
        "description": "한국 전통 한옥이 모여 있는 아름다운 골목 마을입니다.",
        "tip": "실제 주민들이 생활하는 곳이므로 조용히 관람해 주세요.",
        "category": "전통 · 산책"
    },
    {
        "rank": 8,
        "name": "동대문디자인플라자",
        "english": "DDP",
        "lat": 37.5671,
        "lon": 127.0095,
        "area": "중구",
        "description": "독특한 곡선 건축물과 다양한 전시, 디자인 행사가 열리는 문화 공간입니다.",
        "tip": "밤에 방문하면 아름다운 건축물 조명을 볼 수 있습니다.",
        "category": "건축 · 전시"
    },
    {
        "rank": 9,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "area": "종로구",
        "description": "빈대떡, 김밥 등 다양한 한국 음식을 맛볼 수 있는 전통시장입니다.",
        "tip": "다양한 한국 길거리 음식을 맛보세요.",
        "category": "전통시장 · 먹거리"
    },
    {
        "rank": 10,
        "name": "낙산공원",
        "english": "Naksan Park",
        "lat": 37.5804,
        "lon": 127.0072,
        "area": "종로구",
        "description": "서울 성곽길과 도심 풍경을 함께 감상할 수 있는 산책 명소입니다.",
        "tip": "편한 신발을 신고 방문하는 것을 추천합니다.",
        "category": "산책 · 전망"
    }
]

# 지도 만들기
seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 지도에 관광지 표시
for place in places:

    popup_html = f"""
    <div style="width:220px">
        <h4>{place['rank']}. {place['name']}</h4>
        <p>{place['english']}</p>
        <p>{place['description']}</p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{place['rank']}. {place['name']}",
        popup=folium.Popup(
            popup_html,
            max_width=280
        ),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background:#2563eb;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:30px;
                height:30px;
                line-height:26px;
                text-align:center;
                font-weight:bold;
                font-size:13px;
                box-shadow:0 1px 5px rgba(0,0,0,.45);
            ">
                {place['rank']}
            </div>
            """,
            icon_size=(30, 30),
            icon_anchor=(15, 15)
        )
    ).add_to(seoul_map)

# 지도 출력
st.subheader("📍 서울 관광지 위치 지도")

st_folium(
    seoul_map,
    height=600,
    use_container_width=True,
    returned_objects=[]
)

# 관광지 설명
st.subheader("✨ 서울 관광지 TOP 10 소개")

left, right = st.columns(2)

for i, place in enumerate(places):

    target = left if i % 2 == 0 else right

    with target:

        with st.container(border=True):

            st.markdown(
                f"### {place['rank']}. {place['name']}"
            )

            st.caption(
                f"{place['english']} · {place['area']} · {place['category']}"
            )

            st.write(place["description"])

            st.markdown(
                f"💡 **여행 팁:** {place['tip']}"
            )

            url = (
                "https://www.google.com/maps/search/?api=1&query="
                f"{place['lat']},{place['lon']}"
            )

            st.markdown(
                f"[📍 구글 지도에서 위치 보기]({url})"
            )

# 마무리
st.divider()

st.markdown(
    "🇰🇷 **즐거운 서울 여행 되세요!**"
)

st.caption(
    "지도 제공: OpenStreetMap | "
    "관광지 위치는 대표 지점 기준입니다."
)

