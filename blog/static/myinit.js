function initSkiplinks(selector) {
    selector.focus(function() {
        $('#skiplinks').addClass('withfocus').removeClass('withoutfocus');
    });
    selector.blur(function() {
        $('#skiplinks').removeClass('withfocus').addClass('withoutfocus');
    });
}
function initMyTweetbox() {
    $('#sideblockwrap').append(
        '<aside id="tweetbox">'+
	    '<a class="twitter-timeline" data-dnt="true" href="https://twitter.com/rasmus_kaj"  data-widget-id="348079144619356161">Tweets by @rasmus_kaj</a>'+
	    '<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?\'http\':\'https\';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+"://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>');
    $('#skiplinks ul').append('<li><a href="#tweetbox">my tweets</a></li>');
    initSkiplinks($('#skiplinks a[href=#tweetbox]'));
}
function initMyLibthing() {
    $('#sideblockwrap').append(
        '<aside id="booksbox"><h1>Några bra böcker</h1>'
	+'<div id="w5c54f5e485d879152955168d893d33ab"></div>'
	+'<script type="text/javascript" charset="UTF-8" src="'
	+'http://www.librarything.com/widget_get.php?userid=kaj&amp;'
	+'theID=w5c54f5e485d879152955168d893d33ab"></script></aside>');
    $('#skiplinks ul').append('<li><a href="#booksbox">några bra böcker</a></li>');
    initSkiplinks($('#skiplinks a[href=#booksbox]'));
}

$(document).ready(function() {
    $('#skiplinks').addClass('withoutfocus');
    initSkiplinks($('#skiplinks a'));
    $("figure > a").kratsbox();
    if ($('#latestcomments').size()) {
        initMyTweetbox();
        initMyLibthing();
    }
});
