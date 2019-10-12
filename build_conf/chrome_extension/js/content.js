//每打开一个新页面就会被load进来一次，页内跳转不会变，修改一次需要重新载入插件
//load完后猜展示界面,

//function sendMessageToContentScript(message, callback)
//{
//	chrome.tabs.query({active: true, currentWindow: true}, function(tabs)
//	{
//		chrome.tabs.sendMessage(tabs[0].id, message, function(response)
//		{
//			if(callback) callback(response);
//		});
//	});
//}



//全部元素加载完成后执行
window.addEventListener("load", function(event){
        var p_list = $("p")
        var array = []
        for(var i=0;i<p_list.length;i++){
            array.push(p_list[i].innerHTML)
        }
        var span_list = $("span")
        for(var i=0;i<span_list.length;i++){
            array.push(span_list[i].innerHTML)
        }
        message_json = {
            "user_id":"<build_params>userid</build_params>",
            "url":window.location.href,
            "p":array
        }
        var wait_time = 0
        var t1=window.setInterval(function(){
             chrome.runtime.sendMessage(message_json, function(response) {
                wait_time += 1
                if(wait_time > 5){
                    wait_time = 0
                    window.clearInterval(t1);
                }
                if(!response.startsWith('WAIT')){
                    //处理response
//                    $(".s_tab_inner").text(response);
                    //清空定时器
                    window.clearInterval(t1);
                    wait_time = 0
                }
            });
        }, 1000);

});
