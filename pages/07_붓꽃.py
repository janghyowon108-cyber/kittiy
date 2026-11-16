

import streamlit as st
import pandas as pd
import plotly.express as px

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC


# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.markdown("""
두 가지 꽃의 속성을 입력하고 세 가지 머신러닝 알고리즘으로
붓꽃의 품종을 예측해 보세요!
""")


# --------------------------------------------------
# 2. 데이터 불러오기
# --------------------------------------------------

@st.cache_data
def load_data():

    iris = load_iris()

    data = pd.DataFrame(
        iris.data,
        columns=[
            "꽃받침 길이",
            "꽃받침 너비",
            "꽃잎 길이",
            "꽃잎 너비"
        ]
    )

    species_map = {
        0: "세토사 (Setosa)",
        1: "버시컬러 (Versicolor)",
        2: "버지니카 (Virginica)"
    }

    data["품종"] = [
        species_map[int(value)]
        for value in iris.target
    ]

    return data


df = load_data()

species_order = [
    "세토사 (Setosa)",
    "버시컬러 (Versicolor)",
    "버지니카 (Virginica)"
]

species_emojis = {
    "세토사 (Setosa)": "🌼",
    "버시컬러 (Versicolor)": "🌷",
    "버지니카 (Virginica)": "🌺"
}


# --------------------------------------------------
# 3. 알고리즘 만들기
# --------------------------------------------------

def create_models():

    models = {
        "KNN": Pipeline([
            ("scaler", StandardScaler()),
            ("model", KNeighborsClassifier(n_neighbors=5))
        ]),

        "랜덤 포레스트": RandomForestClassifier(
            n_estimators=100,
            random_state=42
        ),

        "SVM": Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale"
            ))
        ])
    }

    return models


# --------------------------------------------------
# 4. 학습 및 예측
# --------------------------------------------------

def predict_iris(x_column, y_column, x_value, y_value):

    X = df[[x_column, y_column]]
    y = df["품종"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    models = create_models()

    input_data = pd.DataFrame(
        [[x_value, y_value]],
        columns=[x_column, y_column]
    )

    results = []

    for name, model in models.items():

        # 모델 학습
        model.fit(X_train, y_train)

        # 사용자 입력값 예측
        prediction = model.predict(input_data)[0]

        # 테스트 데이터 정확도
        accuracy = model.score(X_test, y_test)

        results.append({
            "알고리즘": name,
            "예측 품종": prediction,
            "정확도": accuracy
        })

    return pd.DataFrame(results)


# --------------------------------------------------
# 5. 데이터 분포 그래프
# --------------------------------------------------

def draw_graph(x_column, y_column, x_value, y_value):

    fig = px.scatter(
        df,
        x=x_column,
        y=y_column,
        color="품종",
        category_orders={"품종": species_order},
        color_discrete_sequence=[
            "#F4A6C1",
            "#8BC7E8",
            "#A58BE8"
        ],
        title="붓꽃 데이터 분포"
    )

    # 사용자가 입력한 데이터 표시
    fig.add_scatter(
        x=[x_value],
        y=[y_value],
        mode="markers",
        name="내가 입력한 붓꽃",
        marker=dict(
            symbol="star",
            size=23,
            color="#FF1493",
            line=dict(color="white", width=2)
        ),
        hovertemplate=(
            "내가 입력한 붓꽃<br>"
            + x_column + ": %{x:.1f}cm<br>"
            + y_column + ": %{y:.1f}cm"
            + "<extra></extra>"
        )
    )

    fig.update_layout(
        height=500,
        xaxis_title=x_column + " (cm)",
        yaxis_title=y_column + " (cm)",
        legend_title="품종",
        template="plotly_white"
    )

    return fig


# --------------------------------------------------
# 6. 알고리즘별 작동 원리
# --------------------------------------------------

def show_algorithm_principles():

    st.subheader("🤖 세 가지 알고리즘의 작동 원리")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ① KNN")
        st.markdown("**가까운 이웃 찾기**")
        st.write("""
        - 기존 데이터와 새로운 데이터의 거리를 계산합니다.
        - 가장 가까운 데이터 5개를 찾습니다.
        - 가장 많이 등장한 품종으로 예측합니다.
        """)
        st.info("📌 주변 이웃 5개의 투표로 결정!")

    with col2:
        st.markdown("### ② 랜덤 포레스트")
        st.markdown("**여러 의사결정 나무**")
        st.write("""
        - 여러 개의 의사결정 나무를 만듭니다.
        - 각각의 나무가 품종을 예측합니다.
        - 가장 많은 표를 받은 품종을 선택합니다.
        """)
        st.info("📌 100개 나무의 의견을 모아 결정!")

    with col3:
        st.markdown("### ③ SVM")
        st.markdown("**품종 구분 경계 찾기**")
        st.write("""
        - 품종을 구분할 수 있는 경계를 학습합니다.
        - 새로운 데이터의 위치를 확인합니다.
        - 해당 위치에 맞는 품종을 예측합니다.
        """)
        st.info("📌 데이터 사이의 경계를 학습!")


# --------------------------------------------------
# 7. 알고리즘별 예측 결과 표시
# --------------------------------------------------

def show_individual_results(results):

    st.subheader("🌸 알고리즘별 예측 결과")

    col1, col2, col3 = st.columns(3)

    columns = [col1, col2, col3]

    for column, (_, row) in zip(columns, results.iterrows()):

        name = row["알고리즘"]
        species = row["예측 품종"]
        accuracy = row["정확도"] * 100

        emoji = species_emojis[species]

        with column:

            st.markdown(f"### {name}")

            st.metric(
                label="예측 품종",
                value=emoji + " " + species
            )

            st.metric(
                label="테스트 정확도",
                value=f"{accuracy:.1f}%"
            )

            st.success(
                name + " 알고리즘의 예측 결과입니다."
            )


# --------------------------------------------------
# 8. 세 알고리즘 결과 비교
# --------------------------------------------------

def show_comparison(results):

    st.divider()

    st.subheader("🏆 세 가지 알고리즘 결과 비교")

    # 결과 표
    comparison_df = results.copy()

    comparison_df["예측 품종"] = comparison_df[
        "예측 품종"
    ].apply(
        lambda x: species_emojis[x] + " " + x
    )

    comparison_df["정확도"] = comparison_df[
        "정확도"
    ].apply(
        lambda x: f"{x * 100:.1f}%"
    )

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    # 예측 품종 비교
    st.markdown("### 📊 알고리즘별 예측 품종")

    count_df = (
        results["예측 품종"]
        .value_counts()
        .reindex(species_order, fill_value=0)
        .rename_axis("품종")
        .reset_index(name="예측 알고리즘 수")
    )

    fig1 = px.bar(
        count_df,
        x="품종",
        y="예측 알고리즘 수",
        color="품종",
        text="예측 알고리즘 수",
        category_orders={"품종": species_order},
        color_discrete_sequence=[
            "#F4A6C1",
            "#8BC7E8",
            "#A58BE8"
        ]
    )

    fig1.update_layout(
        height=350,
        showlegend=False,
        yaxis=dict(
            tickmode="linear",
            dtick=1,
            range=[0, 3]
        ),
        template="plotly_white"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # 정확도 비교
    st.markdown("### 🎯 알고리즘별 테스트 정확도")

    accuracy_df = results[
        ["알고리즘", "정확도"]
    ].copy()

    accuracy_df["정확도(%)"] = (
        accuracy_df["정확도"] * 100
    )

    fig2 = px.bar(
        accuracy_df,
        x="알고리즘",
        y="정확도(%)",
        color="알고리즘",
        text="정확도(%)",
        color_discrete_sequence=[
            "#F4A6C1",
            "#8BC7E8",
            "#A58BE8"
        ]
    )

    fig2.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig2.update_layout(
        height=350,
        yaxis_title="정확도 (%)",
        yaxis_range=[0, 110],
        showlegend=False,
        template="plotly_white"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # 세 알고리즘의 예측 일치 여부
    unique_predictions = results["예측 품종"].nunique()

    st.markdown("### 💡 예측 결과 분석")

    if unique_predictions == 1:

        species = results.iloc[0]["예측 품종"]

        st.success(
            "세 가지 알고리즘이 모두 "
            + species
            + "으로 예측했습니다! 🎉"
        )

    else:

        st.warning(
            "알고리즘에 따라 예측 결과가 다릅니다. "
            "각 알고리즘의 작동 방식과 데이터 특징을 비교해 보세요."
        )

    st.caption(
        "※ 테스트 정확도는 학습에 사용하지 않은 데이터에 대한 "
        "예측 성능입니다. 사용자 입력값의 예측 결과와는 별개입니다."
    )


# --------------------------------------------------
# 9. 속성별 예측 화면
# --------------------------------------------------

def make_prediction_tab(x_column, y_column, tab_name):

    st.header(tab_name)

    st.write(
        "두 가지 속성의 값을 입력해 주세요."
    )

    col1, col2 = st.columns(2)

    x_min = float(df[x_column].min())
    x_max = float(df[x_column].max())

    y_min = float(df[y_column].min())
    y_max = float(df[y_column].max())

    x_default = float(df[x_column].mean())
    y_default = float(df[y_column].mean())

    with col1:

        x_value = st.number_input(
            x_column + " (cm)",
            min_value=x_min,
            max_value=x_max,
            value=x_default,
            step=0.1,
            format="%.1f",
            key=tab_name + "_x"
        )

    with col2:

        y_value = st.number_input(
            y_column + " (cm)",
            min_value=y_min,
            max_value=y_max,
            value=y_default,
            step=0.1,
            format="%.1f",
            key=tab_name + "_y"
        )

    st.info(
        f"입력한 값: {x_column} {x_value:.1f}cm / "
        f"{y_column} {y_value:.1f}cm"
    )

    # 데이터 분포 그래프
    st.subheader("📍 붓꽃 데이터 분포 그래프")

    fig = draw_graph(
        x_column,
        y_column,
        x_value,
        y_value
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # 그래프 하단에 알고리즘 작동 원리
    show_algorithm_principles()

    st.divider()

    # 세 알고리즘 예측
    results = predict_iris(
        x_column,
        y_column,
        x_value,
        y_value
    )

    # 알고리즘별 결과를 한 화면에 표시
    show_individual_results(results)

    # 마지막에 전체 결과 비교
    show_comparison(results)


# --------------------------------------------------
# 10. 데이터 설명
# --------------------------------------------------

with st.expander("📚 붓꽃 데이터셋 알아보기"):

    st.write("""
    붓꽃 데이터셋은 머신러닝 학습에 널리 사용되는 데이터입니다.

    세 가지 붓꽃 품종의 꽃받침과 꽃잎의 길이 및 너비가
    기록되어 있습니다.
    """)

    st.write("전체 데이터 수:", len(df))

    st.dataframe(
        df["품종"].value_counts().rename("데이터 수"),
        use_container_width=True
    )


# --------------------------------------------------
# 11. 두 가지 속성 조합 탭
# --------------------------------------------------

tab1, tab2 = st.tabs([
    "🌸 꽃잎 길이 + 꽃잎 너비",
    "🍃 꽃받침 길이 + 꽃받침 너비"
])

with tab1:

    make_prediction_tab(
        "꽃잎 길이",
        "꽃잎 너비",
        "꽃잎 속성 예측"
    )

with tab2:

    make_prediction_tab(
        "꽃받침 길이",
        "꽃받침 너비",
        "꽃받침 속성 예측"
    )


# --------------------------------------------------
# 12. 마무리
# --------------------------------------------------

st.divider()

st.caption(
    "🌸 붓꽃 품종 예측 AI | KNN · Random Forest · SVM"
)
