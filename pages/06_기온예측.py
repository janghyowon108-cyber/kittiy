
# ==========================================
# 7. 선형회귀 알고리즘 직접 구현
# ==========================================

# 연도와 평균기온 데이터
x_values = month_df["연도"].astype(float).tolist()
y_values = month_df["평균기온(℃)"].astype(float).tolist()

# 평균 계산
x_mean = sum(x_values) / len(x_values)
y_mean = sum(y_values) / len(y_values)

# 기울기 계산
numerator = sum(
    (x - x_mean) * (y - y_mean)
    for x, y in zip(x_values, y_values)
)

denominator = sum(
    (x - x_mean) ** 2
    for x in x_values
)

if denominator == 0:
    st.error("연도 데이터가 중복되어 회귀분석을 할 수 없습니다.")
    st.stop()

slope = numerator / denominator

# y절편 계산
intercept = y_mean - slope * x_mean

# 미래 기온 예측
predicted_temperature = (
    slope * forecast_year + intercept
)

# 과거 데이터 예측값
fitted_values = [
    slope * x + intercept
    for x in x_values
]

# 결정계수 R² 계산
ss_res = sum(
    (actual - predicted) ** 2
    for actual, predicted in zip(y_values, fitted_values)
)

ss_tot = sum(
    (actual - y_mean) ** 2
    for actual in y_values
)

r_squared = (
    1 - ss_res / ss_tot
    if ss_tot != 0 else 0
)


# ==========================================
# 8. 회귀선 데이터 만들기
# ==========================================

line_years = list(
    range(
        int(month_df["연도"].min()),
        forecast_year + 1
    )
)

line_df = pd.DataFrame({
    "연도": line_years
})

line_df["회귀선 기온"] = (
    slope * line_df["연도"] + intercept
)
