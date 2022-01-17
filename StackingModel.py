import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.svm import SVR
from sklearn.linear_model import ElasticNet, BayesianRidge
from sklearn.kernel_ridge import KernelRidge
from xgboost import XGBRegressor
from mlxtend.regressor import StackingCVRegressor
from sklearn.metrics import r2_score
import pickle

#三折交叉验证，返回r2分数
def r2_cv(model,X,y):
    r2 = cross_val_score(model, X, y, scoring='r2', cv=5)
    return r2

#网格调参类
class grid():
    def __init__(self, model):
        self.model = model

    def grid_get(self, X, y, param_grid):
        grid_search = GridSearchCV(self.model, param_grid, cv=5, scoring="r2") #r2评估指标
        grid_search.fit(X, y)
        return grid_search.best_params_, grid_search.best_score_

#建模过程
df = pd.read_excel('建模数据(全部数据).xlsx')

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
x_train1,x_test1,y_train1,y_test1 = train_test_split(x,y,test_size = 0.4,random_state = 1) #划分训练集与测试集

#从默认参数的十个模型中选取5个最高分的作为第一层强模型，KernelRidge作为第二层模型，为防止过拟合
#十个模型
models = [Ridge(),Lasso(alpha=0.01,max_iter=1000),RandomForestRegressor(),GradientBoostingRegressor(),SVR(),
          ElasticNet(alpha=0.001,max_iter=1000),BayesianRidge(),ExtraTreesRegressor(),XGBRegressor()]
#模型名字
names = [ "Ridge", "Lasso", "RF", "GBR", "SVR", "Ela","Bay","Extra","Xgb"]
#模型筛选，前5个高分模型
select_models=dict()
for name, model in zip(names, models):
    score = r2_cv(model, x_train1, y_train1)
    select_models[name]=score.mean()
select_models=sorted(select_models.items(),key=lambda d:d[1],reverse=True)
select_models=select_models[:5]
select_models=dict(select_models)
second_model_name="Ker" # 后面stacking使用ker做第二层模型
score = r2_cv(KernelRidge(alpha=0.6, kernel='polynomial', degree=2, coef0=2.5), x_train1,y_train1)
select_models["Ker"]=score.mean()
print(select_models)
#各个模型逐个使用网格调参
Best_params=dict()
Best_scores=dict()
for key in select_models.keys():
    print(key)
    if key=='Ridge':
        Best_params['Ridge'],Best_scores['Ridge']=grid(Ridge()).grid_get(x_train1,y_train1,{'alpha':[0.01, 0.1, 1, 10]})
    elif key=='Lasso':
        Best_params['Lasso'],Best_scores['Lasso']=grid(Lasso()).grid_get(x_train1,y_train1,{'alpha': [0.1,0.5,1],'max_iter':[50,100,500]})
    elif key=='RF':
        Best_params['RF'],Best_scores['RF']=grid(RandomForestRegressor()).grid_get(x_train1,y_train1,{'n_estimators':[50,70,100,130],'max_depth':[5,10,20,40]})
    elif key=='GBR':
        Best_params['GBR'],Best_scores['GBR']=grid(GradientBoostingRegressor()).grid_get(x_train1,y_train1,{'n_estimators':[50,70,100,130],'learning_rate':[0.2,0.4,0.6,0.8],})
    elif key=='SVR':
        Best_params['SVR'],Best_scores['SVR']=grid(SVR()).grid_get(x_train1,y_train1,{'C':[0.01,0.1,1],'kernel':["rbf"],"gamma":[0.01,0.1,1]})
    elif key=='Ela':
        Best_params['Ela'],Best_scores['Ela']=grid(ElasticNet()).grid_get(x_train1,y_train1,{'alpha':[0.01,0.1,0.5],'l1_ratio':[0.01,0.1,0.5],'max_iter':[50,100,500]})
    elif key=='Bay':
        Best_params['Bay'],Best_scores['Bay']=None # 贝叶斯回归不用交叉验证选择超参数
    elif key=='Ker':
        Best_params['Ker'],Best_scores['Ker']=grid(KernelRidge()).grid_get(x_train1,y_train1,{'alpha':[0.3,0.6,0.9],'kernel':['polynomial'],'coef0':[1.0,1.5,2]})
    elif key=='Extra':
        Best_params['Extra'],Best_scores['Extra']=grid(ExtraTreesRegressor()).grid_get(x_train1,y_train1,{'n_estimators':[50,100,150,200],'max_depth':[5,10,20,40]})
    elif key=='Xgb':
        Best_params['Xgb'],Best_scores['Xgb']=grid(XGBRegressor()).grid_get(x_train1,y_train1,{'n_estimators':[50,100,150,200],'max_depth':[5,10,20,40]})
print(Best_params)
print(Best_scores)

#获得各个调参完后的基模型
Ker = KernelRidge()
models=[]
for key, value in Best_params.items():
    if key=='Ridge':
        Ridge=Ridge(alpha=Best_params['Ridge']['alpha'])
        models.append(Ridge)
    elif key=='Lasso':
        Lasso=Lasso(alpha=Best_params['Lasso']['alpha'],max_iter=Best_params['Lasso']['max_iter'])
        models.append(Lasso)
    elif key=='RF':
        RF=RandomForestRegressor(n_estimators=Best_params['RF']['n_estimators'],max_depth=Best_params['RF']['max_depth'])
        models.append(RF)
    elif key=='GBR':
        GBR=GradientBoostingRegressor(n_estimators=Best_params['GBR']['n_estimators'],learning_rate=Best_params['GBR']['learning_rate'])
        models.append(GBR)
    elif key=='SVR':
        svr=SVR(C=Best_params['SVR']['C'],kernel='rbf',gamma=Best_params['SVR']['gamma'])
        models.append(svr)
    elif key=='Ela':
        Ela=ElasticNet(alpha=Best_params['Ela']['alpha'],l1_ratio=Best_params['Ela']['l1_ratio'],max_iter=Best_params['Ela']['max_iter'])
        models.append(Ela)
    elif key=='Bay':
        Bay=BayesianRidge()
        models.append(Bay)
    elif key=='Ker':
        Ker=KernelRidge(alpha=Best_params['Ker']['alpha'],kernel=Best_params['Ker']['kernel'],coef0=Best_params['Ker']['coef0'])
    elif key=='Extra':
        Extra=ExtraTreesRegressor(n_estimators=Best_params['Extra']['n_estimators'],max_depth=Best_params['Extra']['max_depth'])
        models.append(Extra)
    elif key=='Xgb':
        Xgb=XGBRegressor(n_estimators=Best_params['Xgb']['n_estimators'],max_depth=Best_params['Xgb']['max_depth'])
        models.append(Xgb)
print(models)

#各个基模型在测试集的分数
names = list(Best_params.keys())
for name, model in zip(names, models): #5折交叉验证
    score = r2_cv(model, x_test1,y_test1)
    print("{}: {:.6f}".format(name,score.mean()))

stack = StackingCVRegressor(regressors=set(models),
                            meta_regressor=Ker,
                            use_features_in_secondary=True)

stack.fit(x_train1,y_train1)
pred = stack.predict(x_test1)
score = r2_score(y_test1,pred)
score = "{:.6f}".format(score)

pickle.dump(stack, open('stackingmodel.pkl','wb'))

print(score)
# with open("R_score.txt","w") as f:
#     f.write(score)