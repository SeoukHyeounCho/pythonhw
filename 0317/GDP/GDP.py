import pandas as pd
data = {'국가': ['미국', '일본', '영국', '프랑스', '독일', '이탈리아', '캐나다','대한민국', '러시아', '중국', '인도', '인도네시아', '아르헨티나','브라질', '멕시코', '호주', '남아프리카공화국', '사우디아라비아','튀르키예', '유럽연합(EU)'],
'GDP 성장률': [0.9, 0.6, 0.4, 0.5, 1.1, 1.7, 3.9, 1.4, -3.7, 2.9, 6.3,
5.01, 5.9, 3.6, 3.5, 5.9, 4.1, 5.4, 3.9, 1.9],
'인구수': [334, 125, 67.53, 67.65, 83.16, 59.24, 38.44, 51.74, 146, 1412,
1380, 273, 45.81, 213, 126, 25.77, 60.14, 34.11, 84.68, 343]}
df = pd.DataFrame(data)
print(df)


df_numeric = df.select_dtypes(include=[np.number])
pearsonCoef = df_numeric.corr(method='pearson')
print("Pearson Correlation Analysis")
print(pearsonCoef)

spearmanCoef = df_numeric.corr(method='spearman')
print("\nSpearman Correlation Analysis")
print(spearmanCoef)

kendallCoef = df_numeric.corr(method='kendall')
print("\nKendall Correlation Analysis")
print(kendallCoef)


