from flask import Flask,render_template,request, jsonify, send_from_directory
from scipy import stats
import utils
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import PowerTransformer

#加载数据
df = pd.read_excel('建模数据(全部数据).xlsx')  # 特征选择后的特征
df_tran = pd.read_excel('连续特征转化前数值.xlsx')  # 正态化以及标准化之前的某些特征数据

#读取分数
with open("R_score.txt","r") as f:
    data = f.read()
score_list = eval(data)

# 加载模型
model = pickle.load(open('model.pkl', 'rb'))
stackingmodel = pickle.load(open('stackingmodel.pkl', 'rb'))
boostingmodel = pickle.load(open('boostingmodel.pkl', 'rb'))
baggingmodel = pickle.load(open('baggingmodel.pkl', 'rb'))

#离散特征表
missing_labels2=['所在区域', '小区ID', '建楼距今时长', '小区楼栋总数', '小区建成距今时长',
           '建筑结构', '装修情况', '配备电梯', '交易权属', '房屋用途','产权所属', '抵押信息',
           '房本备件','建楼时间-小区建筑年代', '卧室数量','客厅数量','挂牌时间-上次交易时间',
           '厨房数量', '卫生间数量', '总层数', '有无储物间', '有无入室花园', '窗户数量',
           '落地窗数量', '客厅采光程度', '主卧采光程度', '阳台采光程度', '户型结构_复式', '户型结构_平层',
           '户型结构_跃层', '户型结构_错层', '建筑类型_塔楼', '建筑类型_平房', '建筑类型_板塔结合', '建筑类型_板楼', '所在楼层_中楼层',
           '所在楼层_低楼层', '所在楼层_地下室', '所在楼层_高楼层', '教育设施数量', '交通设施数', '购物设施数',
           '生活设施数', '娱乐设施数', '医疗设施数']

'''
    feature_list:用户所输入的各个值
    返回值：所预测出来的值
'''
def Predict_model(feature_list, model):
    model = model
    x = df.loc[:, (df.columns != '房屋总价') & (df.columns != '房屋每平米价')]
    feature_name = list(x.columns)
    feature_dict = dict(zip(feature_name, feature_list))
    print(feature_list)
    count_data1=pd.DataFrame()
    count_data2=pd.DataFrame()
    '''
        所输入数据正态化部分
    '''
    for i in df_tran.columns:
        if i not in x.columns:
            continue
        if feature_dict[i] != '':
            pt = PowerTransformer().fit(df_tran[[i]])
            feature_dict[i] = (pt.transform([[feature_dict[i]]]))[0][0]

    '''
        缺失值填充部分
    '''
    feature_dict = pd.DataFrame(feature_dict, index=[0])
    try:
        feature_dict['所在区域'] = feature_dict['所在区域'].astype('float')
        #众数表
        count_data1 = x.groupby('所在区域').agg(lambda x: stats.mode(x)[0][0]).reset_index()
        #均值表
        count_data2 = x.groupby('所在区域').mean()
    except:
        pass

    #条件填充（众数与平均值）
    try:
        for i in feature_dict.columns:
            if (i in missing_labels2) and ((feature_dict[i] == '')[0]):
                feature_dict[i] = (count_data1.loc[count_data1['所在区域'] == feature_dict['所在区域'][0], i]).values[0]
            elif ((feature_dict[i] == '')[0]):
                feature_dict[i] = count_data2.loc[feature_dict['所在区域'][0], i]
    except:
        pass
    # 全填充（众数与平均值）
    for i in feature_dict.columns:
        if (i in missing_labels2) and ((feature_dict[i] == '')[0]):
            feature_dict[i] = x[i].mode()[0]
        elif ((feature_dict[i] == '')[0]):
            feature_dict[i] = x[i].mean()
    feature_dict = feature_dict.astype('float')
    # 转回字典方便操作
    feature_dict = dict(zip(feature_name, feature_dict.iloc[0, :]))
    print(feature_dict)

    '''
        所输入数据标准化
    '''
    for i in feature_name:
        mean = np.mean(df[i])
        std = np.std(df[i])
        feature_dict[i] = (feature_dict[i] - mean) / std

    print(feature_dict)


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

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

#主页面
@app.route('/')
def index():
    return render_template('index.html')

#下载页面
@app.route("/download")
def download():
    return send_from_directory("../houseprice",filename="初始数据集.xlsx",as_attachment=True)

#可视化界面
@app.route('/visual/')
def visual():
    return render_template('visual.html')

#时间
@app.route('/visual/time/')
def gettime():
    return utils.get_time()

@app.route('/visual/data/')
def get_data():
    data = utils.get_data()
    areaDic = dict()
    for area in ['天河','越秀','海珠','荔湾','黄埔','白云','番禺','南沙','增城','花都','从化']:
        price,avePrice, = [],[]
        count = 0
        for d in data:
            if(d[0]==area):
                price.append(d[1])
                avePrice.append(d[2])
                count = count + 1
        areaDic[area]=[int(np.array(price).mean()), int(np.array(avePrice).mean()), count]
    allprice = [[i[0],i[1][0]] for i in areaDic.items()]
    avePrice = [i[1] for i in areaDic.values()]
    map = [{"name":i[0]+'区',"value":i[1][1]} for i in areaDic.items()]
    pie = [{"name":i[0],"value":i[1][2]} for i in areaDic.items()]
    print({"allprice":allprice,"avePrice":avePrice,"map":map,"pie":pie})
    return jsonify({"allprice":allprice,"avePrice":avePrice,"map":map,"pie":pie})

#特征名字表
@app.route('/predict/model1Name/')
def model1Name():
    namedic = utils.get_model1_name()
    return jsonify(namedic)

#Stacking模型页面
@app.route('/predict/stacking')
def predict():
    return render_template('predict.html', stack_score=score_list[0])

@app.route('/predict/Stacking',methods=['POST'])
def model1Predict():
    features_list = list(request.form.values())
    predict_outcome = Predict_model(features_list,stackingmodel)
    return render_template('predict.html', prediction_display_area='预测价格为：{:.6f}万元'.format(predict_outcome))

#Boosting模型页面
@app.route('/predict/boosting')
def Model_2():
    return render_template('Model_2.html', stack_score=score_list[1])

@app.route('/predict/Boosting',methods=['POST'])
def model2Predict():
    features_list = list(request.form.values())
    predict_outcome = Predict_model(features_list,boostingmodel)
    return render_template('Model_2.html', prediction_display_area='预测价格为：{:.6f}万元'.format(predict_outcome))

#Bagging模型页面
@app.route('/predict/bagging')
def Model_3():
    return render_template('Model_3.html', stack_score=score_list[2])

@app.route('/predict/Bagging',methods=['POST'])
def model3Predict():
    features_list = list(request.form.values())
    predict_outcome = Predict_model(features_list,baggingmodel)
    return render_template('Model_3.html', prediction_display_area='预测价格为：{:.6f}万元'.format(predict_outcome))

if __name__ == "__main__":
    app.run(debug=True)

