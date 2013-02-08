var IS_ENGINE = ( navigator.userAgent == "JaykinBacon" );
var IN_GAME = false;

// States
var STATE_VIDEO = 0;
var STATE_SPLASH = 1;
var STATE_MENU = 2;		
var CURRENT_STATE = -1;
		
// Auto scaling...
function updateScale()
{			
	// Resize if we get small
	var w = Math.min(1, $(window).width()/1280);
	window.document.body.style.setProperty('zoom', w, 'important')	
}

$( function(){ 
	updateScale();
	//$("#links").css("margin-top",-($("#links").height()*0.3)+"px");
} );

$(window).resize(updateScale);

// Mouse click stuff
function cycleState()
{
	setState( CURRENT_STATE + 1 );
}

function setState( state )
{
	state = Math.min(2,state);
	
	if ( state == CURRENT_STATE )
		return;
	
	console.log("Setting state to "+state);
	CURRENT_STATE = state;
	
	switch( CURRENT_STATE )
	{
		case STATE_VIDEO:
			switchToIntroVideo();
			break;
		case STATE_SPLASH:
			switchToSplash();
			break;
		case STATE_MENU:
			switchToMenu();
			break;
	}	
}
	
$(document).click( cycleState );

$( function(){
	setState( IS_ENGINE ? STATE_VIDEO : STATE_MENU ); // If engine, show the video otherwise just skip to menu
});

/*
 INTRO VIDEO
*/
function switchToIntroVideo()
{
	switchFromSplash();
	switchFromMenu();
	
	$("#video").show();	
	
	$('#video video').bind("ended", cycleState); // Cycle to next state when we end
	var introVideo = $('#video video').get(0);
	introVideo.volume = 0.25;
	introVideo.play();		
}	   
			
function switchFromIntroVideo()
{
	if ( IS_ENGINE && !IN_GAME )
		MENU.playMenuMusic();
	
	var introVideo = $('#video video').get(0);			
	introVideo.pause();
	$("#video").hide();
}

/*
 SPLASH
*/

function switchToSplash()
{
	switchFromIntroVideo();
	switchFromMenu();
	
	$("#splash").show();
	$("#splash #background div").delay(500).animate( { "opacity":"0.35" }, 2500 );
	$("#splash #logo").delay(1500).animate( { "opacity":"1" }, 4500 );
	splashBackgroundScroll();
}

function switchFromSplash()
{
	$("#splash").hide();
}

var dir_1 = [ (Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1 ];		
var pos_1 = [500,500,0,250];

function splashBackgroundScroll()
{
	$( "#splash #background #layer_1" ).css("background-position",pos_1[0]+"px "+pos_1[1]+"px");
	$( "#splash #background #layer_2" ).css("background-position",pos_1[2]+"px "+pos_1[3]+"px");
	
	pos_1[0] += dir_1[0];
	pos_1[1] += dir_1[1];
	pos_1[2] += dir_1[2];
	pos_1[3] += dir_1[3];
	
	if ( CURRENT_STATE == STATE_SPLASH )
		setTimeout(splashBackgroundScroll, 10);
}		

/*
 MENU
*/

function switchToMenu()
{
	switchFromIntroVideo();
	switchFromSplash();
	
	$("#menu").delay(800).fadeIn(1000);		
	
	if ( IS_ENGINE )
		MENU.playSound("gunshot");
}

function switchFromMenu()
{
	$("#menu").hide();
}

var CURRENT_PAGE = false;
var PAGE_FRONT = false;
var PAGE_CUSTOMISATION = "player_customization";
var PAGE_FINDSERVER = "findserver";
var PAGE_DONATE = "donate";

function changePage( desired_page )
{
	console.log("Trying to change page",desired_page);
	if ( desired_page == CURRENT_PAGE ) 
		return;
		
	if ( desired_page != PAGE_FRONT && CURRENT_PAGE != PAGE_FRONT ) // If we're not on front page and want to change to a different non-front page, stop.
		return;
		
	if ( desired_page != PAGE_FRONT ) 
	{
		$("#menu #links").animate({"width":"0px"},500);
		$("#menu #"+desired_page).animate({"left":"6%"},500);		
	}
	else
	{
		$("#menu #"+CURRENT_PAGE).animate({"left":"106%"},500);	
		$("#menu #links").animate({"width":"90%"},500);	
	}
	
	//$("#menu #links").animate({"width":"0px"},500);
	//$("#menu #player_customization").animate({"left":"6%"},500);
		
	CURRENT_PAGE = desired_page;
}

var menu_options = {
	// Button ID, Button Text, Button Desc, Display in menu, Display in game, Handled in webpage, func on open
	"resume" : [ "RESUME GAME", "Return to the current game.", false, true, false ], // Button text, button desc, display in game.
	"disconnect":[ "DISCONNECT", "Disconnect from the current game.", false, true, false ],
	"playerlist":[ "PLAYER LIST", "Other players in the current game.", false, true, false ],
	"findserver_new":[ "FIND SERVERS", "Find a server.", true, true, PAGE_FINDSERVER, findServerTabOpen ],
	"findservers":[ "FIND SERVERS (CLASSIC)", "Find servers.", true, false, false ],
	"createserver":[ "CREATE SERVER", "Create a local or internet server.", true, false, false ],
	"customizeplayer":[ "CUSTOMIZE PLAYER", "Change your player model.", true, true, PAGE_CUSTOMISATION ],
	"options":[ "OPTIONS", "Change game options.", true, true, false ],
	"donate":[ "DONATE", "Support our mod.", true, true, PAGE_DONATE ],
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
		$("#menu #background #bg_img").fadeOut(2000);
	}
	else
	{				
		$("#menu #background #bg_img").fadeIn(2000, function(){$("body").css("background-color","black");});
	}
}

$(updateMenu); // Run on load

// Menu links
function menuClick( button_div )
{
	var pressed = $(button_div).attr('id');
	var button_data = menu_options[pressed];
	console.log("Button press: "+pressed,button_data);
	
	if ( button_data[4] != false ) // Handled by page
	{
		changePage( button_data[4] );
	}
	else
	{
		if ( IS_ENGINE )
			MENU.buttonPress(pressed);
	}
	
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
	var target_element = $('#player_customization #selection #options .mCSB_container');
	var objs;
	
	if ( IS_ENGINE )
	{
		objs = MENU.getPlayerModels()
	}
	else
	{
		objs = [ ["postal", "Test Model"], 
		["adamjensen", "Test Model 2"],
		["alien", "These"],
		["allied", "Are"],
		["ash", "Populated"],
		["6", "By"],
		["7", "The"],
		["8", "Engine"],
		["10", "Test Model"], 
		["20", "Test Model 2"],
		["30", "These"],
		["40", "Are"],
		["50", "Populated"],
		["60", "By"],
		["70", "The"],
		["80", "Engine"],
		["100", "Test Model"], 
		["200", "Test Model 2"],
		["300", "These"],
		["400", "Are"],
		["500", "Populated"],
		["600", "By"],
		["700", "The"],
		["800", "Engine"]
		];
	}
		
	for ( var i = 0; i < objs.length; i++ )
	{
		var model_id = objs[i][0];
		var model_name = objs[i][1];
		
		// Setup urls
		PLAYER_MODELS[model_id] = {
			"model": model_name,
			"img": "img/mainmenu/players/"+model_id+".png",
			"img_thumb": "img/mainmenu/players/preview/"+model_id+".png" 
		};
		
		target_element.append("<div id='"+model_id+"' class='container'><li><img><div>"+model_name.toUpperCase()+"</div></li></div>");
		setupPlayerCustomizeImages( model_id );
	}
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

$( function() {

	$('#player_customization #selection #options').mCustomScrollbar({
		scrollInertia:0,
		scrollEasing:"easeOutCirc",
		advanced:{ updateOnContentResize: true }
	});
	
	// Set up model list etc...
	setupPlayerModels ();
	
	// Update our menu with selected model
	if ( IS_ENGINE ) 
	{
		var current_model = MENU.getPlayerCurrentModel();
		
		if ( PLAYER_MODELS[current_model] != undefined )
			selectPlayerModel( current_model );
	}
	else
	{
		for ( var pl in PLAYER_MODELS )
		{
			selectPlayerModel( pl );
			break;
		}
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
	
	$("#buttons #back").click(function(){changePage(false)});
		
});

/*
 ENGINE (functions called by engine)
*/

function updateGameState(state) // Called when we change from menu to ingame or vice versa
{
	IN_GAME = state;	
	
	updateMenu(); // Rebuild our menu options based on ingame status.
	
	if ( IN_GAME )
		setState(STATE_MENU); // Switch to menu straight away, skip any videos playing.
}

/* 

FIND SERVER 

*/
var findServerTabOpened = false;
var findServerHasScrollbar = false;
var findServers = [];
function findServerTabOpen()
{
	if (findServerTabOpened)
		return;
		
	findServerTabOpened = true;
	
	if ( IS_ENGINE )
		MENU.serverMasterRequest();
}

function serversServerResponded( server )
{
	/*
	args.Push( Awesomium::JSValue( Awesomium::WSLit( pServerItem->m_NetAdr.GetQueryAddressString() ) ) ); // IP
	args.Push( Awesomium::JSValue( Awesomium::WSLit( pServerItem->GetName() ) ) ); // NAME
	args.Push( Awesomium::JSValue( pServerItem->m_nPing ) ); // PING
	args.Push( Awesomium::JSValue( pServerItem->m_nPlayers ) ); // PLAYERS
	args.Push( Awesomium::JSValue( pServerItem->m_nMaxPlayers ) ); // PLAYERS
	args.Push( Awesomium::JSValue( Awesomium::WSLit( pServerItem->m_szMap ) ) ); // MAP
	args.Push( Awesomium::JSValue( Awesomium::WSLit( pServerItem->m_szGameDescription ) ) ); // GAME DESC
	*/
	
	//findServers.push( server );
	
	var truncated_name = server.name;
	if ( truncated_name.length > 32 )
		truncated_name = truncated_name.substring(0,29)+"...";
	
	//var serv_str = "<li class='server_row' id='server_"+server.id+"'>"+truncated_name+" ("+server.players+"/"+server.maxplayers+") - "+server.desc+"</li>";
	var serv_str = "<li class='server_row' id='server_"+server.id+"'>"+server.players+"/"+server.maxplayers+" - "+truncated_name+" - "+server.desc+"</li>";
	
	
	$("#findserver #selection").append(serv_str);
}

function serversRefreshComplete()
{
	/*$("#findserver #selection").mCustomScrollbar({
		scrollInertia:111,
		scrollEasing:"easeOutCirc",
		advanced:{ updateOnContentResize: true }
	});*/
}

	