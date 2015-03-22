!function(d,w,ap){if ('querySelector' in d && 'addEventListener' in w &&
                      'forEach' in ap) {

    function initSkiplinks() {
        var sl = d.getElementById('skiplinks');
        sl.className = 'withoutfocus';
        ap.forEach.call(sl.querySelectorAll('a'), function(a) {
            a.addEventListener('focus', function() {
                sl.className = 'withfocus';
            });
            a.addEventListener('blur', function() {
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
    function socbox(sel, uf) {
        var t = d.querySelector(sel);
        if (t) {
            t.onclick = function(e) {
                window.open(uf(t), 'socbox',
                            'toolbar=no,location=no,status=no,menubar=no,width=600,height=300')
                    .moveTo(e.screenX-50, e.screenY-120);
                return false;
            }
        }
    }
    function rkinit() {
        if (d.getElementById('latestcomments')) {
            d.getElementById('sideblockwrap').insertAdjacentHTML('beforeend',
             '<aside id="tweetbox">'+
             '<a class="twitter-timeline" href="https://twitter.com/rasmus_kaj"'+
             ' data-dnt="true" data-widget-id="348079144619356161">'+
             'Tweets by @rasmus_kaj</a></aside>'+
             '<aside id="booksbox"><h1>Några bra böcker</h1>'+
             '<div id="w5c54f5e485d879152955168d893d33ab"></div></aside>');
            d.querySelector('#skiplinks ul').insertAdjacentHTML('beforeend',
             '<li><a href="#tweetbox">my tweets</a></li> '+
             '<li><a href="#booksbox">några bra böcker</a></li>');
            addscript('http://platform.twitter.com/widgets.js', 'twitter-wjs')
            addscript('http://www.librarything.com/widget_get.php?userid=kaj'+
                      '&theID=w5c54f5e485d879152955168d893d33ab', 'libthing-wjs')
        }
        initSkiplinks();
        kratsbox("figure > a", kbsettings);
        socbox('#socialwidgets .twitter', function(e) {
            return e.href + "?text=" + encodeURIComponent(e.getAttribute('data-text')) + "&url=" + encodeURIComponent(d.location) + "&via=" + encodeURIComponent(e.getAttribute('data-via'));
        });
        socbox('#socialwidgets .facebook', function(e) {
            return e.href+'?u='+encodeURIComponent(d.location)+'&display=popup';
        });
    }
    if (d.readyState == 'complete'
        || d.readyState == 'loaded'
        || d.readyState == 'interactive') {
        rkinit()
    } else {
        d.addEventListener('DOMContentLoaded', rkinit, false)
    }
}}(document,window,Array.prototype);
