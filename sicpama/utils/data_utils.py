import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def detailed_outlier_report(df, z_thresh=3, rare_thresh=0.01, visualize=True):
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(exclude=np.number).columns
    
    print("🧼 [결측치 비율 확인]\n")
    null_ratios = df.isnull().mean()
    for col, ratio in null_ratios.items():
        if ratio > 0:
            msg = "⚠️ 높음" if ratio > 0.3 else "△ 주의"
            print(f" - {col}: {ratio:.1%} {msg}")

    print("\n📊 [숫자형 변수 이상값 리포트]\n")

    for col in num_cols:
        series = df[col].dropna()
        q50 = series.median()
        max_val = series.max()
        min_val = series.min()
        mean = series.mean()
        std = series.std()
        upper_std = mean + 3 * std
        lower_std = mean - 3 * std
        z_scores = np.abs(stats.zscore(series))
        z_outliers = (z_scores > z_thresh).sum()

        # IQR 계산
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        iqr_lower = Q1 - 1.5 * IQR
        iqr_upper = Q3 + 1.5 * IQR
        iqr_outliers = ((series < iqr_lower) | (series > iqr_upper)).sum()

        print(f"📌 {col}")
        print(f" - Median: {q50:.2f}")
        print(f" - Max: {max_val:.2f} / Min: {min_val:.2f}")
        print(f" - Mean ± 3*Std: [{lower_std:.2f}, {upper_std:.2f}]")
        if max_val > upper_std or min_val < lower_std:
            print("   → 🚨 이상값 의심됨 (3*표준편차 범위 초과)")
        else:
            print("   → ✅ 정상 범위 내")

        print(f" - Z-score > {z_thresh}: {z_outliers}건")
        if z_outliers > 0:
            print("   → 🚨 이상값 의심됨 (Z-score 기준)")
        else:
            print("   → ✅ Z-score 이상 없음")

        print(f" - IQR 범위: [{iqr_lower:.2f}, {iqr_upper:.2f}]")
        print(f" - IQR 기준 이상값: {iqr_outliers}건")
        if iqr_outliers > 0:
            print("   → 🚨 이상값 의심됨 (IQR 기준)")
        else:
            print("   → ✅ IQR 기준 이상 없음")

        print("")

        if visualize:
            plt.figure(figsize=(6, 1.5))
            sns.boxplot(x=series, color='skyblue')
            plt.title(f'Boxplot - {col}')
            plt.tight_layout()
            plt.show()

    print("\n📦 [범주형 변수 희귀값 확인] (비율 < {:.1%})".format(rare_thresh))
    for col in cat_cols:
        freq = df[col].value_counts(normalize=True)
        rare_categories = freq[freq < rare_thresh].index
        rare_mask = df[col].isin(rare_categories)
        rare_count = rare_mask.sum()
        rare_ratio = rare_count / len(df)

        if rare_count > 0:
            print(f" - {col}: 희귀값 {rare_count}개 ({rare_ratio:.1%}) → ⚠️ 희귀 범주 존재")
        else:
            print(f" - {col}: ✅ 전부 적정 분포")
