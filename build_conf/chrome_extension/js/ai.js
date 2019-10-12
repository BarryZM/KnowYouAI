

// 获取当前选项卡ID
function getCurrentTabId(callback)
{
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs)
	{
		if(callback) callback(tabs.length ? tabs[0].id: null);
	});
}


function executeScriptToCurrentTab(code)
{
	getCurrentTabId((tabId) =>
	{
		chrome.tabs.executeScript(tabId, {code: code});
	});
}

function executeScriptToCurrentTabByFile(file_name)
{
	getCurrentTabId((tabId) =>
	{
		chrome.tabs.executeScript(tabId, {file: file_name});
	});
}

// 演示2种方式操作DOM

//// 修改背景色
//$('#update_bg_color').click(() => {
//	executeScriptToCurrentTab('document.body.style.backgroundColor="red";')
//});



//$('#change').click(function(){
////    alert("改DOM啦")
//    executeScriptToCurrentTabByFile("js/content.js")
////    executeScriptToCurrentTab('document.body.style.backgroundColor="red"');
//
//})
function clean(str,max_number){
    //超过max_number换行
    var t = ""
    var size_of_line = max_number
    if (str.length > size_of_line){
        for(var i=0;i<str.length;i++){
            if((i+1) % size_of_line == 0){
                t+="</br>" + str[i]
            }else{
                t+=str[i]
            }
        }
    }else{
        t = str
    }
    return t;
}

function send(query){
    request_url = "<build_params>host</build_params>/extension_dialogue";
    $.ajax({
      url:request_url,
      type: "POST",
      data: JSON.stringify({
            "user_id":"<build_params>userid</build_params>",
            "query":query// 注意不要在此行增加逗号
      }),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success:function(data,stata){
           //如果data是json，自动data编程了json
            var t = data["response"]
            var cont = $('#cont')
            var last = cont.html()
            var ai_response = last + "<div class='lis_lf'><span class='peo'></span><p>"+t+"</p></div>";
            cont.html(ai_response)
            var position = cont[0].scrollHeight
            cont.scrollTop(position);
      },
      error:function(XMLHttpRequest, textStatus, errorThrown) {
            // XMLHttpRequest是一个obj
           reason = JSON.stringify(XMLHttpRequest)
      }
    })
}

//$('#send').click(function(){
//    //点击发送后
//    send()
////    alert("OK "+request_url)
//
//})

//来自content.js的通信
//chrome.runtime.onMessage.addListener(function(request, sender, sendResponse)
//{
//	// console.log(sender.tab ?"from a content script:" + sender.tab.url :"from the extension");
//	if(request.cmd == 'test') alert(request.value);
//	sendResponse('我收到了你的消息！');
//});
IDEX = 0
$('#take').click(function(){
//    alert("send")
//    oText = $('#txt').text()
    var text = $('#txt').val()
    $("#txt").val("") //清空
    var t = clean(text,20)
    var cont = $('#cont')
//    alert(text)
    var last = cont.html()
    //更新用户的输入
    var user_inp =last + "<div class='lis_rf'><span class='peo'></span><p class=\'lis_rf_p\'>"+t+"</p></div>";
//    var ai_response = "<div class='lis_lf'><span class='peo'></span><p>"+t+" 1"+"</p></div>";
    cont.html(user_inp)
    send(text)
    var position = cont[0].scrollHeight
//    alert(position)
    cont.scrollTop(position);
})


$(document).keyup(function(event){
 if(event.keyCode ==13){
  $("#take").trigger("click");
 }
});
//alert($("#take").click)