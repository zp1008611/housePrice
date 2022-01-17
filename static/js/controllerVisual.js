// ajax前后台交互代码
// 右上角时间模块的更新
function gettime() {
    $.ajax({
        url:'/visual/time',
        type:'get',
        timeout:10000,
        success:function(data) {
            $('#visualtime').html(data)
        },
        error:function(xhr,type,errorThrown) {
            
        }
    });
}
// 模块数据
function get_data() {
    $.ajax({
        url:'/visual/data',
        success:function(data) {
            option_bar.series[0].data = data.avePrice
            option_bar.series[1].data = data.allprice
            option_map.series[0].data = data.map
            option_pie.series[0].data = data.pie
            ec_bar.setOption(option_bar)
            ec_map.setOption(option_map)
            chart_pie.setOption(option_pie)
        },
        error:function(xhr,type,errorThrown) {
        }
    });
}
// 调用函数
gettime() // 我们先调用一次这个函数，防止第一次刷新页面有空白
get_data()
setInterval(gettime,1000)
setInterval(get_data,100000)
