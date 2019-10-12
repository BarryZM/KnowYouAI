var oAs=document.getElementsById("fir");
var oTxt=document.getElementById("txt");
var oTake=document.getElementById("take");
var cont=document.getElementById("cont");
//点击切换头像AI还是用户的
oAs.onOff=true;
oAs.onclick=function(){
    if(this.onOff){
        this.className="sec";
        this.onOff=false;
    }else{
        this.className="fir";
        this.onOff=true;
    }
}

//点击发送
oTake.onclick=function(){
    alert(">>>>")
    if(oTxt.value.length !=0){
        if(oAs.onOff){
            cont.innerHTML+= "<div class='lis_lf'><span class='peo'></span><p class='lis_txt'>"+oTxt.value+"</p></div>";
        }else{
              cont.innerHTML+= "<div class='lis_rt'><span class='peo'></span><p class='lis_txt'>"+oTxt.value+"</p></div>";
        }
        oTxt.value=" ";
    }else{
　　　　return false;
　　}

    //使滚动条一直保持在底端，来显示最新发布的消息
    //必学写在最后，不然获取的scrollHeight不是最新的
    cont.scrollTop = cont.scrollHeight;
}