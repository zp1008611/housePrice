var ec_map = echarts.init(
	document.getElementById('visualMap'), 'white', {renderer: 'canvas'});
var option_map = {
"animation": true,
"animationThreshold": 2000,
"animationDuration": 1000,
"animationEasing": "cubicOut",
"animationDelay": 0,
"animationDurationUpdate": 300,
"animationEasingUpdate": "cubicOut",
"animationDelayUpdate": 0,
"color": [
"#c23531",
"#2f4554",
"#61a0a8",
"#d48265",
"#749f83",
"#ca8622",
"#bda29a",
"#6e7074",
"#546570",
"#c4ccd3",
"#f05b72",
"#ef5b9c",
"#f47920",
"#905a3d",
"#fab27b",
"#2a5caa",
"#444693",
"#726930",
"#b2d235",
"#6d8346",
"#ac6767",
"#1d953f",
"#6950a1",
"#918597"
],
"series": [
{
	"type": "map",
	"name": "近七日广州二手房区域单价",
	"label": {
		"show": false,
		"position": "top",
		"margin": 8
	},
	"mapType": "广州",
	"data": [
		{
			"name": "\u5929\u6cb3\u533a",
			"value": 58272.0
		},
		{
			"name": "\u8d8a\u79c0\u533a",
			"value": 50151.0
		},
		{
			"name": "\u6d77\u73e0\u533a",
			"value": 42168.0
		},
		{
			"name": "\u8354\u6e7e\u533a",
			"value": 37615.0
		},
		{
			"name": "\u9ec4\u57d4\u533a",
			"value": 33714.0
		},
		{
			"name": "\u767d\u4e91\u533a",
			"value": 32826.0
		},
		{
			"name": "\u756a\u79ba\u533a",
			"value": 29371.0
		},
		{
			"name": "\u5357\u6d77\u533a",
			"value": 26405.0
		},
		{
			"name": "\u5357\u6c99\u533a",
			"value": 22739.0
		},
		{
			"name": "\u589e\u57ce\u533a",
			"value": 18834.0
		},
		{
			"name": "\u82b1\u90fd\u533a",
			"value": 15584.0
		},
		{
			"name": "\u987a\u5fb7\u533a",
			"value": 15482.0
		},
		{
			"name": "\u4ece\u5316\u533a",
			"value": 13092.0
		}
	],
	"roam": false,
	"aspectScale": 0.75,
	"nameProperty": "name",
	"selectedMode": false,
	"zoom": 1,
	"mapValueCalculation": "sum",
	"showLegendSymbol": false,
	"emphasis": {}
}
],
"legend": [
{
	"data": [
		"近七日广州二手房区域单价"
	],
	"selected": {
		"\u5e7f\u5dde\u533a\u57df\u623f\u4ef7": true
	},
	"show": false,
	"padding": 5,
	"itemGap": 10,
	"itemWidth": 25,
	"itemHeight": 14
}
],
"tooltip": {
"show": true,
"trigger": "item",
"triggerOn": "mousemove|click",
"axisPointer": {
	"type": "line"
},
"showContent": true,
"alwaysShowContent": false,
"showDelay": 0,
"hideDelay": 100,
"textStyle": {
	"fontSize": 14
},
"borderWidth": 0,
"padding": 5
},
"title": [
{
	"text": "近七日广州二手房区域单价",
	"subtext": "数据来自链家网",
	"top": "top",
	"padding": 5,
	"itemGap": 10
}
],
"visualMap": {
"show": true,
"type": "continuous",
"min": 13092.0,
"max": 58272.0,
"text": [
	"High",
	"Low"
],
"inRange": {
	"color": [
		"lightskyblue",
		"yellow",
		"orangered"
	]
},
"calculable": true,
"inverse": false,
"splitNumber": 5,
"dimension": 0,
"orient": "vertical",
"left": "10",
"top": "center",
"showLabel": true,
"itemWidth": 20,
"itemHeight": 140,
"borderWidth": 0
}
};
ec_map.setOption(option_map);