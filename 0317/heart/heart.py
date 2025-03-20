import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics


col_Names = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach','exang', 'oldpeak', 'slope', 'ca', 'thal', 'label']
df_heart = pd.read_csv('http://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data', names=col_Names)
#df_heart

df_heart.replace('?', np.nan, inplace=True)
df_heart=df_heart.dropna()
#df_heart

train, test = train_test_split(df_heart, test_size=0.3, random_state=0, 
stratify=df_heart['label'])
train_X = train[train.columns[:13]]
train_Y = train[train.columns[13:]]
test_X = test[test.columns[:13]]
test_Y = test[test.columns[13:]]

plt.hist(df_heart.label, bins=4)
ax = sns.heatmap(df_heart.corr( ), annot=True, annot_kws={"size":6})
plt.show( )


model = RandomForestClassifier(n_estimators=100)
model.fit(train_X, train_Y)
pred_RF = model.predict(test_X)
print('랜덤 포레스트 알고리즘 예측 정확도:', metrics.accuracy_score(pred_RF, test_Y))
