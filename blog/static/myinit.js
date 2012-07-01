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
        '<div class="sideblock" id="tweetbox"><h2>My tweets</h2></div>');
    $('#skiplinks ul').append('<li><a href="#tweetbox">my tweets</a></li>');
    initSkiplinks($('#skiplinks a[href=#tweetbox]'));
    $('#tweetbox').tweet({
        username: "rasmus_kaj",
        join_text: "auto",
        avatar_size: 0,
        count: 5,
        auto_join_text_default: ":",
        auto_join_text_ed: "I",
        auto_join_text_ing: "I were",
        auto_join_text_reply: "I replied to",
        auto_join_text_url: ":"
    });
}
