import pandas as pd
import pickle
from sklearn.model_selection import train_test_split, RandomizedSearchCV
import xgboost as xgb


import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False

df = pd.read_excel('建模数据(全部数据).xlsx')

# 分出目标变量和自变量
X = df.loc[:,(df.columns!='房屋总价')&(df.columns!='房屋每平米价')]
y = df.loc[:,'房屋总价']

# 划分训练测试集
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3,random_state=42)

# 建模过程
params = {
    'n_estimators': [400, 500, 600, 700, 800],
    'max_depth': [3, 4, 5, 6, 7, 8, 9, 10],
    'min_child_weight': [1, 2, 3, 4, 5, 6],
    'gamma': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
    'subsample': [0.6, 0.7, 0.8, 0.9],
    'colsample_bytree': [0.6, 0.7, 0.8, 0.9],
    'reg_alpha': [0.05, 0.1, 1, 2, 3],
    'reg_lambda': [0.05, 0.1, 1, 2, 3],
    'learning_rate': [0.01, 0.05, 0.07, 0.1, 0.2]
}

import time
s = time.time()
model = xgb.XGBRegressor()
optimized_model = RandomizedSearchCV(model, params, cv=5, n_jobs=-1)
optimized_model.fit(X_train, y_train)
e = time.time()
print('调参用时（min）：',(e-s)/60)
score = optimized_model.score(X_test,y_test)
print(score)
score = ",{:.6f}".format(score)
pickle.dump(optimized_model, open('boostingmodel.pkl','wb'))
with open("R_score.txt","a") as f:
    f.write(score)


