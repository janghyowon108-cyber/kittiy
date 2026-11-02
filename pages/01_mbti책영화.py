
import streamlit as st
import random

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="MBTI 책 & 영화 추천",
    page_icon="📚",
    layout="wide"
)

# -----------------------------
# 디자인 CSS
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #F7F5FF;
}
.main-title {
    text-align: center;
    color: #6941C6;
    font-size: 36px;
    font-weight: bold;
}
.sub-title {
    text-align: center;
    color: #77718A;
    font-size: 17px;
}
.book-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #E5DDFC;
    min-height: 210px;
}
.movie-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #DCE5FF;
    min-height: 210px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 제목
# -----------------------------
st.markdown(
    '<div class="main-title">📚 MBTI 취향 저격 추천소 🎬</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">내 MBTI와 어울리는 책 2권, 영화 2편을 만나보자!</div>',
    unsafe_allow_html=True
)

st.write("")
st.write("")

st.info("💜 나의 MBTI를 선택하면 취향에 맞는 책과 영화를 추천해 줄게!")

# -----------------------------
# 책 데이터 (모두 한국 작가)
# -----------------------------
books = {
    "완득이": {
        "author": "김려령",
        "genre": "성장 소설",
        "desc": "평범하지 않은 환경 속에서 자신만의 방식으로 성장하는 완득이의 이야기!",
        "reason": "유쾌한 웃음과 따뜻한 감동을 함께 느낄 수 있어요."
    },
    "아몬드": {
        "author": "손원평",
        "genre": "성장 소설",
        "desc": "감정을 느끼는 데 어려움이 있는 소년 윤재가 세상과 관계를 맺어가는 이야기.",
        "reason": "감정과 인간관계에 대해 깊이 생각해 볼 수 있어요."
    },
    "페인트": {
        "author": "이희영",
        "genre": "청소년 소설",
        "desc": "부모를 직접 선택할 수 있는 미래 사회를 배경으로 한 흥미로운 이야기!",
        "reason": "가족과 선택, 관계에 대해 새로운 시각을 얻을 수 있어요."
    },
    "체리새우: 비밀글입니다": {
        "author": "황영미",
        "genre": "청소년 소설",
        "desc": "친구 관계 속에서 고민하고 성장하는 중학생 다현이의 이야기.",
        "reason": "학교생활과 친구 관계에 공감하며 읽기 좋아요."
    },
    "시간을 파는 상점": {
        "author": "김선영",
        "genre": "청소년 소설",
        "desc": "시간을 사고파는 특별한 상점을 중심으로 펼쳐지는 이야기.",
        "reason": "시간과 삶의 의미를 생각해 보게 해요."
    },
    "불편한 편의점": {
        "author": "김호연",
        "genre": "힐링 소설",
        "desc": "서울의 한 편의점에서 다양한 사람들이 만나며 벌어지는 따뜻한 이야기.",
        "reason": "편안하게 읽으면서 일상의 소중함을 느낄 수 있어요."
    },
    "달러구트 꿈 백화점": {
        "author": "이미예",
        "genre": "판타지",
        "desc": "잠든 사람들에게 꿈을 판매하는 신비로운 백화점 이야기.",
        "reason": "상상력을 자극하는 독특한 세계관이 매력적이에요."
    },
    "어서 오세요, 휴남동 서점입니다": {
        "author": "황보름",
        "genre": "힐링 소설",
        "desc": "동네 서점에서 사람들이 만나 서로의 삶을 나누는 이야기.",
        "reason": "바쁜 일상에서 잠시 쉬어 가고 싶을 때 추천해요."
    },
    "위저드 베이커리": {
        "author": "구병모",
        "genre": "판타지",
        "desc": "신비로운 마법의 빵을 만드는 베이커리에서 벌어지는 이야기.",
        "reason": "독특한 상상력과 흥미로운 전개가 돋보여요."
    },
    "유원": {
        "author": "백온유",
        "genre": "성장 소설",
        "desc": "과거의 사건을 안고 살아가는 한 소녀의 성장과 변화를 그린 이야기.",
        "reason": "자신의 감정과 삶을 돌아보게 해요."
    },
    "순례 주택": {
        "author": "유은실",
        "genre": "청소년 소설",
        "desc": "개성 넘치는 사람들이 살아가는 순례 주택에서 벌어지는 유쾌한 이야기.",
        "reason": "재미와 따뜻한 메시지를 동시에 만날 수 있어요."
    },
    "긴긴밤": {
        "author": "루리",
        "genre": "우화",
        "desc": "코뿔소와 어린 펭귄이 함께 길을 찾아가는 특별한 이야기.",
        "reason": "우정과 용기, 서로를 이해하는 마음을 배울 수 있어요."
    },
    "죽이고 싶은 아이": {
        "author": "이꽃님",
        "genre": "미스터리",
        "desc": "한 사건을 둘러싼 여러 사람의 이야기가 펼쳐지는 청소년 소설.",
        "reason": "반전과 추리 요소를 좋아한다면 흥미롭게 읽을 수 있어요."
    },
    "세계를 건너 너에게 갈게": {
        "author": "이꽃님",
        "genre": "청소년 소설",
        "desc": "시간을 뛰어넘어 편지를 주고받는 두 사람의 특별한 이야기.",
        "reason": "따뜻한 감동과 상상력을 함께 느낄 수 있어요."
    },
    "행운이 너에게 다가오는 중": {
        "author": "이꽃님",
        "genre": "청소년 소설",
        "desc": "청소년들의 일상과 관계, 성장에 관한 이야기를 담은 작품.",
        "reason": "주변 사람들과 자신의 삶을 돌아보게 해요."
    },
    "마당을 나온 암탉": {
        "author": "황선미",
        "genre": "성장 동화",
        "desc": "자신의 꿈을 찾아 새로운 세상으로 나아가는 암탉 잎싹의 이야기.",
        "reason": "꿈과 도전, 자유의 의미를 생각해 볼 수 있어요."
    }
}

# -----------------------------
# 영화 데이터
# 국내 극장 누적 관객 100만 명 이상
# -----------------------------
movies = {
    "극한직업": {
        "audience": "1,626만 명",
        "rating": "15세 이상 관람가",
        "genre": "코미디 · 액션",
        "desc": "잠복근무를 위해 치킨집을 운영하게 된 형사들의 좌충우돌 이야기!",
        "reason": "빠른 전개와 웃음이 가득한 인기 코미디 영화예요."
    },
    "신과함께-죄와 벌": {
        "audience": "1,441만 명",
        "rating": "12세 이상 관람가",
        "genre": "판타지 · 드라마",
        "desc": "저승에서 여러 재판을 받게 된 주인공의 특별한 여정을 그린 영화.",
        "reason": "화려한 상상력과 감동적인 스토리가 매력적이에요."
    },
    "국제시장": {
        "audience": "1,425만 명",
        "rating": "12세 이상 관람가",
        "genre": "드라마",
        "desc": "격변하는 시대를 살아온 한 가족의 삶과 사랑을 그린 작품.",
        "reason": "가족의 소중함과 따뜻한 감동을 느낄 수 있어요."
    },
    "어벤져스: 엔드게임": {
        "audience": "1,393만 명",
        "rating": "12세 이상 관람가",
        "genre": "SF · 액션",
        "desc": "어벤져스 영웅들이 세상을 구하기 위해 마지막 도전에 나서는 이야기.",
        "reason": "웅장한 스케일과 흥미진진한 전개가 돋보여요."
    },
    "겨울왕국 2": {
        "audience": "1,374만 명",
        "rating": "전체 관람가",
        "genre": "애니메이션 · 판타지",
        "desc": "엘사와 안나가 마법의 비밀을 찾아 떠나는 환상적인 모험!",
        "reason": "멋진 음악과 아름다운 영상미를 즐길 수 있어요."
    },
    "아바타": {
        "audience": "1,362만 명",
        "rating": "12세 이상 관람가",
        "genre": "SF · 모험",
        "desc": "신비로운 행성 판도라에서 펼쳐지는 놀라운 모험 이야기.",
        "reason": "상상 속 세계를 실제처럼 경험하는 재미가 있어요."
    },
    "알라딘": {
        "audience": "1,255만 명",
        "rating": "전체 관람가",
        "genre": "판타지 · 뮤지컬",
        "desc": "마법 램프를 발견한 알라딘의 신나는 모험과 사랑 이야기.",
        "reason": "신나는 음악과 화려한 장면이 가득한 영화예요."
    },
    "겨울왕국": {
        "audience": "1,029만 명",
        "rating": "전체 관람가",
        "genre": "애니메이션 · 판타지",
        "desc": "서로 다른 능력을 가진 두 자매의 사랑과 모험 이야기.",
        "reason": "귀에 익숙한 음악과 감동적인 이야기가 매력적이에요."
    },
    "인터스텔라": {
        "audience": "1,027만 명",
        "rating": "12세 이상 관람가",
        "genre": "SF · 모험",
        "desc": "인류의 미래를 위해 우주로 떠나는 사람들의 이야기.",
        "reason": "우주와 과학, 상상력을 좋아한다면 강력 추천해요."
    }
}

# -----------------------------
# MBTI별 추천 매칭
# -----------------------------
recommendations = {
    "ISTJ": {
        "books": ["페인트", "시간을 파는 상점"],
        "movies": ["인터스텔라", "국제시장"]
    },
    "ISFJ": {
        "books": ["불편한 편의점", "긴긴밤"],
        "movies": ["국제시장", "겨울왕국"]
    },
    "INFJ": {
        "books": ["아몬드", "유원"],
        "movies": ["신과함께-죄와 벌", "인터스텔라"]
    },
    "INTJ": {
        "books": ["위저드 베이커리", "페인트"],
        "movies": ["인터스텔라", "어벤져스: 엔드게임"]
    },
    "ISTP": {
        "books": ["완득이", "죽이고 싶은 아이"],
        "movies": ["극한직업", "아바타"]
    },
    "ISFP": {
        "books": ["달러구트 꿈 백화점", "마당을 나온 암탉"],
        "movies": ["알라딘", "겨울왕국 2"]
    },
    "INFP": {
        "books": ["긴긴밤", "세계를 건너 너에게 갈게"],
        "movies": ["겨울왕국 2", "신과함께-죄와 벌"]
    },
    "INTP": {
        "books": ["위저드 베이커리", "아몬드"],
        "movies": ["인터스텔라", "아바타"]
    },
    "ESTP": {
        "books": ["완득이", "순례 주택"],
        "movies": ["극한직업", "어벤져스: 엔드게임"]
    },
    "ESFP": {
        "books": ["순례 주택", "달러구트 꿈 백화점"],
        "movies": ["알라딘", "극한직업"]
    },
    "ENFP": {
        "books": ["달러구트 꿈 백화점", "세계를 건너 너에게 갈게"],
        "movies": ["알라딘", "겨울왕국 2"]
    },
    "ENTP": {
        "books": ["죽이고 싶은 아이", "위저드 베이커리"],
        "movies": ["어벤져스: 엔드게임", "극한직업"]
    },
    "ESTJ": {
        "books": ["페인트", "완득이"],
        "movies": ["국제시장", "어벤져스: 엔드게임"]
    },
    "ESFJ": {
        "books": ["체리새우: 비밀글입니다", "불편한 편의점"],
        "movies": ["국제시장", "겨울왕국"]
    },
    "ENFJ": {
        "books": ["행운이 너에게 다가오는 중", "체리새우: 비밀글입니다"],
        "movies": ["신과함께-죄와 벌", "겨울왕국 2"]
    },
    "ENTJ": {
        "books": ["시간을 파는 상점", "유원"],
        "movies": ["어벤져스: 엔드게임", "인터스텔라"]
    }
}

# -----------------------------
# MBTI 선택
# -----------------------------
st.markdown("### 🧩 나의 MBTI는 무엇일까?")

mbti_list = list(recommendations.keys())

selected_mbti = st.selectbox(
    "나의 MBTI를 선택해 줘!",
    mbti_list,
    index=0
)

if st.button("🎁 내 취향 추천받기!", use_container_width=True):

    st.session_state["show_result"] = True
    st.session_state["selected_mbti"] = selected_mbti

# -----------------------------
# 추천 결과
# -----------------------------
if st.session_state.get("show_result", False):

    mbti = st.session_state["selected_mbti"]
    result = recommendations[mbti]

    st.balloons()

    st.divider()

    st.markdown(
        f"<h2 style='text-align:center;color:#6941C6;'>💜 {mbti}를 위한 추천 결과!</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;'>오늘의 나를 위한 특별한 콘텐츠를 만나봐요 ✨</p>",
        unsafe_allow_html=True
    )

    # 책 추천
    st.header("📚 나에게 어울리는 책 BEST 2")

    book_cols = st.columns(2)

    for i, title in enumerate(result["books"]):
        book = books[title]

        with book_cols[i]:
            st.markdown('<div class="book-card">', unsafe_allow_html=True)
            st.subheader(f"📖 {title}")
            st.write(f"✍️ 작가: {book['author']}")
            st.write(f"🏷️ 장르: {book['genre']}")
            st.write(book["desc"])
            st.info("💡 " + book["reason"])
            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # 영화 추천
    st.header("🎬 나에게 어울리는 영화 BEST 2")

    movie_cols = st.columns(2)

    for i, title in enumerate(result["movies"]):
        movie = movies[title]

        with movie_cols[i]:
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)
            st.subheader(f"🍿 {title}")
            st.write(f"👥 누적 관객: {movie['audience']}")
            st.write(f"🔖 관람 등급: {movie['rating']}")
            st.write(f"🎭 장르: {movie['genre']}")
            st.write(movie["desc"])
            st.info("💡 " + movie["reason"])
            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.success("🎉 오늘의 책과 영화 추천이 완료되었어요!")

    st.caption(
        "※ MBTI 추천은 재미와 취향 탐색을 위한 참고 자료입니다. "
        "사람마다 좋아하는 책과 영화는 다를 수 있어요."
    )

    if st.button("🔄 다른 MBTI도 확인하기"):
        st.session_state["show_result"] = False
        st.rerun()

# -----------------------------
# 하단 안내
# -----------------------------
st.divider()

st.markdown(
    "<div style='text-align:center;color:#888;'>"
    "📚 책으로 성장하고 🎬 영화로 즐기는 하루!<br>"
    "MBTI 취향 저격 추천소 © 2026"
    "</div>",
    unsafe_allow_html=True
)
