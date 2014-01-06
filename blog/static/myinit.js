if ('querySelector' in document && 'addEventListener' in window &&
    'forEach' in Array) {

    function initSkiplinks() {
        var sl = document.querySelector('#skiplinks');
        sl.className = 'withoutfocus';
        Array.prototype.forEach.call(sl.querySelectorAll('a'), function(link) {
            link.addEventListener('focus', function() {
                sl.className = 'withfocus';
            });
            link.addEventListener('blur', function() {
                sl.className = 'withoutfocus';
            });
        });
    }
    
    function addscript(src,id) {
        if (!document.getElementById(id)) {
            var e=document.createElement('script');
            e.defer=e.async=true;
            e.id=id;
            e.src=src;
            document.querySelector('head').appendChild(e);
        }
    }
    
    function initMyTweetbox() {
        document.querySelector('#sideblockwrap').innerHTML +=
        ('<aside id="tweetbox">'+
         '<a class="twitter-timeline" href="https://twitter.com/rasmus_kaj"'+
         ' data-dnt="true"  data-widget-id="348079144619356161">'+
         'Tweets by @rasmus_kaj</a>');
        addscript('http://platform.twitter.com/widgets.js', 'twitter-wjs')
        document.querySelector('#skiplinks ul').innerHTML +=
        '<li><a href="#tweetbox">my tweets</a></li>';
    }
    function initMyLibthing() {
        document.querySelector('#sideblockwrap').innerHTML +=
        ('<aside id="booksbox"><h1>Några bra böcker</h1>'
         +'<div id="w5c54f5e485d879152955168d893d33ab"></div></aside>');
        addscript('http://www.librarything.com/widget_get.php?userid=kaj'+
                  '&theID=w5c54f5e485d879152955168d893d33ab', 'libthing-wjs')
        document.querySelector('#skiplinks ul').innerHTML +=
        '<li><a href="#booksbox">några bra böcker</a></li>';
    }
    
    document.addEventListener('DOMContentLoaded', function() {
        if (document.querySelector('#latestcomments')) {
            initMyTweetbox();
            initMyLibthing();
        }
        initSkiplinks();
        kratsbox("figure > a", kbsettings);
    }, false);
}
