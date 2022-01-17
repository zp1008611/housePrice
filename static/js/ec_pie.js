var chart_pie = echarts.init(
    document.getElementById('visualpie'), 'white', {renderer: 'canvas'});
var option_pie = {
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
    "type": "pie",
    "clockwise": true,
    "data": [
        {
            "name": "\u82b1\u90fd",
            "value": 211
        },
        {
            "name": "\u4ece\u5316",
            "value": 1562
        },
        {
            "name": "\u9ec4\u57d4",
            "value": 2604
        },
        {
            "name": "\u8354\u6e7e",
            "value": 2639
        },
        {
            "name": "\u5929\u6cb3",
            "value": 2694
        },
        {
            "name": "\u8d8a\u79c0",
            "value": 2719
        },
        {
            "name": "\u767d\u4e91",
            "value": 2732
        },
        {
            "name": "\u756a\u79ba",
            "value": 2738
        },
        {
            "name": "\u5357\u6c99",
            "value": 2750
        },
        {
            "name": "\u589e\u57ce",
            "value": 2779
        },
        {
            "name": "\u6d77\u73e0",
            "value": 2860
        }
    ],
    "radius": [
        "5%",
        "57%"
    ],
    "center": [
        "55%",
        "50%"
    ],
    "label": {
        "show": true,
        "position": "top",
        "margin": 8,
        "formatter": "{b}:\n {c}"
    },
    "rippleEffect": {
        "show": true,
        "brushType": "stroke",
        "scale": 2.5,
        "period": 4
    }
}
],
"legend": [
{
    "data": [
        "\u987a\u5fb7",
        "\u82b1\u90fd",
        "\u4ece\u5316",
        "\u5357\u6d77",
        "\u9ec4\u57d4",
        "\u8354\u6e7e",
        "\u5929\u6cb3",
        "\u8d8a\u79c0",
        "\u767d\u4e91",
        "\u756a\u79ba",
        "\u5357\u6c99",
        "\u589e\u57ce",
        "\u6d77\u73e0"
    ],
    "selected": {},
    "show": true,
    "left": "2%",
    "top": "15%",
    "orient": "vertical",
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
    "text": "\u5e7f\u5dde\u4e8c\u624b\u623f\u5206\u533a\u623f\u6e90\u603b\u6570\u5360\u6bd4",
    "subtext": "\u6570\u636e\u6765\u81ea\u94fe\u5bb6\u7f51",
    "padding": 5,
    "itemGap": 10
}
]
};
chart_pie.setOption(option_pie);