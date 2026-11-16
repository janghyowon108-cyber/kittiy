
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ----------------------------------
# 1. 페이지 설정
# ----------------------------------

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측")
st.write("꽃잎의 길이와 너비를 입력하면 AI가 붓꽃의 품종을 예측합니다.")

st.divider()

# ----------------------------------
# 2. CSV 파일 불러오기
# ----------------------------------

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더에서 CSV 찾기
    csv_path = Path(__file__).resolve().parent.parent / "Iris.csv"

    if not csv_path.exists():
        csv_path = Path(__file__).resolve().parent / "Iris.csv"

    if not csv_path.exists():
        st.error("Iris.csv 파일을 찾을 수 없습니다.")
        st.stop()

    try:
        data = pd.read_csv(csv_path, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(csv_path, encoding="utf-8-sig")

    return data


df = load_data()

# 사용할 컬럼
feature_cols = ["꽃잎 길이", "꽃잎 너비"]
target_col = "품종"

X = df[feature_cols]
y = df[target_col]

# ----------------------------------
# 3. 입력 범위 계산
# ----------------------------------

length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

# ----------------------------------
# 4. KNN 분류 모델 생성
# ----------------------------------

model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

model.fit(X, y)

# ----------------------------------
# 5. 사용자 입력
# ----------------------------------

st.subheader("✏️ 붓꽃 측정값 입력")

st.info(
    f"""
    📌 입력 가능한 범위

    - 꽃잎 길이: {length_min:.1f} ~ {length_max:.1f} cm
    - 꽃잎 너비: {width_min:.1f} ~ {width_max:.1f} cm
    """
)

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=1.4,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=0.2,
        step=0.1,
        format="%.1f"
    )

# ----------------------------------
# 6. 품종 예측
# ----------------------------------

input_data = pd.DataFrame(
    [[petal_length, petal_width]],
    columns=feature_cols
)

prediction = model.predict(input_data)[0]

st.divider()

st.subheader("🤖 AI 품종 예측 결과")

# 품종별 한글 이름
species_names = {
    "Iris-setosa": "세토사 (Setosa)",
    "Iris-versicolor": "버시컬러 (Versicolor)",
    "Iris-virginica": "버지니카 (Virginica)"
}

species_emojis = {
    "Iris-setosa": "🌼",
    "Iris-versicolor": "🌷",
    "Iris-virginica": "🌺"
}

st.success(
    f"예측된 붓꽃 품종: {species_emojis[prediction]} "
    f"{species_names[prediction]}"
)

result_col1, result_col2 = st.columns(2)

with result_col1:
    st.metric("꽃잎 길이", f"{petal_length:.1f} cm")

with result_col2:
    st.metric("꽃잎 너비", f"{petal_width:.1f} cm")

# ----------------------------------
# 7. 그래프 그리기
# ----------------------------------

st.divider()

st.subheader("📊 붓꽃 품종 분포 및 입력값")

st.write(
    "가로축은 꽃잎 길이, 세로축은 꽃잎 너비입니다."
)

fig = go.Figure()

# 실제 데이터 품종별 표시
colors = {
    "Iris-setosa": "#3498DB",
    "Iris-versicolor": "#2ECC71",
    "Iris-virginica": "#9B59B6"
}

for species in df["품종"].unique():

    species_df = df[df["품종"] == species]

    fig.add_trace(
        go.Scatter(
            x=species_df["꽃잎 길이"],
            y=species_df["꽃잎 너비"],
            mode="markers",
            name=species_names[species],
            marker=dict(
                size=9,
                color=colors[species],
                opacity=0.65
            )
        )
    )

# 사용자가 입력한 값: 형광 핑크 별
fig.add_trace(
    go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers",
        name="내가 입력한 값",
        marker=dict(
            symbol="star",
            size=25,
            color="#FF1493",
            line=dict(
                color="#FF69B4",
                width=2
            )
        ),
        hovertemplate=(
            "내 입력값<br>"
            "꽃잎 길이: %{x:.1f}cm<br>"
            "꽃잎 너비: %{y:.1f}cm"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    xaxis_title="꽃잎 길이 (cm)",
    yaxis_title="꽃잎 너비 (cm)",
    height=600,
    template="plotly_white",
    hovermode="closest",
    legend_title="붓꽃 품종"
)

fig.update_xaxes(
    range=[length_min - 0.3, length_max + 0.3]
)

fig.update_yaxes(
    range=[width_min - 0.15, width_max + 0.15]
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------
# 8. 데이터 정보
# ----------------------------------

st.divider()

st.subheader("📚 학습 데이터 정보")

c1, c2, c3 = st.columns(3)

c1.metric("전체 데이터", f"{len(df)}개")
c2.metric("붓꽃 품종", f"{df['품종'].nunique()}종")
c3.metric("분류 알고리즘", "KNN")

st.caption(
    "본 예측은 Iris 데이터의 꽃잎 길이와 너비를 "
    "이용한 KNN 분류 결과입니다."
)
