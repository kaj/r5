!function(d){if ('querySelector' in d && 'addEventListener' in window &&
                 'forEach' in Array) {

    function initSkiplinks() {
        var sl = d.getElementById('skiplinks');
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
        if (!d.getElementById(id)) {
            var e=d.createElement('script');
            e.defer=e.async=true;
            e.id=id;
            e.src=src;
            d.querySelector('head').appendChild(e);
        }
    }
    
    d.addEventListener('DOMContentLoaded', function() {
        if (d.getElementById('latestcomments')) {
            d.getElementById('sideblockwrap').innerHTML +=
            ('<aside id="tweetbox">'+
             '<a class="twitter-timeline" href="https://twitter.com/rasmus_kaj"'+
             ' data-dnt="true"  data-widget-id="348079144619356161">'+
             'Tweets by @rasmus_kaj</a></aside>'+
             '<aside id="booksbox"><h1>Några bra böcker</h1>'+
             '<div id="w5c54f5e485d879152955168d893d33ab"></div></aside>');
            d.querySelector('#skiplinks ul').innerHTML +=
            ('<li><a href="#tweetbox">my tweets</a></li> '+
             '<li><a href="#booksbox">några bra böcker</a></li>');
            addscript('http://platform.twitter.com/widgets.js', 'twitter-wjs')
            addscript('http://www.librarything.com/widget_get.php?userid=kaj'+
                      '&theID=w5c54f5e485d879152955168d893d33ab', 'libthing-wjs')
        }
        initSkiplinks();
        kratsbox("figure > a", kbsettings);
    }, false);
}}(document);
