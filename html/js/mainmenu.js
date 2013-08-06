var IS_ENGINE = ( navigator.userAgent == "JaykinBacon" );
var IN_GAME = false;
var TOTAL_BACKGROUNDS = 2;

if ( !IS_ENGINE ) $(function(){ $(document).trigger('CEFReady') });
var bDisplayedSplash = false;

var iState = -1;
var iMaxState = 2;


// Auto scaling...
function updateScale()
{			
	// Resize if we get small
	var w = Math.min(1, $(window).width()/1280);
	window.document.body.style.setProperty('zoom', w, 'important')	
}

$( updateScale );
$(window).resize(updateScale);

function updateGameState( inGame )
{
	if ( inGame == IN_GAME )
        return;
        
    while (iState < iMaxState) cycleMenuState();

    IN_GAME = inGame;
    updateMenu();
}

function cycleMenuState()
{
	if ( iState >= iMaxState ) return;
	
	console.log("Cycling menu state from "+iState+" to "+(iState+1)+".");
	iState++;
	
	if ( iState == 0 ) // start into sequence
	{
		$("#video").show();
		$('#video video').bind("ended", cycleMenuState);
		var introVideo = $('#video video').get(0);
		introVideo.volume = 0.2;
		introVideo.play();
	}
	else if ( iState == 1 ) // display splash, start menu musiq
	{
		console.log("TODO: We've endered iState 1, play our menu music.");
		
		// Hide video
		var introVideo = $('#video video').get(0);			
		introVideo.pause();
		$("#video").hide();
		
		// Show splash
		splashBackgroundScrollLoop();
	
		$("#splash").fadeIn();
			
		$("#splash #logo").delay(1500).fadeIn(3000);
		$("#splash #background div").delay(500).animate( { "opacity":"0.35" }, 2500 );
	}
	else if ( iState == 2 ) // Main menu.
	{
		$("#splash").fadeOut();
    	$("#menu").fadeIn(IN_GAME ? 0 : 1000);
	}
}

$(document).on('CEFReady', function() {
    updateMenu();	
	$(document).click(cycleMenuState);
	cycleMenuState();
});
	
// Setup brackground
$( function() {
	$("#menu #background #bg_img").css('background-image', 'url(img/mainmenu/menu_bg_' + (Math.floor(Math.random()*TOTAL_BACKGROUNDS)+1) + '.png)');
});
	
	
/*
 * Intro video & splash
 */

// Splash background scroll
var dir_1 = [ (Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1 ];		
var pos_1 = [Math.random()*500,Math.random()*500,Math.random()*250,Math.random()*250];

function splashBackgroundScrollLoop()
{
	if ( iState > 1 ) return;
	$( "#splash #background #layer_1" ).css("background-position",pos_1[0]+"px "+pos_1[1]+"px");
	$( "#splash #background #layer_2" ).css("background-position",pos_1[2]+"px "+pos_1[3]+"px");
	
	pos_1[0] += dir_1[0];
	pos_1[1] += dir_1[1];
	pos_1[2] += dir_1[2];
	pos_1[3] += dir_1[3];
	
	setTimeout(splashBackgroundScrollLoop, 10);
}

/*
 MENU
*/

var CURRENT_PAGE = false;
var PAGE_FRONT = false;
var PAGE_CUSTOMISATION = "player_customization";
var PAGE_FINDSERVER = "findserver";

function changePage( desired_page )
{
	if ( desired_page == CURRENT_PAGE ) 
		return;
		
	if ( desired_page != PAGE_FRONT && CURRENT_PAGE != PAGE_FRONT ) // If we're not on front page and want to change to a different non-front page, stop.
		return;
		
	if ( desired_page != PAGE_FRONT ) 
	{
		$("#menu #links").animate({"width":"0px"},250);
		$("#menu #"+desired_page).animate({"left":"6%"},250);		
	}
	else
	{
		$("#menu #"+CURRENT_PAGE).animate({"left":"106%"},250);	
		$("#menu #links").animate({"width":"90%"},250);	
	}
		
	CURRENT_PAGE = desired_page;
}

var menu_options = {
	// Button ID, Button Text, Button Desc, Display in menu, Display in game, Handled in webpage, func on open
	"resume" : [ "RESUME GAME", "Return to the current game.", false, true, false ], // Button text, button desc, display in game.
	"disconnect":[ "DISCONNECT", "Disconnect from the current game.", false, true, false ],
	//"playerlist":[ "PLAYER LIST", "Other players in the current game.", false, true, false ],
	//"findserver_new":[ "FIND SERVERS", "Find a server.", true, true, PAGE_FINDSERVER, findServerTabOpen ],
	"findservers":[ "FIND SERVERS (TEMP)", "Find servers.", true, false, false ],
	"createserver":[ "CREATE SERVER", "Create a local or internet server.", true, false, false ],
	"customizeplayer":[ "CUSTOMIZE PLAYER", "Change your player model.", true, true, PAGE_CUSTOMISATION ],
	"options":[ "OPTIONS", "Change game options.", true, true, false ],
	"donate":[ "DONATE", "Support our mod.", true, true, false ],
	"quit":[ "QUIT", "Quit the game.", true, true, false ]
};

function updateMenu()
{
	$("#menu #links").html("");
	
	for (var link in menu_options)
	{
		var link_data = menu_options[link];
		var link_html = '<li id="'+link+'" onclick="menuClick(this);">'+link_data[0]+'</li>';
		
		if ( (!IN_GAME && link_data[2]) || (IN_GAME && link_data[3]) )
			$("#menu #links").append(link_html);
	}
	
	// Update desc on mouseover
	var link_desc = $("#menu #link_description");
	
	$("#menu #links li").hover(function(){ 
		link_desc.text(menu_options[$(this).attr("id")][1]); 
	},
	function(){ 
		link_desc.text(""); 
	});

	// If we're in game, let user see through background
	if ( IN_GAME )
	{
		$("body").css("background-color","rgba(0,0,0,0.4)");
		$("#menu #background #bg_img").hide();
	}
	else
	{				
		$("#menu #background #bg_img").show();
        $("body").css("background-color","black");
	}
}

// Menu links
function menuClick( button_div )
{
	var pressed = $(button_div).attr('id');
	var button_data = menu_options[pressed];
	
	if ( button_data[4] != false ) // Handled by page
		changePage( button_data[4] );
	else
		if ( IS_ENGINE ) MENU.buttonPress(pressed);
	
	if ( button_data[5] != undefined && button_data[5] != false )
		button_data[5]();
}

// PLAYER CUSTOMIZATION
var PLAYER_DEFAULTIMG_BIG = "img/mainmenu/players/missing.png";
var PLAYER_DEFAULTIMG_THUMB = "img/mainmenu/players/preview/missing.png";
var PLAYER_MODELS;
var CURRENT_PLAYER = false;

function setupPlayerModels()
{
	
	PLAYER_MODELS = {};
    var playerModels;
    var target_element = $('#player_customization #selection #options .mCSB_container');
    var active_model = CURRENT_PLAYER;

	if ( !IS_ENGINE )
	{	
		var playerModels = [ 
			["postal", "Test Model", false, true ],
			["postal2", "Test Model 2", false ],
			["postal3", "Test Model 3", false ],
			];
		}
	else
	{	
		playerModels = MENU.getPlayerModels();
	}
	
    for(var id in playerModels)
    {
        var model_id = playerModels[id][0];
        var model_name = playerModels[id][1];
        var model_active = playerModels[id][2];
		var li_class = ( playerModels[id][3] ? "private" : "" );

        //console.log("Model "+model_id+": "+model_name+" "+(model_active?"ACTIVE":"INACTIVE"));

        // Setup urls
        PLAYER_MODELS[model_id] = {
            "model": model_name,
            "img": "img/mainmenu/players/"+model_id+".png",
            "img_thumb": "img/mainmenu/players/preview/"+model_id+".png"
        };

        target_element.append("<div id='"+model_id+"' class='container'><li class='"+li_class+"'><img><div>"+model_name.toUpperCase()+"</div></li></div>");
        setupPlayerCustomizeImages( model_id );

        if ( model_active ) active_model = model_id;
    }

    // Set up menu hover

    $("#player_customization #selection #options .container").hover(
        function () {
            $(this).addClass("hover_1");
            $(this).find("li").addClass("hover_2");
        },
        function () {
            $(this).removeClass("hover_1");
            $(this).find("li").removeClass("hover_2");
        }
    );

    $("#player_customization #selection #options .container").click(function() {
        selectPlayerModel($(this).attr('id'));
    });

    selectPlayerModel( active_model );
}

function setupPlayerCustomizeImages( model_id )
{
	var img_elem = $("#player_customization #selection #"+model_id+" li img");		
	img_elem.error(function() { 
		PLAYER_MODELS[model_id]["img_thumb"] = PLAYER_DEFAULTIMG_THUMB;
		PLAYER_MODELS[model_id]["img"] = PLAYER_DEFAULTIMG_BIG;
		
		$(this).attr('src', PLAYER_DEFAULTIMG_THUMB) 
	});
	img_elem.attr('src', PLAYER_MODELS[model_id]["img_thumb"]);
}

function selectPlayerModel( model_id )
{
    console.log("Selecting "+model_id);
    
	if ( CURRENT_PLAYER == model_id )
		return;
		
	if ( PLAYER_MODELS[model_id] == undefined )
	{
		console.log("selectPlayerModel - Unable to find model_id ("+model_id+")");
		return;
	}

	$.each(PLAYER_MODELS, function( index, value ) {
		var element = $('#player_customization #selection #options #'+index);
		
		element.removeClass("selected");
		element.find("li").removeClass("selected_2");		
	});
		
	if ( IS_ENGINE )
		MENU.selectPlayerModel(model_id);
	
	var button_element = $('#'+model_id);
	button_element.addClass("selected");
	button_element.find("li").addClass("selected_2");
	
	var elem = $("#player_customization #selection #preview");
		
	elem.fadeOut(250, function(){ 
		elem.css( {"background-image":"url("+PLAYER_MODELS[model_id]["img"]+")"} );
		elem.fadeIn(500);
	} );		
	
	CURRENT_PLAYER = model_id;
}

$(document).on('CEFReady', function() {

	$('#player_customization #selection #options').mCustomScrollbar({
		scrollInertia:0,
		scrollEasing:"easeOutCirc",
		advanced:{ updateOnContentResize: true }
	});

	// Set up model list etc...
	setupPlayerModels ();

	$("#buttons #back").click(function(){changePage(false)});
	
	// Skip intro 
	if ( !IS_ENGINE )
	{
		cycleMenuState();
		cycleMenuState();
	}
		
});