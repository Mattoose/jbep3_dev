var IS_ENGINE = ( navigator.userAgent == "JaykinBacon" );

if ( !IS_ENGINE ) $(function(){ $(document).trigger('CEFReady') });
var bDisplayedSplash = false;

$(document).on('CEFReady', function() {	
	// We're good to go, start fading in, do the fancy stuff.	
	$("#video").show();
	$('#video video').bind("ended", displaySplash);
	var introVideo = $('#video video').get(0);
	introVideo.volume = 0.25;
	introVideo.play();
});

$(document).click(displaySplash)

function displaySplash()
{
	if ( bDisplayedSplash ) return;
	bDisplayedSplash = true;
	
	// Hide video
	var introVideo = $('#video video').get(0);			
	introVideo.pause();
	$("#video").hide();
	
	// Show splash
	splashBackgroundScrollLoop();

	$("#splash").fadeIn();
		
	$("#splash #logo").delay(1500).fadeIn(3000);
	$("#splash #background div").delay(500).animate( { "opacity":"0.35" }, 2500 );	
	
	if ( IS_ENGINE ) INTRO.displayedVideo();	
}

// Splash background scroll
var dir_1 = [ (Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1 ];		
var pos_1 = [Math.random()*500,Math.random()*500,Math.random()*250,Math.random()*250];

function splashBackgroundScrollLoop()
{
	$( "#splash #background #layer_1" ).css("background-position",pos_1[0]+"px "+pos_1[1]+"px");
	$( "#splash #background #layer_2" ).css("background-position",pos_1[2]+"px "+pos_1[3]+"px");
	
	pos_1[0] += dir_1[0];
	pos_1[1] += dir_1[1];
	pos_1[2] += dir_1[2];
	pos_1[3] += dir_1[3];
	
	setTimeout(splashBackgroundScrollLoop, 10);
}