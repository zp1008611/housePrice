var ec_bar= echarts.init(
            document.getElementById('visualbar'), 'white', {renderer: 'canvas'});
var option_bar = {
    "animation": true,
    "animationThreshold": 2000,
    "animationDuration": 1000,
    "animationEasing": "cubicOut",
    "animationDelay": 0,
    "animationDurationUpdate": 300,
    "animationEasingUpdate": "cubicOut",
    "animationDelayUpdate": 0,
    "color": [
        "#61a0a8",
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
            "type": "bar",
            "name": "单价(元/平米)",
            "legendHoverLink": true,
            "data": [
                58272.0,
                50151.0,
                42168.0,
                37615.0,
                33714.0,
                32826.0,
                29371.0,
                26405.0,
                22739.0,
                18834.0,
                15584.0,
            ],
            "showBackground": false,
            "barMinHeight": 0,
            "barCategoryGap": "50%",
            "barGap": "30%",
            "large": false,
            "largeThreshold": 400,
            "seriesLayoutBy": "column",
            "datasetIndex": 0,
            "clip": true,
            "zlevel": 0,
            "z": 0,
            "label": {
                "show": true,
                "position": "inside",
                "margin": 8
            },
            "rippleEffect": {
                "show": true,
                "brushType": "stroke",
                "scale": 2.5,
                "period": 4
            }
        },
        {
            "type": "line",
            "name": "房屋总价(万元)",
            "connectNulls": false,
            "yAxisIndex": 1,
            "symbolSize": 4,
            "showSymbol": true,
            "smooth": false,
            "clip": true,
            "step": false,
            "data": [
                [
                    "天河",
                    572.0
                ],
                [
                    "越秀",
                    374.0
                ],
                [
                    "海珠",
                    352.0
                ],
                [
                    "荔湾",
                    309.0
                ],
                [
                    "黄埔",
                    307.0
                ],
                [
                    "白云",
                    321.0
                ],
                [
                    "番禺",
                    369.0
                ],
                [
                    "南沙",
                    255.0
                ],
                [
                    "增城",
                    217.0
                ],
                [
                    "花都",
                    147.0
                ],
                [
                    "从化",
                    171.0
                ]
            ],
            "hoverAnimation": true,
            "label": {
                "show": true,
                "position": "top",
                "margin": 8
            },
            "lineStyle": {
                "show": true,
                "width": 1,
                "opacity": 1,
                "curveness": 0,
                "type": "solid",
                "color": "#2a5caa"
            },
            "areaStyle": {
                "opacity": 0
            },
            "itemStyle": {
                "color": "#2a5caa",
                "borderColor": "#2a5caa",
                "borderWidth": 3
            },
            "zlevel": 0,
            "z": 0,
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
                "单价(元/平米)",
                "房屋总价(万元)",
            ],
            "selected": {
                "单价(元/平米)": true,
                "房屋总价(万元)": true
            },
            "show": true,
            "padding": 5,
            "itemGap": 10,
            "itemWidth": 25,
            "itemHeight": 14,
			"left": '50%'
        }
    ],
    "tooltip": {
        "show": true,
        "trigger": "axis",
        "triggerOn": "mousemove|click",
        "axisPointer": {
            "type": "cross"
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
    "xAxis": [
        {
            "type": "category",
            "show": true,
            "scale": false,
            "nameLocation": "end",
            "nameGap": 15,
            "gridIndex": 0,
            "axisPointer": {
                "show": true,
                "type": "shadow"
            },
            "inverse": false,
            "offset": 0,
            "splitNumber": 5,
            "minInterval": 0,
            "splitLine": {
                "show": false,
                "lineStyle": {
                    "show": true,
                    "width": 1,
                    "opacity": 1,
                    "curveness": 0,
                    "type": "solid"
                }
            },
            "data": null
        }
    ],
    "yAxis": [
        {
            "type": "value",
            "show": true,
            "scale": false,
            "nameLocation": "end",
            "nameGap": 15,
            "gridIndex": 0,
            "axisTick": {
                "show": true,
                "alignWithLabel": false,
                "inside": false
            },
            "inverse": false,
            "offset": 0,
            "splitNumber": 5,
            "minInterval": 0,
            "splitLine": {
                "show": true,
                "lineStyle": {
                    "show": true,
                    "width": 1,
                    "opacity": 1,
                    "curveness": 0,
                    "type": "solid"
                }
            }
        },
        {
            "type": "value",
            "show": true,
            "scale": false,
            "nameLocation": "end",
            "nameGap": 15,
            "interval": 200,
            "gridIndex": 0,
            "inverse": false,
            "offset": 0,
            "splitNumber": 5,
            "min": 0,
            "max": 800,
            "minInterval": 0,
            "splitLine": {
                "show": false,
                "lineStyle": {
                    "show": true,
                    "width": 1,
                    "opacity": 1,
                    "curveness": 0,
                    "type": "solid"
                }
            }
        }
    ],
    "title": [
        {
            "text": "广州各区二手房价格",
            "subtext": "数据来自链家网",
            "padding": 5,
            "itemGap": 10
        }
    ]
};
ec_bar.setOption(option_bar);