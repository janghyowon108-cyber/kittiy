
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
# 1. 페이지 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.write(
    "붓꽃의 꽃잎과 꽃받침 정보를 입력하면 "
    "세 가지 머신러닝 알고리즘이 품종을 예측합니다."
)


# --------------------------------------------------
# 2. 붓꽃 데이터 불러오기
# --------------------------------------------------

@st.cache_data
def load_iris_data():
    iris = load_iris()

    df = pd.DataFrame(
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

    df["품종"] = [
        species_map[int(value)]
        for value in iris.target
    ]

    return df


df = load_iris_data()

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
# 3. 머신러닝 알고리즘 만들기
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
# 4. 품종 예측 및 결과 비교 함수
# --------------------------------------------------

def run_prediction(x_column, y_column, x_value, y_value):

    X = df[[x_column, y_column]]
    y = df["품종"]

    # 학습 데이터와 테스트 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    models = create_models()

    predictions = []
    accuracies = []

    input_data = pd.DataFrame(
        [[x_value, y_value]],
        columns=[x_column, y_column]
    )

    for model_name, model in models.items():

        # 모델 학습
        model.fit(X_train, y_train)

        # 사용자 입력값 예측
        prediction = model.predict(input_data)[0]

        # 테스트 데이터 정확도
        accuracy = model.score(X_test, y_test)

        predictions.append({
            "알고리즘": model_name,
            "예측 품종": prediction,
            "정확도": accuracy
        })

        accuracies.append({
            "알고리즘": model_name,
            "테스트 정확도": accuracy * 100
        })

    result_df = pd.DataFrame(predictions)
    accuracy_df = pd.DataFrame(accuracies)

    return result_df, accuracy_df


# --------------------------------------------------
# 5. 그래프 그리기
# --------------------------------------------------

def draw_scatter_graph(x_column, y_column, x_value, y_value):

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
        title="붓꽃 데이터 분포와 입력한 꽃의 위치"
    )

    # 사용자가 입력한 꽃의 위치
    fig.add_scatter(
        x=[x_value],
        y=[y_value],
        mode="markers",
        name="내가 입력한 붓꽃",
        marker=dict(
            symbol="star",
            size=22,
            color="#FF1493",
            line=dict(
                color="white",
                width=2
            )
        ),
        hovertemplate=(
            "내가 입력한 붓꽃<br>"
            + x_column + ": %{x:.1f}cm<br>"
            + y_column + ": %{y:.1f}cm"
            + "<extra></extra>"
        )
    )

    fig.update_layout(
        height=550,
        xaxis_title=x_column + " (cm)",
        yaxis_title=y_column + " (cm)",
        legend_title="붓꽃 품종",
        template="plotly_white"
    )

    return fig


# --------------------------------------------------
# 6. 알고리즘 작동 원리 설명
# --------------------------------------------------

def show_algorithm_explanations():

    st.subheader("🤖 세 가지 알고리즘의 작동 원리")

    with st.expander("① KNN - 가까운 이웃을 찾아 예측하는 알고리즘", expanded=True):

        st.markdown("""
        **KNN(K-Nearest Neighbors)은 주변의 가까운 데이터를 참고하는 방법입니다.**

        1. 입력한 붓꽃의 꽃잎 또는 꽃받침 정보를 확인합니다.
        2. 기존 붓꽃 데이터 중 입력값과 가까운 데이터 5개를 찾습니다.
        3. 가장 많이 등장한 품종을 최종 예측 결과로 선택합니다.

        📌 **쉽게 말하면?**

        새로운 학생이 전학 왔을 때 주변에 있는 친구 5명의 특징을 살펴보고
        가장 비슷한 유형을 판단하는 것과 비슷합니다.
        """)

    with st.expander("② 랜덤 포레스트 - 여러 개의 의사결정 나무를 활용"):

        st.markdown("""
        **랜덤 포레스트(Random Forest)는 여러 개의 의사결정 나무를 사용하는 방법입니다.**

        1. 여러 개의 의사결정 나무를 만듭니다.
        2. 각각의 나무가 입력한 붓꽃의 품종을 예측합니다.
        3. 여러 나무의 예측 결과를 모읍니다.
        4. 가장 많은 표를 받은 품종을 최종 결과로 선택합니다.

        📌 **쉽게 말하면?**

        여러 명의 전문가에게 의견을 물어보고
        가장 많은 사람이 선택한 답을 결정하는 것과 비슷합니다.
        """)

    with st.expander("③ SVM - 품종을 구분하는 경계를 찾는 알고리즘"):

        st.markdown("""
        **SVM(Support Vector Machine)은 서로 다른 품종을 구분하는 경계를 찾는 방법입니다.**

        1. 기존 붓꽃 데이터를 품종별로 살펴봅니다.
        2. 서로 다른 품종을 가장 잘 구분할 수 있는 경계를 찾습니다.
        3. 새로운 붓꽃 데이터가 어느 영역에 위치하는지 확인합니다.
        4. 해당 영역에 맞는 품종을 예측합니다.

        📌 **쉽게 말하면?**

        서로 다른 두 그룹의 학생들 사이에 선을 그어
        새로운 학생이 어느 그룹에 가까운지 판단하는 것과 비슷합니다.
        """)


# --------------------------------------------------
# 7. 예측 결과 비교
# --------------------------------------------------

def show_comparison(result_df, accuracy_df):

    st.subheader("📊 세 가지 알고리즘의 예측 결과 비교")

    st.write("각 알고리즘이 어떤 품종으로 예측했는지 확인해 보세요.")

    display_df = result_df.copy()

    display_df["예측 품종"] = display_df["예측 품종"].apply(
        lambda name: species_emojis[name] + " " + name
    )

    display_df["정확도"] = display_df["정확도"].apply(
        lambda value: f"{value * 100:.1f}%"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # 품종별 예측 횟수
    count_df = (
        result_df["예측 품종"]
        .value_counts()
        .reindex(species_order, fill_value=0)
        .rename_axis("품종")
        .reset_index(name="예측 알고리즘 수")
    )

    st.write("### 🏆 알고리즘별 예측 결과 분포")

    fig = px.bar(
        count_df,
        x="품종",
        y="예측 알고리즘 수",
        color="품종",
        category_orders={"품종": species_order},
        color_discrete_sequence=[
            "#F4A6C1",
            "#8BC7E8",
            "#A58BE8"
        ],
        text="예측 알고리즘 수"
    )

    fig.update_layout(
        height=350,
        showlegend=False,
        yaxis=dict(
            tickmode="linear",
            dtick=1,
            range=[0, 3]
        ),
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # 테스트 정확도 비교
    st.write("### 🎯 알고리즘별 테스트 정확도")

    accuracy_fig = px.bar(
        accuracy_df,
        x="알고리즘",
        y="테스트 정확도",
        color="알고리즘",
        text="테스트 정확도",
        color_discrete_sequence=[
            "#F4A6C1",
            "#8BC7E8",
            "#A58BE8"
        ]
    )

    accuracy_fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    accuracy_fig.update_layout(
        height=350,
        yaxis_title="정확도 (%)",
        xaxis_title="알고리즘",
        yaxis_range=[0, 110],
        showlegend=False,
        template="plotly_white"
    )

    st.plotly_chart(
        accuracy_fig,
        use_container_width=True
    )

    st.caption(
        "※ 테스트 정확도는 학습에 사용하지 않은 테스트 데이터에서 "
        "얼마나 정확하게 예측했는지를 나타냅니다. "
        "이번 결과는 선택한 두 가지 속성만 사용한 모델의 결과입니다."
    )


# --------------------------------------------------
# 8. 탭별 예측 화면
# --------------------------------------------------

def make_prediction_tab(
    x_column,
    y_column,
    tab_title
):

    st.header(tab_title)

    st.write(
        "아래 두 가지 속성의 값을 입력하면 "
        "세 가지 알고리즘이 붓꽃 품종을 예측합니다."
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
            key=tab_title + "_x"
        )

    with col2:
        y_value = st.number_input(
            y_column + " (cm)",
            min_value=y_min,
            max_value=y_max,
            value=y_default,
            step=0.1,
            format="%.1f",
            key=tab_title + "_y"
        )

    st.info(
        "입력한 값: "
        + x_column + " "
        + f"{x_value:.1f}cm / "
        + y_column + " "
        + f"{y_value:.1f}cm"
    )

    # 그래프
    st.subheader("📍 붓꽃 데이터 분포")

    fig = draw_scatter_graph(
        x_column,
        y_column,
        x_value,
        y_value
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # 그래프 아래 알고리즘 설명
    show_algorithm_explanations()

    st.divider()

    # 세 알고리즘 예측
    result_df, accuracy_df = run_prediction(
        x_column,
        y_column,
        x_value,
        y_value
    )

    st.subheader("🌸 AI 품종 예측 결과")

    for _, row in result_df.iterrows():

        species = row["예측 품종"]
        emoji = species_emojis[species]

        st.success(
            row["알고리즘"]
            + " 예측 결과: "
            + emoji
            + " "
            + species
        )

    # 결과 비교
    show_comparison(
        result_df,
        accuracy_df
    )


# --------------------------------------------------
# 9. 전체 데이터 정보
# --------------------------------------------------

with st.expander("📚 붓꽃 데이터셋 알아보기"):

    st.write("""
    이 앱은 머신러닝 공부에 자주 사용되는 Iris 붓꽃 데이터셋을 사용합니다.

    붓꽃 데이터에는 세 가지 품종이 있으며,
    각 품종의 꽃받침과 꽃잎 길이 및 너비가 기록되어 있습니다.
    """)

    st.write("전체 데이터 개수:", len(df))

    st.write("품종별 데이터 개수")

    st.dataframe(
        df["품종"].value_counts().rename("데이터 개수"),
        use_container_width=True
    )


# --------------------------------------------------
# 10. 두 가지 속성 조합을 탭으로 구분
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
# 11. 마무리
# --------------------------------------------------

st.divider()

st.caption(
    "🌸 붓꽃 품종 예측 AI | "
    "KNN · Random Forest · SVM"
)
