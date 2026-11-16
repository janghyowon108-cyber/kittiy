
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from collections import Counter

# ----------------------------------
# 1. 페이지 설정
# ----------------------------------

st.set_page_config(
    page_title="AI 붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측 시스템")

st.write(
    "세 가지 머신러닝 분류 알고리즘을 선택하여 "
    "붓꽃 품종을 예측해 보세요!"
)

st.divider()

# ----------------------------------
# 2. CSV 파일 불러오기
# ----------------------------------

@st.cache_data
def load_data():

    current_folder = Path(__file__).resolve().parent

    possible_paths = [
        current_folder.parent / "Iris.csv",
        current_folder / "Iris.csv",
        Path.cwd() / "Iris.csv"
    ]

    csv_path = None

    for path in possible_paths:
        if path.exists():
            csv_path = path
            break

    if csv_path is None:
        st.error("Iris.csv 파일을 찾을 수 없습니다.")

        st.write("검색한 위치:")
        for path in possible_paths:
            st.code(str(path))

        st.stop()

    try:
        data = pd.read_csv(csv_path, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(csv_path, encoding="utf-8-sig")

    required_columns = [
        "꽃잎 길이",
        "꽃잎 너비",
        "품종"
    ]

    if not all(col in data.columns for col in required_columns):
        st.error("CSV 파일의 컬럼명을 확인해주세요.")
        st.write(data.columns.tolist())
        st.stop()

    return data


df = load_data()

# ----------------------------------
# 3. 학습 데이터 설정
# ----------------------------------

feature_cols = ["꽃잎 길이", "꽃잎 너비"]
target_col = "품종"

X = df[feature_cols]
y = df[target_col]

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

colors = {
    "Iris-setosa": "#3498DB",
    "Iris-versicolor": "#2ECC71",
    "Iris-virginica": "#9B59B6"
}

# ----------------------------------
# 4. 입력 범위 설정
# ----------------------------------

length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

# ----------------------------------
# 5. 알고리즘 선택
# ----------------------------------

st.subheader("🧠 분류 알고리즘 선택")

algorithm = st.selectbox(
    "사용할 머신러닝 알고리즘을 선택하세요.",
    [
        "KNN (K-최근접 이웃)",
        "Random Forest (랜덤 포레스트)",
        "SVM (서포트 벡터 머신)"
    ]
)

# ----------------------------------
# 6. 세 가지 모델 생성
# ----------------------------------

models = {

    "KNN (K-최근접 이웃)": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", KNeighborsClassifier(
            n_neighbors=5
        ))
    ]),

    "Random Forest (랜덤 포레스트)": RandomForestClassifier(
        n_estimators=100,
        random_state=42
    ),

    "SVM (서포트 벡터 머신)": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            probability=True,
            random_state=42
        ))
    ])
}

# 선택한 모델 학습
model = models[algorithm]
model.fit(X, y)

# ----------------------------------
# 7. 사용자 입력
# ----------------------------------

st.divider()

st.subheader("✏️ 붓꽃 측정값 입력")

st.info(
    f"""
    입력 가능한 값의 범위

    🌷 꽃잎 길이: {length_min:.1f} ~ {length_max:.1f} cm

    🌷 꽃잎 너비: {width_min:.1f} ~ {width_max:.1f} cm
    """
)

col1, col2 = st.columns(2)

with col1:

    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=1.4,
        step=0.1,
        format="%.1f"
    )

with col2:

    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=0.2,
        step=0.1,
        format="%.1f"
    )

input_data = pd.DataFrame(
    [[petal_length, petal_width]],
    columns=feature_cols
)

# ----------------------------------
# 8. 품종 예측
# ----------------------------------

prediction = model.predict(input_data)[0]

st.divider()

st.subheader("🤖 AI 예측 결과")

st.success(
    f"{species_emojis[prediction]} 예측 품종: "
    f"{species_names[prediction]}"
)

st.write(f"사용한 알고리즘: **{algorithm}**")

result1, result2 = st.columns(2)

result1.metric(
    "꽃잎 길이",
    f"{petal_length:.1f} cm"
)

result2.metric(
    "꽃잎 너비",
    f"{petal_width:.1f} cm"
)

# ----------------------------------
# 9. 품종 예측 확률
# ----------------------------------

st.subheader("📊 품종별 예측 확률")

probabilities = model.predict_proba(input_data)[0]

prob_df = pd.DataFrame({
    "품종": [
        species_names[name]
        for name in model.classes_
    ],
    "예측 확률": probabilities
})

st.bar_chart(
    prob_df.set_index("품종"),
    y="예측 확률"
)

# ----------------------------------
# 10. 붓꽃 분포 그래프
# ----------------------------------

st.divider()

st.subheader("📈 붓꽃 품종 분포 그래프")

st.write(
    "가로축: 꽃잎 길이 / 세로축: 꽃잎 너비"
)

fig = go.Figure()

# 실제 붓꽃 데이터
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

# 사용자 입력값: 형광 핑크 별
fig.add_trace(
    go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers",
        name="내가 입력한 값",
        marker=dict(
            symbol="star",
            size=27,
            color="#FF1493",
            line=dict(
                color="#FF69B4",
                width=2
            )
        ),
        hovertemplate=(
            "사용자 입력값<br>"
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

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------
# 11. 알고리즘별 작동 원리
# ----------------------------------

st.divider()

st.header("📚 선택한 알고리즘의 작동 원리")

# ==================================
# KNN 설명
# ==================================

if algorithm == "KNN (K-최근접 이웃)":

    st.subheader("🔵 KNN (K-Nearest Neighbors)")

    st.write("""
    KNN은 새로운 데이터와 가장 가까운 K개의 데이터를
    찾아서 품종을 예측하는 알고리즘입니다.

    이번 프로그램에서는 K=5를 사용합니다.
    """)

    st.markdown("### ① 가까운 데이터 5개 찾기")

    scaler = model.named_steps["scaler"]
    knn = model.named_steps["classifier"]

    scaled_input = scaler.transform(input_data)
    scaled_X = scaler.transform(X)

    distances, indices = knn.kneighbors(
        scaled_input
    )

    neighbors = df.iloc[indices[0]].copy()

    neighbors["거리"] = distances[0]
    neighbors["순위"] = range(1, 6)

    st.write("사용자 입력값과 가까운 데이터 5개입니다.")

    st.dataframe(
        neighbors[
            [
                "순위",
                "꽃잎 길이",
                "꽃잎 너비",
                "품종",
                "거리"
            ]
        ].round(3),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### ② 주변 이웃의 투표 결과")

    votes = neighbors["품종"].value_counts()

    vote_df = pd.DataFrame({
        "품종": [
            species_names[s]
            for s in votes.index
        ],
        "투표 수": votes.values
    })

    st.bar_chart(
        vote_df.set_index("품종")
    )

    st.markdown("### ③ 최종 품종 결정")

    st.success(
        f"가장 많은 투표를 받은 품종: "
        f"{species_names[prediction]}"
    )

    st.info(
        "가까운 이웃 5개 중 가장 많이 등장한 "
        "품종을 최종 결과로 선택합니다."
    )

# ==================================
# Random Forest 설명
# ==================================

elif algorithm == "Random Forest (랜덤 포레스트)":

    st.subheader("🌳 Random Forest (랜덤 포레스트)")

    st.write("""
    랜덤 포레스트는 여러 개의 의사결정나무를 만들어
    각각 품종을 예측하게 한 뒤 결과를 종합하는 알고리즘입니다.

    이번 프로그램에서는 100개의 의사결정나무를 사용합니다.
    """)

    st.markdown("### ① 여러 개의 의사결정나무 생성")

    st.write("""
    각각의 나무는 학습 데이터의 일부를 이용하여
    서로 다른 분류 기준을 학습합니다.
    """)

    st.metric(
        "생성한 의사결정나무 수",
        "100개"
    )

    st.markdown("### ② 각 나무의 예측 결과")

    tree_predictions = [
        tree.predict(input_data)[0]
        for tree in model.estimators_
    ]

    tree_votes = Counter(tree_predictions)

    tree_df = pd.DataFrame({
        "품종": [
            species_names[s]
            for s in tree_votes.keys()
        ],
        "투표 수": list(tree_votes.values())
    })

    st.bar_chart(
        tree_df.set_index("품종")
    )

    st.markdown("### ③ 다수결로 최종 결정")

    st.write(
        "100개의 의사결정나무가 내린 예측 결과를 "
        "종합하여 최종 품종을 결정합니다."
    )

    st.success(
        f"최종 예측 품종: {species_names[prediction]}"
    )

# ==================================
# SVM 설명
# ==================================

elif algorithm == "SVM (서포트 벡터 머신)":

    st.subheader("🟣 SVM (Support Vector Machine)")

    st.write("""
    SVM은 서로 다른 품종의 데이터를 구분하는
    가장 적절한 경계를 찾는 분류 알고리즘입니다.
    """)

    st.markdown("### ① 데이터 분포 확인")

    st.write("""
    꽃잎 길이와 꽃잎 너비를 기준으로
    세 가지 붓꽃 품종이 어디에 분포하는지 학습합니다.
    """)

    st.markdown("### ② 최적의 분류 경계 찾기")

    st.write("""
    SVM은 품종 사이를 구분하는 경계를 학습합니다.

    경계와 가장 가까운 데이터인 서포트 벡터를 기준으로
    데이터 사이의 간격(Margin)을 최대화합니다.
    """)

    st.markdown("### ③ 새로운 데이터 분류")

    st.write("""
    새로운 붓꽃 데이터가 입력되면 학습된 분류 경계를
    이용하여 어떤 품종에 속하는지 예측합니다.

    이번 프로그램에서는 RBF 커널을 사용하여
    직선으로 나누기 어려운 비선형 관계도 학습할 수 있습니다.
    """)

    st.success(
        f"최종 예측 품종: {species_names[prediction]}"
    )

# ----------------------------------
# 12. 데이터 정보
# ----------------------------------

st.divider()

st.subheader("📚 학습 데이터 정보")

c1, c2, c3 = st.columns(3)

c1.metric("전체 데이터", f"{len(df)}개")
c2.metric("붓꽃 품종", f"{df['품종'].nunique()}종")
c3.metric("사용 알고리즘", "3개")

st.caption(
    "Iris 데이터의 꽃잎 길이와 너비를 이용하여 "
    "세 가지 머신러닝 분류 알고리즘을 비교하는 프로그램입니다."
)

