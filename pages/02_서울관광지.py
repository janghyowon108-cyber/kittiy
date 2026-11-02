"lat": 37.5671, "lon": 127.0095, "area": "중구",
        "description": "독특한 곡선 형태의 건축물로 유명하며 전시, 디자인 행사, 야간 조명 등을 즐길 수 있어요.",
        "tip": "건물 외관과 주변 야경도 사진으로 남겨 보세요.",
        "category": "건축 · 전시",
    },
    {
        "rank": 9, "name": "광장시장", "english": "Gwangjang Market",
        "lat": 37.5700, "lon": 126.9997, "area": "종로구",
        "description": "빈대떡, 김밥 등 다양한 한국 길거리 음식을 맛볼 수 있는 전통시장으로 유명해요.",
        "tip": "사람이 붐빌 수 있으니 소지품을 잘 챙기고 여유 있게 둘러보세요.",
        "category": "전통시장 · 먹거리",
    },
    {
        "rank": 10, "name": "낙산공원", "english": "Naksan Park",
        "lat": 37.5804, "lon": 127.0072, "area": "종로구",
        "description": "성곽길과 서울 도심 전망을 함께 즐길 수 있는 산책 명소예요. 최근 외국인 방문 증가가 주목된 곳이기도 해요.",
        "tip": "언덕길과 계단이 있으니 편한 신발을 신어 주세요.",
        "category": "산책 · 전망",
    },
]

st.title("🗺️ 외국인에게 인기 있는 서울 관광지 TOP 10")
st.caption("서울 여행에서 놓치기 아까운 대표 명소 10곳을 지도에서 확인해 보세요!")

st.info(
    "📌 이 목록은 서울시의 외국인 방문객 동향 자료와 서울 공식 관광 안내를 참고해 만든 "
    "추천 큐레이션입니다. 서울시가 발표한 단일 공식 TOP 10 순위는 아닙니다."
)

# Folium + OpenStreetMap: 별도의 지도 API 키 없이 표시됩니다.
seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True,
)

for place in PLACES:
    popup_html = f"""
    <div style="width:230px; font-family: sans-serif;">
      <b>#{place['rank']} {place['name']}</b><br>
      <span style="color:#555;">{place['english']}</span><br>
      <small>{place['area']} · {place['category']}</small><br><br>
      {place['description']}
    </div>
    """
    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"#{place['rank']} {place['name']}",
        popup=folium.Popup(popup_html, max_width=280),
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
            ">{place['rank']}</div>
            """,
            icon_size=(30, 30),
            icon_anchor=(15, 15),
        ),
    ).add_to(seoul_map)

st.subheader("📍 서울 관광지 지도")
st_folium(
    seoul_map,
    height=600,
    use_container_width=True,
    returned_objects=[],
)

st.subheader("✨ 관광지 간단 소개")
st.write("지도 위의 숫자 마커를 누르면 장소 이름과 설명도 확인할 수 있어요.")

# 두 열로 보기 좋게 소개
left, right = st.columns(2)
for i, place in enumerate(PLACES):
    target = left if i % 2 == 0 else right
    with target:
        with st.container(border=True):
            st.markdown(f"### {place['rank']}. {place['name']}")
            st.caption(f"{place['english']} · {place['area']} · {place['category']}")
            st.write(place["description"])
            st.markdown(f"💡 **여행 팁:** {place['tip']}")
            google_maps_url = (
                "https://www.google.com/maps/search/?api=1&query="
                f"{place['lat']},{place['lon']}"
            )
            st.markdown(f"[구글 지도에서 위치 보기]({google_maps_url})")

st.divider()
st.caption(
    "자료 참고: 서울특별시의 2025년 외국인 방문객 동향 분석(2026년 공개), "
    "서울 공식 관광 안내. 방문객 동향은 조사 기준과 기간에 따라 달라질 수 있습니다."
)
