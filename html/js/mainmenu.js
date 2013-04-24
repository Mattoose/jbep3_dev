var IS_ENGINE = ( navigator.userAgent == "JaykinBacon" );
var IN_GAME = false;

// Auto scaling...
function updateScale()
{			
	// Resize if we get small
	var w = Math.min(1, $(window).width()/1280);
	window.document.body.style.setProperty('zoom', w, 'important')	
}

$( updateScale );
$(window).resize(updateScale);

$(document).on('CEFReady', function() {
    updateMenu();
    $("#menu").fadeIn(1000);
});

/*
 MENU
*/

var CURRENT_PAGE = false;
var PAGE_FRONT = false;
var PAGE_CUSTOMISATION = "player_customization";
var PAGE_FINDSERVER = "findserver";

function changePage( desired_page )
{
	console.log("Trying to change page",desired_page);
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
	
	//$("#menu #links").animate({"width":"0px"},500);
	//$("#menu #player_customization").animate({"left":"6%"},500);
		
	CURRENT_PAGE = desired_page;
}

var menu_options = {
	// Button ID, Button Text, Button Desc, Display in menu, Display in game, Handled in webpage, func on open
	"resume" : [ "RESUME GAME", "Return to the current game.", false, true, false ], // Button text, button desc, display in game.
	"disconnect":[ "DISCONNECT", "Disconnect from the current game.", false, true, false ],
	"playerlist":[ "PLAYER LIST", "Other players in the current game.", false, true, false ],
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
		$("#menu #background #bg_img").fadeOut(2000);
	}
	else
	{				
		$("#menu #background #bg_img").fadeIn(2000, function(){$("body").css("background-color","black");});
	}
}

// Menu links
function menuClick( button_div )
{
	var pressed = $(button_div).attr('id');
	var button_data = menu_options[pressed];
	console.log("Button press: "+pressed,button_data);
	
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
    var playerModels = MENU.getPlayerModels();
    var target_element = $('#player_customization #selection #options .mCSB_container');
    var active_model = CURRENT_PLAYER;

    /*var objs = [ ["postal", "Test Model"],
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
        ];*/

    for(var id in playerModels)
    {
        console.log(playerModels[id]);
        var model_id = playerModels[id][0];
        var model_name = playerModels[id][1];
        var model_active = playerModels[id][2];

        console.log("Model "+model_id+": "+model_name+" "+(model_active?"ACTIVE":"INACTIVE"));

        // Setup urls
        PLAYER_MODELS[model_id] = {
            "model": model_name,
            "img": "img/mainmenu/players/"+model_id+".png",
            "img_thumb": "img/mainmenu/players/preview/"+model_id+".png"
        };

        target_element.append("<div id='"+model_id+"' class='container'><li><img><div>"+model_name.toUpperCase()+"</div></li></div>");
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
		
});

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

	