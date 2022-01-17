import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import PowerTransformer

'''
    feature_list:用户所输入的各个值
    返回值：所预测出来的值
'''
def Predict_model(feature_list):
    df = pd.read_excel('最终建模数据.xlsx')  # 特征选择后的特征
    df_tran = pd.read_excel('连续特征转化前数值.xlsx')  # 正态化以及标准化之前的某些特征数据
    x = df.loc[:, (df.columns != '房屋总价') & (df.columns != '房屋每平米价')]

    #加载模型
    model = pickle.load(open('model.pkl', 'rb'))

    # 测试例子
    feature_name = list(x.columns)
    # feature_list即那个用户输入的数据表，拿的第一个房子作为测试
    #feature_list = [1, 5, 12, 9.283333333, 402, 9, 0.405616943, 3086.8619047619, 2246.71428571429, 117.68,
    #                6, 1, 23.536, 12, 3, 0, 6, 2, 2, 1, 2299.875, 5596, 10, 6973]
    feature_dict = dict(zip(feature_name, feature_list))

    # 变换所输入的数据，正态化，某些特征不用正态化
    for i in df_tran.columns:
        if i not in x.columns:
            continue
        pt = PowerTransformer().fit(df_tran[[i]])
        feature_dict[i] = (pt.transform([[feature_dict[i]]]))[0][0]

    # 变换所输入的数据，标准化，全部特征都要
    for i in feature_name:
        mean = np.mean(df[i])
        std = np.std(df[i])
        feature_dict[i] = (feature_dict[i] - mean) / std

    # 预测
    features_final = list(feature_dict.values())
    features = np.array(features_final).reshape(1, -1)
    predict_outcome_list = model.predict(features)
    predict_outcome = predict_outcome_list[0]

    # 预测结果还得逆转回去
    # 标准化逆转
    result_mean = np.mean(df['房屋总价'])
    result_std = np.std(df['房屋总价'])
    predict_outcome = predict_outcome * result_std + result_mean
    # box-cox逆转
    pt = PowerTransformer('box-cox').fit(df_tran[['房屋总价']])
    predict_outcome = pt.inverse_transform([[predict_outcome]])[0][0]
    return predict_outcome