'''
特征工程部分：
1.各特征转化为数值型特征
2.异常值检测
3.缺失值填充
4.特征变换
5.特征选择
最终数据集：包含做完特征变换后的特征样本值，以及未变换前的房屋总价和房屋每平米价
'''
import pymysql
import pandas as pd
import numpy as np
import category_encoders as ce
import re
import cn2an
import datetime
from scipy.stats import skew
from scipy import stats
from sklearn.preprocessing import PowerTransformer

conn = pymysql.connect(
    host = '106.52.47.202',
    user = 'root',
    passwd = '123456',
    db = 'house',
    port=3306,
    charset = 'utf8'
)

cursor01 = conn.cursor()
cursor01.execute(
        "select column_name, column_comment from information_schema.columns where table_schema ='house' and table_name = 'allhouses'")
all_info = list(cursor01.fetchall())
print(all_info)
df = pd.read_sql('select * from allhouses',conn)
column_names = []
for i in all_info:
    column_names.append(i[1])
df.columns = column_names
df1 = df.copy()

#有几十个房子由于页面特殊爬取错乱
df1 = df1.dropna(subset=['装修情况'])
#某些特征无用，删除
df1 = df1.drop(columns=['小区详情url','房屋年限','房子ID'],axis=1)

df1.to_excel('初始数据集.xlsx',index=None)
'''
(1)各特征转化为数值特征
1.去除单位
2.特征组合
3.特征编码
'''
#物业费用有些是1.2至100元/平米/月 有些是1.5元/平米/月的类型，对于前者取中值，对于后者只去除单位
df1.loc[df1['小区物业费用']=='暂无信息','小区物业费用'] = np.nan #对于暂无信息的值记作空值
df1.loc[df1['小区物业费用'].notnull(),'小区物业费用']=\
df1.loc[df1['小区物业费用'].notnull(),'小区物业费用'].apply(lambda x:x[:-6])
df1.loc[df1['小区物业费用'].notnull(),'小区物业费用']=\
df1.loc[df1['小区物业费用'].notnull(),'小区物业费用'].apply(lambda x: (np.double(x.split('至')[0])+np.double(x.split('至')[1]))/2 if '至' in x else x)

#对于上次交易时间与挂牌时间，做衍生指标处理，为挂牌时间-上次交易时间，单位天数
df1.loc[df['上次交易']=='暂无数据','上次交易'] = np.nan #对于暂无信息的值记作空值
today = str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)
df1['当前时间'] = today
df1['当前时间'] = pd.to_datetime(df1['当前时间'],errors = 'coerce')
df1['上次交易'] = pd.to_datetime(df1['上次交易'],errors = 'coerce')
df1['挂牌时间'] = pd.to_datetime(df1['挂牌时间'],errors = 'coerce')
df1['挂牌时间-上次交易时间'] = ((df1['挂牌时间'] - df1['上次交易']).values/np.timedelta64(1, 'h'))/24
df1['当前时间-挂牌时间']=((df1['当前时间'] - df1['挂牌时间']).values/np.timedelta64(1, 'h'))/24
#删除原指标
df1 = df1.drop(columns = ['上次交易','挂牌时间','当前时间'])

#房屋用途，标签编码
yongtu_mapping = {
           '别墅':5,
           '商业':4,
           '商住两用':3,
           '普通住宅':2,
           '平房':1,
}
df1['房屋用途'] = df1['房屋用途'].map(yongtu_mapping)

#抵押信息，将信息改为有无抵押，暂无信息则改为NaN，后进行编码处理
df1.loc[(df1['抵押信息']!='无抵押')&(df1['抵押信息'].notnull()),'抵押信息']=\
df1.loc[(df1['抵押信息']!='无抵押')&(df1['抵押信息'].notnull()),'抵押信息'].apply(lambda x:x[:3])
df1.loc[df1['抵押信息']=='暂无数','抵押信息']=np.nan

#前3个特征为有序特征，如产权共有的房子会更受消费者的青睐，因此均作二值化处理
df1.loc[df1['产权所属']=='共有','产权所属']=1
df1.loc[df1['产权所属']=='非共有','产权所属']=0
df1.loc[df1['抵押信息']=='无抵押','抵押信息']=1
df1.loc[df1['抵押信息']=='有抵押','抵押信息']=0
df1.loc[df1['房本备件']=='已上传房本照片','房本备件']=1
df1.loc[df1['房本备件']=='未上传房本照片','房本备件']=0

#对于交易权属，使用频数编码
count_enc = ce.CountEncoder()
#Transform the features, rename the columns with the _count suffix, and join to dataframe
df1['交易权属'] = count_enc.fit_transform(df1['交易权属'])

#建筑时间
df1.loc[df1['建楼时间'].notnull(),'建楼时间']=df1.loc[df1['建楼时间'].notnull(),'建楼时间'].apply(lambda x:x[:-2])
df1.loc[df1['建楼时间']=='未知','建楼时间']=np.nan
df1['建楼时间-小区建筑年代']=np.nan
df1['建楼时间-小区建筑年代']=df1.loc[df1['建楼时间'].notnull(),'建楼时间'].astype(float)-df1.loc[df1['小区建筑年代'].notnull(),'小区建筑年代'].astype(float)
df1.loc[df1['建楼时间'].notnull(),'建楼时间']=\
float(datetime.datetime.now().year)-(df1.loc[df1['建楼时间'].notnull(),'建楼时间'].astype(float))
df1.loc[df1['小区建筑年代'].notnull(),'小区建筑年代']=\
float(datetime.datetime.now().year)-(df1.loc[df1['小区建筑年代'].notnull(),'小区建筑年代'].astype(float))
df1.rename(columns={"建楼时间":"建楼距今时长", "小区建筑年代":"小区建成距今时长"},inplace=True)

#面积特征
df1.loc[df1['套内面积']=='暂无数据','套内面积']=np.nan
df1.loc[df1['建筑面积'].notnull(),'建筑面积']=df1.loc[df1['建筑面积'].notnull(),'建筑面积'].apply(lambda x:x[:-1]).astype(float)
df1.loc[df1['套内面积'].notnull(),'套内面积']=df1.loc[df1['套内面积'].notnull(),'套内面积'].apply(lambda x:x[:-1]).astype(float)
#衍生特征，建筑面积-套内面积=公摊面积
df1['公摊面积']=np.nan
df1['公摊面积']=df1.loc[df1['建筑面积'].notnull(),'建筑面积']-df1.loc[df1['套内面积'].notnull(),'套内面积']

#梯户比例：衍生特征户数/梯数
re2 = re.compile('(.+)梯(.+)户')
def cn_extraction(x):
    if x==np.nan:
        return ['一','零']
    ret = re2.findall(x)
    if ret:
        return (re2.findall(x))[0]
    else:
        return ['一','零']
def calculate_ratio(x):
    h = cn2an.cn2an(x[1],'smart')
    t = cn2an.cn2an(x[0],'smart')
    r = h/t
    return r
df1.loc[df1['梯户比例'].notnull(),'梯户比例']=df1.loc[df1['梯户比例'].notnull(),'梯户比例'].apply(cn_extraction).apply(calculate_ratio)

#房屋户型：衍生特征：卧室数量，客厅数量，厨房数量，卫生间数量
re1 = re.compile('\d+')
temp = df1.loc[:,'房屋户型'].apply(re1.findall)
df1['卧室数量']=df1['客厅数量']=df1['厨房数量']=df1['卫生间数量']=np.nan
df1['卧室数量'] = temp.apply(lambda x:x[0])
df1['客厅数量'] = temp.apply(lambda x:x[1])
df1['厨房数量'] = temp.apply(lambda x:x[2])
df1['卫生间数量'] = temp.apply(lambda x:x[3])
df1 = df1.drop(columns = ['房屋户型'])

#所在楼层衍生特征总楼层数目
re3 = re.compile('.+共(\d+)层.+')
df1['总层数'] = df1.loc[:,'所在楼层'].apply(lambda x:re3.findall(x)[0])

# 户型分间衍生以下特征
# 1.客厅面积占比
# 2.卧室面积占比
# 3.实际使用面积
# 4.落地窗数量
# 5.有无储物间
# 6.有无入室花园
# 7.窗户数量
# 8.平均卧室面积
# 9.客厅、卧室、阳台朝向，采光等级

#朝向以等级分级
#南＞东南=西南＞东=西＞东北=西北＞北
rank_direction = {
    '南':5,
    '东南':4,
    '西南':4,
    '东':3,
    '西':3,
    '东北':2,
    '西北':2,
    '北':1,
    '无':None
}

def change_direct(x):
    for k,j in rank_direction.items():
        if k in x:
            return j
df1.loc[df1['户型分间']=='{}','户型分间']=np.nan
list1=[]
list2=[]
list3=[]
list4=[]
list5=[]
list6=[]
list7=[]
list8=[]
list9=[]
list10=[]
list11=[]
for item in df1.loc[df1['户型分间'].notnull(), '户型分间']:
    item = eval(item)  # 转换为字典
    df2 = pd.DataFrame(item)
    if '储物间' in df2.columns:
        list3.append(1)
    else:
        list3.append(0)
    if '入户花园' in df2.columns:
        list4.append(1)
    else:
        list4.append(0)
    j = 0
    k = 0
    for i in df2.iloc[2]:
        if i == '落地飘窗':
            j = j + 1
        if i != '无窗':
            k = k + 1
    list2.append(j)
    list5.append(k)
    df3 = df2.filter(regex='客厅')
    df4 = df2.filter(regex='卧室')
    df5 = df2.filter(regex='阳台')
    using_area = 0
    for p in df2.iloc[0]:
        p = p.split('平')
        p = np.double(p[0])
        using_area = using_area + p
    list6.append(using_area)
    livingroom_sum = 0
    for p in df3.iloc[0]:
        p = p.split('平')
        p = np.double(p[0])
        livingroom_sum = livingroom_sum + p
    list1.append(np.double(livingroom_sum / using_area))
    room_sum = 0
    for p in df4.iloc[0]:
        p = p.split('平')
        p = np.double(p[0])
        room_sum = room_sum + p
    list8.append(np.double(room_sum / using_area))
    m = df4.shape[1]
    if m != 0:
        room_ave = room_sum / m
    else:
        room_ave = 0
    list7.append(room_ave)

    # 房屋朝向等级
    # 客厅
    try:
        list9.append(change_direct(df3['客厅'][1]))
    except:
        list9.append(None)
    # 主卧
    try:
        x1 = df4.iloc[1, np.argmax(df4.loc[0, :].apply(lambda x: x[:-2]).astype(float))]
        list10.append(change_direct(x1))
    except:
        list10.append(None)
    # 主阳台
    try:
        x1 = df5.iloc[1, np.argmax(df5.loc[0, :].apply(lambda x: x[:-2]).astype(float))]
        list11.append(change_direct(x1))
    except:
        list11.append(None)
df1['客厅面积占比']=df1['户型分间']
df1['卧室面积占比']=df1['户型分间']
df1['平均卧室面积']=df1['户型分间']
df1['实际使用面积']=df1['户型分间']
df1['有无储物间']=df1['户型分间']
df1['有无入室花园']=df1['户型分间']
df1['窗户数量']=df1['户型分间']
df1['落地窗数量']=df1['户型分间']
df1['客厅采光程度']=df1['户型分间']
df1['主卧采光程度']=df1['户型分间']
df1['阳台采光程度']=df1['户型分间']
df1.loc[df1['客厅面积占比'].notnull(),'客厅面积占比']=list1
df1.loc[df1['落地窗数量'].notnull(),'落地窗数量']=list2
df1.loc[df1['有无储物间'].notnull(),'有无储物间']=list3
df1.loc[df1['有无入室花园'].notnull(),'有无入室花园']=list4
df1.loc[df1['窗户数量'].notnull(),'窗户数量']=list5
df1.loc[df1['实际使用面积'].notnull(),'实际使用面积']=list6
df1.loc[df1['平均卧室面积'].notnull(),'平均卧室面积']=list7
df1.loc[df1['卧室面积占比'].notnull(),'卧室面积占比']=list8
df1.loc[df1['客厅采光程度'].notnull(),'客厅采光程度']=list9
df1.loc[df1['主卧采光程度'].notnull(),'主卧采光程度']=list10
df1.loc[df1['阳台采光程度'].notnull(),'阳台采光程度']=list11
df1=df1.drop(['户型分间'],axis=1)

##重要性不大，且难处理
df1=df1.drop(['小区建筑类型'],axis=1)
df1=df1.drop(['房屋朝向'],axis=1)

#户型结构、建筑类型、所在楼层（为无序特征）：使用onehot编码
df1['户型结构']=df1['户型结构'].replace("暂无数据",np.NAN)
df1 = pd.concat([df1, pd.get_dummies(df1.loc[:,['户型结构']])], sort=False, axis=1)
df1=df1.drop('户型结构',axis=1)
df1['建筑类型']=df1['建筑类型'].replace("暂无数据",np.NAN)
df1 = pd.concat([df1, pd.get_dummies(df1.loc[:,['建筑类型']])], sort=False, axis=1)
df1=df1.drop('建筑类型',axis=1)

#所在楼层
df1['所在楼层']=df1['所在楼层'].astype(str)
def rep(x):
    pattern = re.compile(r'\s\((.*)\)')
    return pattern.sub(r'',x)
df1['所在楼层']=df1['所在楼层'].apply(rep)
df1['所在楼层']=df1['所在楼层'].replace("nan",np.NAN)
df1 = pd.concat([df1, pd.get_dummies(df1.loc[:,['所在楼层']])], sort=False, axis=1)
df1=df1.drop('所在楼层',axis=1)

#建筑结构、装修情况：定义等级后编码
df1['建筑结构']=df1['建筑结构'].replace("未知结构",np.NAN)
jiegou_mapping = {
           '钢结构': 6,
           '钢混结构':5,
           '框架结构':4,
           '混合结构':3,
           '砖混结构':2,
           '砖木结构':1}
df1['建筑结构'] = df1['建筑结构'].map(jiegou_mapping)

df1['装修情况']=df1['装修情况'].replace("其他",np.NAN)
zhuangxiu_mapping={
    '精装':3,
    '简装':2,
    '毛坯':1
}
df1['装修情况'] = df1['装修情况'].map(zhuangxiu_mapping)
#电梯二值化处理
df1['配备电梯']=df1['配备电梯'].replace("暂无数据",1)
df1['配备电梯']=df1['配备电梯'].replace("NULL",1)
df1['配备电梯']=df1['配备电梯'].replace("有",1)
df1['配备电梯']=df1['配备电梯'].replace("无",0)

#所在广州区域
list_sorted=['天河','越秀','海珠','荔湾','白云','番禺','黄埔','南沙','顺德','增城','花都','从化','南海']
mapping={'天河':12,'越秀':11,'海珠':10,'荔湾':9,'白云':8,'番禺':7,'黄埔':6,'南沙':5,'顺德':4,'增城':3,'花都':2,'从化':1,'南海':0}
df1['所在区域']=df1['所在区域'].map(mapping)

'''
(2)异常值检测及处理
有以下处理
1.特征为负数的都为异常值：小区建成距今时长、挂牌时间-上次交易时间（负数的为异常值，当作缺失值）
2.小区物业费用（小区物业费用过高或过低的为异常值，当作缺失值）
3.实际使用面积应该比建筑面积小，因此将实际面积大于建筑面积的部分视为异常值
'''
# 特征为负数的都为异常值，作为缺失值
def delete_negative(df1,label):
    if(len(df1.loc[df1[label]<0,label])>0):
        print('特征{0}的异常值数目为:{1}'.format(label,len(df1.loc[df1[label]<0,label])))
    df1.loc[df1[label]<0,label]=np.nan
for i in df1.keys():
    try:
        delete_negative(df1,i)
    except:
        continue

# 小区物业费用处理
df1['小区物业费用'] = df1['小区物业费用'].astype('float')
lower_q=df1['小区物业费用'].quantile(0.25,interpolation='lower')#下四分位数
higher_q=df1['小区物业费用'].quantile(0.75,interpolation='higher')#上四分位数
IQR=higher_q-lower_q
#取下四分位数-3*IQR为下界，取上四分位数+3*IQR为上界
Lower_fence = lower_q - (IQR * 3)
Upper_fence = higher_q + (IQR * 3)
# 小区物业费用（过高过低当作缺失值）
df1.loc[df1['小区物业费用']<Lower_fence,'小区物业费用']=np.nan
df1.loc[df1['小区物业费用']>Upper_fence,'小区物业费用']=np.nan
df1.loc[df1['实际使用面积']>df1['建筑面积'],'实际使用面积']=np.nan

'''
(4)缺失值处理
(1,2,3根据一定规则进行填充)
1.套内面积与公摊面积
2.配备电梯
3.采光程度
4.其余采用条件均值或条件众值进行填充
'''
total = df1.isnull().sum().sort_values(ascending=False)
percent = (df1.isnull().sum()/df1.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total','Percent'])

'''
相关数据填充
1.套内面积与公摊面积
建筑面积是无缺失的，套内面积缺失较多，导致公摊面积也缺失较多，三者之间有联系。 得
房率=套内面积/建筑面积。 
一般来说，地下室(0) 60%，低层住宅（1-3）92%，多层住宅（4-9）得房率88%，高层住宅（>=10）80% 
根据得房率×建筑面积来填充套内面积。再用建筑面积-套内面积得到缺失的公摊面积。
'''
# 套内面积、公摊面积
df1[['套内面积','建筑面积','公摊面积','总层数']]=df1[['套内面积','建筑面积','公摊面积','总层数']].astype('float')
condition= (df1['套内面积'].isnull()) & (df1['总层数']==0)
condition1= (df1['套内面积'].isnull()) & (df1['总层数']<4) & (df1['总层数']>0)
condition2=(df1['套内面积'].isnull()) & (df1['总层数']<10) & (df1['总层数']>3)
condition3=(df1['套内面积'].isnull()) & (df1['总层数']>9)
df1.loc[condition,'套内面积']=df1.loc[condition,'建筑面积']*0.6
df1.loc[condition1,'套内面积']=df1.loc[condition1,'建筑面积']*0.92
df1.loc[condition2,'套内面积']=df1.loc[condition2,'建筑面积']*0.88
df1.loc[condition3,'套内面积']=df1.loc[condition3,'建筑面积']*0.80
df1.loc[df1['公摊面积'].isnull(),'公摊面积']=df1.loc[df1['公摊面积'].isnull(),'建筑面积']-df1.loc[df1['公摊面积'].isnull(),'套内面积']

'''
2.电梯
配备电梯根据总层数来判断有无电梯，楼层大于6的视为有电梯，小于等于6的视为没有电梯。
'''
# 配备电梯
condition4=(df1['配备电梯'].isnull()) & (df1['总层数']<7)
condition5=(df1['配备电梯'].isnull()) & (df1['总层数']>6)
df1.loc[condition4,'配备电梯']=0
df1.loc[condition5,'配备电梯']=1

'''
3.采光程度
三个关于采光程度的特征，以中等程度3进行填充
'''
df1['客厅采光程度']=df1['客厅采光程度'].replace(np.NAN,3)
df1['主卧采光程度']=df1['主卧采光程度'].replace(np.NAN,3)
df1['阳台采光程度']=df1['阳台采光程度'].replace(np.NAN,3)

'''
4.其他缺失值填充
'''
missing_labels=list(df1.keys())
#离散型特征，使用条件众数填充，以小区ID为条件
df2 = df1[['所在区域', '小区ID', '建楼距今时长', '小区楼栋总数', '小区建成距今时长',
           '建筑结构', '装修情况', '配备电梯', '交易权属', '房屋用途','产权所属', '抵押信息',
           '房本备件', '挂牌时间-上次交易时间','建楼时间-小区建筑年代', '卧室数量','客厅数量',
           '厨房数量', '卫生间数量', '总层数', '有无储物间', '有无入室花园', '窗户数量',
           '落地窗数量', '客厅采光程度', '主卧采光程度', '阳台采光程度', '户型结构_复式', '户型结构_平层',
           '户型结构_跃层', '户型结构_错层', '建筑类型_塔楼', '建筑类型_平房', '建筑类型_板塔结合', '建筑类型_板楼', '所在楼层_中楼层',
           '所在楼层_低楼层', '所在楼层_地下室', '所在楼层_高楼层', '教育设施数量', '交通设施数', '购物设施数',
           '生活设施数', '娱乐设施数', '医疗设施数']]
count_data =df2.groupby('小区ID').agg(lambda x: stats.mode(x)[0][0]).reset_index()
missing_labels2=['所在区域', '小区ID', '建楼距今时长', '小区楼栋总数', '小区建成距今时长',
           '建筑结构', '装修情况', '配备电梯', '交易权属', '房屋用途','产权所属', '抵押信息',
           '房本备件', '挂牌时间-上次交易时间','建楼时间-小区建筑年代', '卧室数量','客厅数量',
           '厨房数量', '卫生间数量', '总层数', '有无储物间', '有无入室花园', '窗户数量',
           '落地窗数量', '客厅采光程度', '主卧采光程度', '阳台采光程度', '户型结构_复式', '户型结构_平层',
           '户型结构_跃层', '户型结构_错层', '建筑类型_塔楼', '建筑类型_平房', '建筑类型_板塔结合', '建筑类型_板楼', '所在楼层_中楼层',
           '所在楼层_低楼层', '所在楼层_地下室', '所在楼层_高楼层', '教育设施数量', '交通设施数', '购物设施数',
           '生活设施数', '娱乐设施数', '医疗设施数']

for i in missing_labels2:
    for j in df1.loc[df1[i].isnull(),:].index:
        df1.loc[j,i]=count_data.loc[count_data['小区ID']==df1.loc[j,'小区ID'],i].values[0]

#未填完的用全部众数填充
for i in missing_labels2:
    df1[i].fillna(df1[i].mode()[0],inplace=True)

for i in df1.columns:
    try:
        df1[i]=df1[i].astype('float')
    except:
        continue

#连续特征使用条件均值，使用同个小区的均值填充
mean_data = df1.groupby('小区ID').mean()
for i in missing_labels:
    for j in df1.loc[df1[i].isnull(),:].index:
        df1.loc[j,i]=mean_data.loc[df1.loc[j].小区ID,i]

# 未填充完的特征
pretotal=total
total2 = df1.isnull().sum().sort_values(ascending=False)
percent = (df1.isnull().sum()/df1.isnull().count()).sort_values(
        ascending=False)
missing_data = pd.concat([total2, pretotal], axis=1, keys=['Total','PreTotal'])
# 剩余特征
missing_labels=missing_data[missing_data['Total']!=0].index

#剩余特征进一步使用条件均值填充，条件为所在广州区域
mean_data2= df1.groupby('所在区域').mean()
for i in missing_labels:
    for j in df1.loc[df1[i].isnull(),:].index:
        df1.loc[j,i]=mean_data2.loc[df1.loc[j].所在区域,i]

#剩余填充特征
pretotal=total2
total3 = df1.isnull().sum().sort_values(ascending=False)
percent = (df1.isnull().sum()/df1.isnull().count()).sort_values(
        ascending=False)
missing_data = pd.concat([total3, pretotal], axis=1, keys=['Total','PreTotal'])
missing_labels=missing_data[missing_data['Total']!=0].index

# 剩余特征填完，直接用整列均值
for i in missing_labels:
    df1[i].fillna(df1[i].mean(),inplace=True)

#剩余填充特征
pretotal=total2
total3 = df1.isnull().sum().sort_values(ascending=False)
percent = (df1.isnull().sum()/df1.isnull().count()).sort_values(
        ascending=False)
missing_data = pd.concat([total3, pretotal], axis=1, keys=['Total','PreTotal'])
missing_labels=missing_data[missing_data['Total']!=0].index

df1=df1.drop(columns = ['小区ID'])

'''
(4)特征变换
'''
#对房屋总价正态变换，后面可以用inverse_transform反转
df1_1 = df1.copy()
pt = PowerTransformer('box-cox').fit(df1[['房屋总价']])
df1['房屋总价'] = pt.transform(df1[['房屋总价']])

#对房屋每平米价正态变换，后面可以用inverse_transform反转
pt = PowerTransformer('box-cox').fit(df1[['房屋每平米价']])
df1['房屋每平米价'] = pt.transform(df1[['房屋每平米价']])

#连续特征表
lianxu = ['小区物业费用', '建筑面积', '套内面积', '梯户比例','公摊面积',
          '客厅面积占比','卧室面积占比', '平均卧室面积', '实际使用面积',
          '教育设施平均距离', '交通设施平均距离', '购物设施平均距离',
          '生活设施平均距离', '娱乐设施平均距离', '医疗设施平均距离']

skewness = df1[lianxu].apply(lambda x: skew(x))
skewness.sort_values(ascending=False)
skewness = skewness[abs(skewness)>0.75]
skewness = list(skewness.index)
skewness.append('房屋总价')
skewness.append('房屋每平米价')

df_tran = df1_1.loc[:,skewness]
df_tran.to_excel('连续特征转化前数值.xlsx', index=None)

#将偏度大于0.75的变量进行正态化
for i in skewness:
    pt = PowerTransformer().fit(df1[[i]])
    df1[i] = pt.transform(df1[[i]])

'''
(5)特征选择
'''
def spearman(frame, features):
    spr = pd.DataFrame()
    spr['feature'] = features
    spr['corr'] = [frame[f].corr(frame['房屋总价'], 'spearman') for f in features]
    select_dict=dict(zip(spr['feature'],spr['corr']))
    select_dict={k:v for k,v in select_dict.items() if abs(v)>0.1}
    spr = spr.sort_values('corr')
    return select_dict
df1.keys()
df2=df1.drop('房屋每平米价',1)
# 筛选出相关系数绝对值大于0.1的特征
select_dict=spearman(df2, df2.columns)
select_dict.pop('房屋总价')
select_list=list(select_dict.keys())
select_data = df1[select_list]
select_labels=[]
corrmat = select_data.corr()
for i in select_list:
    for j in select_list:
        if abs(corrmat.loc[i,j])==1:
            continue
        if 0.8<abs(corrmat.loc[i,j]):
            select_labels.append(i)
            select_labels.append(j)
select_labels = list(set(select_labels))
max_score = 0
max_label = None
for i in select_labels:
    if select_dict[i]>max_score:
        max_score = select_dict[i]
        max_label = i
select_labels.remove(max_label)
select_list = list(set(select_dict.keys()) - set(select_labels))

select_list.append('房屋总价')
select_list.append('房屋每平米价')
if '所在区域' not in select_list:
    select_list.append('所在区域')

df_final = df1[select_list]
mid = df_final['所在区域']
df_final.drop(labels=['所在区域'], axis=1,inplace = True)
df_final.insert(0, '所在区域', mid)

with open('model1Name.txt','w', encoding='gbk') as file:
    for c in list(df_final.keys()):
        if (c == '房屋总价') or (c=='房屋每平米价'):
            continue
        file.write(c)
        file.write(',')

df_final['当前时间-挂牌时间'] = df1['当前时间-挂牌时间']
# df_j01 = df_final.loc[df_final['当前时间-挂牌时间']<365,:]
# df_j01.drop(labels=['当前时间-挂牌时间'], axis=1,inplace = True)
# df_j01.to_excel('建模数据1(一年内).xlsx',index=None)
#
# df_j02 = df_final.loc[df_final['当前时间-挂牌时间']<210,:]
# df_j02.drop(labels=['当前时间-挂牌时间'], axis=1,inplace = True)
# df_j02.to_excel('建模数据2(七个月内).xlsx',index=None)
#
# df_j03 = df_final.loc[df_final['当前时间-挂牌时间']<100,:]
# df_j03.drop(labels=['当前时间-挂牌时间'], axis=1,inplace = True)
# df_j03.to_excel('建模数据3(三个月内).xlsx',index=None)

df_final.drop(labels=['当前时间-挂牌时间'], axis=1,inplace = True)
df_final.to_excel('建模数据(全部数据).xlsx', index=None)