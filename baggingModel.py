import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PowerTransformer
from sklearn.ensemble import RandomForestRegressor 
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
import pickle

df = pd.read_excel('建模数据(全部数据).xlsx')
df_tran = pd.read_excel('连续特征转化前数值.xlsx')

#分出目标变量和自变量
x=df.loc[:,(df.columns!='房屋总价')&(df.columns!='房屋每平米价')]
y=df.loc[:,'房屋总价']

#标准化
scale_x=StandardScaler()
x.loc[:,:]=scale_x.fit_transform(x)
scale_y=StandardScaler()
y2=np.array(y).reshape(-1,1)
y1=scale_y.fit_transform(y2)
y.loc[:]=[i for k in y1 for i in k]
x_train1,x_test1,y_train1,y_test1 = train_test_split(x,y,test_size = 0.4,random_state = 1)

#建模过程
rfc_params = {"n_estimators": [*range(10,100+1)],
          "max_depth": [*range(1,30+1)],
          'bootstrap': [False, True],
          'oob_score': [False],
          'max_features': ['auto', 'sqrt', 'log2'],
}

rfc = RandomForestRegressor()
br_gs = RandomizedSearchCV(rfc, rfc_params, cv=5, verbose=1,n_jobs=-1)
br_gs.fit(x_train1, y_train1)
print(br_gs.best_params_, br_gs.best_score_)
score =br_gs.score(x_test1,y_test1)
score = ",{:.6f}".format(score)
pickle.dump(br_gs, open('baggingmodel.pkl','wb'))
with open("R_score.txt","a") as f:
    f.write(score)


