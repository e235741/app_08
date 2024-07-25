import numpy as np

# 標本データ
data = np.array([4, 2, 3, 2, 3, 5, 4, 1])
n = len(data)

# 標本平均と分散
mu_hat = np.mean(data)
sigma_hat_squared = np.var(data)

# モデル1 (µ = 2)
mu_1 = 2
log_likelihood_1 = -n / 2 * np.log(2 * np.pi * sigma_hat_squared) - 1 / (2 * sigma_hat_squared) * np.sum((data - mu_1) ** 2)
aic_1 = 2 * 1 - 2 * log_likelihood_1

# モデル2 (µ 未知)
log_likelihood_2 = -n / 2 * np.log(2 * np.pi * sigma_hat_squared) - 1 / (2 * sigma_hat_squared) * np.sum((data - mu_hat) ** 2)
aic_2 = 2 * 2 - 2 * log_likelihood_2

# 結果表示
print({aic_1})
print(f"AIC of Model 2: {aic_2}")

# AICが最小のモデルを選択
best_model = "Model 1" if aic_1 < aic_2 else "Model 2"
print(f"Best model according to AIC: {best_model}")
