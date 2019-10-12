
//每次刷新插件会被执行一次，至永远
STATE = 0 //BEGIN
DATA = null
function SendToServer(data_str,func){
    request_url = "<build_params>host</build_params>/extension";
    $.ajax({
      url:request_url,
      type: "POST",
      data: data_str,
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success:function(data,stata){
           //如果data是json，自动data编程了json
            func(data)
      },
      error:function(XMLHttpRequest, textStatus, errorThrown) {
            // XMLHttpRequest是一个obj
           reason = JSON.stringify(XMLHttpRequest)
      }
    })
}



chrome.contextMenus.create({
	title: "功能尚未开发",
	onclick: function(){alert("功能尚未开发");}
});




// 监听来自content-script的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse)
{
    sendResponse("OK")
    SendToServer(JSON.stringify(request),function(data){})





});