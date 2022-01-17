// 基于准备好的dom，初始化echarts实例
var myChart = echarts.init(document.getElementById('visualright'));
myChart.showLoading();
//步骤一:创建异步对象
var ajax = new XMLHttpRequest();
//步骤二:设置请求的url参数,参数一是请求的类型,参数二是请求的url,可以带参数,动态的传递参数starName到服务端
ajax.open('get','guangzhou.json');
//步骤三:发送请求
ajax.send();
//步骤四:注册事件 onreadystatechange 状态改变就会调用
ajax.onreadystatechange = function () {
    if (ajax.readyState==4 &&ajax.status==200) {
        //步骤五 如果能够进到这个判断 说明 数据 完美的回来了,并且请求的页面是存在的
        myChart.hideLoading();
        geoCoordMap=ajax.response;
        //将地图注册上去
        echarts.registerMap('guangzhou',ajax.response );
        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    }
}

var dataa=[
    {name:"荔湾区", value: [113.243038,23.124943,"荔湾区-1号店"]},
    {name:"海珠区", value: [113.262008,23.103131,"海珠区-1号店"]},
    {name:"越秀区", value: [113.280714,23.125624,"越秀区-1号店"]},
    {name:"天河区", value: [113.335367,23.13559,"天河区-1号店"]},
    {name:"黄埔区", value: [113.450761,23.103239,"黄埔区-1号店"]},
    {name:"白云区", value: [113.262831,23.162281,"白云区-1号店"]},
    {name:"番禺区", value: [113.364619,22.938582,"番禺区-1号店"]},
    {name:"南沙区", value: [113.53738,22.794531,"南沙区-1号店"]},
    {name:"从化区", value: [113.587386,23.545283,"从化区-1号店"]},
    {name:"花都区", value: [113.211184,23.39205,"花都区-1号店"]},
    {name:"增城区", value: [113.829579,23.290497,"增城区-1号店"]},
]

// 指定图表的配置项和数据
var option = {
    backgroundColor: '#ccc',
    title: {
        text: '广州市 echart -门店分布图',
        subtext: '数据来源于我瞎编的',
        sublink: 'http://lengff.xyz',
        x: 'center',
        itemGap:2,
        subtextStyle:{
            color:"#fff"
        },
        textStyle:{
            color:"#fff"
        }
    },
    tooltip: {
        trigger: 'item',
        formatter: function (params) {
            return params.name + ' : ' + params.value[2];
        }
    },
    legend: {
        orient: 'vertical',
        y: 'bottom',
        x:'right',
        data:['测试门店分布'],
        textStyle: {
            color: '#fff'
        }
    },
    geo: {
        map: 'guangzhou',
        roam: true,
        zoom:1.2,
        layoutSize:"50%",
        label: {
            emphasis: {
                show: true
            }
        },
        itemStyle: {
            normal: {
                areaColor: '#2b87bb',
                borderColor: '#73ffb3'
            },
            emphasis: {
                borderColor: '#fff',
                borderWidth: 1,
                areaColor: '#4e4e4e'
            }
        }
    },
    toolbox: {
        show: true,
        right: 'left',
        top: 0,
        feature: {
            dataView: {readOnly: false},
            restore: {},
            saveAsImage: {}
        }
    },
    series: [
        {
            name:'测试门店分布',
            type: 'scatter',
            coordinateSystem: 'geo',
            label: {
                normal: {
                    color:'#fff',
                    formatter: '{b}',
                    position: 'bottom',
                    show: true
                }
            },
            data: dataa,
            symbolSize: 30,
            encode: {value: 2},
            symbol:'pin',
            zlevel: 1
        }
    ]
}
