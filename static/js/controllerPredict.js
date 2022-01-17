function model1Name() {
    $.ajax({
        url:'/predict/model1Name',
        type:'get',
        timeout:100,
        success:function(data) {
            for (var i=1;i<=data[0];i++)
            {
                $('.box ul.txt').append('<div class="onetxt" style="width: 30%;display: inline-block;">'+'<div class="datainput" style="float: right;margin-top: 3px;"><input type="number" step="0.0001" min="0" max="99999" name="'+data[i]+'"></div>'+'<div class="datatxt" style="float: right;line-height: 24px;">'+data[i]+' </div>'+'</div>');
            }
        },
        error:function(xhr,type,errorThrown) {
        }
    });
}
model1Name()


