
$(window).load(function() {
    
    $("#tabs").tabs();
    if(!$.browser.mozilla){
	alert("Only tested for Mozilla Firefox. Use at your own risk");
    }

});

function bodyinit(){
    $("body").trigger("cLoad");
}




function calculateFontSize(title,desiredWidth,desiredHeight){
    size = 1;
    $fontEl = $("<div class ='geo-invisible' />")
	.text(title)
	.appendTo($("body"))
	.css("font-size",size+"px");
    do{
	$fontEl.css("font-size",(size++)+("px"));
    }
    while($fontEl.width() < desiredWidth && $fontEl.height() < desiredHeight);
    $fontEl.remove();
    return size-1;
    
}