function initSkiplinks() {
    var sl = document.querySelector('#skiplinks');
    sl.className = 'withoutfocus';
    [].forEach.call(sl.querySelectorAll('a'), function(link) {
	link.addEventListener('focus', function() {
            sl.className = 'withfocus';
	});
	link.addEventListener('blur', function() {
            sl.className = 'withoutfocus';
	});
    });
}

function addscript(d,src,id) {
    var js,fjs=d.getElementsByTagName('script')[0];
    if(!d.getElementById(id)){
	js=d.createElement('script');
	js.defer='defer';
	js.async='async';
	js.id=id;
	js.src=src;
	fjs.parentNode.insertBefore(js,fjs);
    }
}

function initMyTweetbox() {
    document.querySelector('#sideblockwrap').innerHTML +=
        ('<aside id="tweetbox">'+
	    '<a class="twitter-timeline" data-dnt="true" href="https://twitter.com/rasmus_kaj"  data-widget-id="348079144619356161">Tweets by @rasmus_kaj</a>');
    document.querySelector('#skiplinks ul').innerHTML +=
    '<li><a href="#tweetbox">my tweets</a></li>';
    addscript(document,'http://platform.twitter.com/widgets.js',
	      'twitter-wjs')
}
function initMyLibthing() {
    document.querySelector('#sideblockwrap').innerHTML +=
       ('<aside id="booksbox"><h1>Några bra böcker</h1>'
	+'<div id="w5c54f5e485d879152955168d893d33ab"></div></aside>');
    theDestination='w5c54f5e485d879152955168d893d33ab';
    addscript(document,'http://www.librarything.com/widget_get.php?'+
	      'userid=kaj&theID=w5c54f5e485d879152955168d893d33ab',
	      'libthing-wjs')
    document.querySelector('#skiplinks ul').innerHTML += '<li><a href="#booksbox">några bra böcker</a></li>';
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('#latestcomments')) {
        initMyTweetbox();
        initMyLibthing();
    }
    initSkiplinks();
    kratsbox("figure > a");
}, false);
