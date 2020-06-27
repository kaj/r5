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
             'Tweets by @rasmus_kaj</a></aside>');
            d.querySelector('#skiplinks ul').insertAdjacentHTML('beforeend',
             '<li><a href="#tweetbox">my tweets</a></li>');
            addscript('//platform.twitter.com/widgets.js', 'twitter-wjs')
        }
        initSkiplinks();
        kratsbox("figure > a", kbsettings);
        socbox('#socialwidgets .twitter', function(e) {
            return e.href + "?text=" + encodeURIComponent(e.getAttribute('data-text')) + "&url=" + encodeURIComponent(d.location) + "&via=" + encodeURIComponent(e.getAttribute('data-via'));
        });
        socbox('#socialwidgets .facebook', function(e) {
            return e.href+'?u='+encodeURIComponent(d.location)+'&display=popup';
        });
	var t = d.querySelector('#writecomment textarea');
	if (t) {
	    t.style.height = '5.2em'
	    t.style.maxHeight = '20em'
	    var p = t.parentNode;
	    t.onkeyup = function() {
		p.style.height = p.scrollHeight + 'px';
		t.style.height = '5.2em';
		t.style.height = t.scrollHeight + 'px';
		p.style.height = null;
	    }
	}
        [].forEach.call(document.querySelectorAll('.wrapiframe'), function(w) {
            var f = w.querySelector('iframe[height][width]');
            if (f) {
                w.style.paddingBottom = 100 * f.height / f.width + '%';
            }
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
