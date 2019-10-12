
//建立一個可存取到該file的url
function getObjectURL(file) {
        var url = null ;
        if (window.createObjectURL!=undefined) { // basic
            url = window.createObjectURL(file) ;
        } else if (window.URL!=undefined) { // mozilla(firefox)
            url = window.URL.createObjectURL(file) ;
        } else if (window.webkitURL!=undefined) { // webkit or chrome
            url = window.webkitURL.createObjectURL(file) ;
        }
        return url ;
 }


var text = $("#f-left");
text.focus();

function send(query){
    var  host = $("#host").attr("value")
    var request_url = host + "/web";
    var user_id = $("#user_id").attr("value")
    $.ajax({
      url:request_url,
      type: "POST",
      data: JSON.stringify({
            "user_id":user_id,
            "query":query// 注意不要在此行增加逗号
      }),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success:function(data,stata){
           //如果data是json，自动data编程了json
            var result = data["response"]
            var body_obj = $(".b-body")
            body_obj.append("<div class='rotWord'><span style=\"background:url('/static/img/rot.png')\"></span> <p id='member'>" + result + "</p></div>");
			var activate = data["activate"]
			if (activate.length > 0){
			    body_obj.append("<div class='rotWord'><span style=\"background:url('/static/img/rot.png')\"></span> <p id='member'>" + activate + "</p></div>");
			}
			body_obj.scrollTop(10000000);
      },
      error:function(XMLHttpRequest, textStatus, errorThrown) {
            // XMLHttpRequest是一个obj
           reason = JSON.stringify(XMLHttpRequest)
      }
    })
}

function action(){
	if(text.val()==null||text.val()==""){
		text.focus();
		return;
	}
	$(".b-body").append("<div class='mWord'><span style=\"background:url('/static/img/my.png')\"></span><p>" + text.val() + "</p></div>");
	$(".b-body").scrollTop(10000000);
	var query = text.val()
	send(query)
	text.val("");
	text.focus();
}

function upload_image(){
        var user_id = $("#user_id").attr("value")
        var  host = $("#host").attr("value")
        var formData = new FormData($('#uploadForm')[0]);
        $.ajax({
            url:host + "/web_image?user_id="+user_id,
            type: "POST",
            data: formData,
            async: true,
            cashe: false,
            contentType:false,
            processData:false,
            success:function (data) {
                data = JSON.parse(data)
                var result = data["response"]
                var body_obj = $(".b-body")
                body_obj.append("<div class='rotWord'><span style=\"background:url('/static/img/rot.png')\"></span> <p id='member'>" + result + "</p></div>");
			    var activate = data["activate"]
			    if (activate.length > 0){
			        body_obj.append("<div class='rotWord'><span style=\"background:url('/static/img/rot.png')\"></span> <p id='member'>" + activate + "</p></div>");
			    }
			    body_obj.scrollTop(10000000);
        　　},
        　　error: function (returndata) {
        　　　　　alert("上传失败！")
            }
        })
//        $.ajaxFileUpload({
//            url:"http://localhost/web_image?user_id="+user_id,
//            fileElementId: "upload", //文件上传域的ID，这里是input的ID，而不是img的
//            dataType: 'json', //返回值类型 一般设置为json
//            contentType: "application/x-www-form-urlencoded; charset=utf-8",
//            success: function (data) {
//                alert(data.code+" "+ data.msg);
//                if (data.code==200){
//
//                }
//
//            }
//
//        });
}


$("#btn1").click(function(){
	$("#upload").click(); //隐藏了input:file样式后，点击头像就可以本地上传
    $("#upload").on("change",function(){
        var objUrl = getObjectURL(this.files[0]) ; //获取图片的路径，该路径不是图片在本地的路径
        if (objUrl) {
            var img_tag = "<img src=" + objUrl +" style=\"width:128px;height:128px;\"/>"
            $(".b-body").append("<div class='mWord'><span style=\"background:url('/static/img/my.png')\"></span><p>" + img_tag + "</p></div>");
            $(".b-body").scrollTop(10000000);
            upload_image()
            $("#upload").replaceWith('<input id="upload" name="file" accept="image/*" type="file" style="display: none"/>')
        }
    });

});

$("#btn2").click(function(){
		action()
});

$(document).keydown(function(event){
	if(event.keyCode==13)
	{
		action();
	}
});

