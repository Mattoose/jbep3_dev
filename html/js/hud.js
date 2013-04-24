var IS_GAME = ( navigator.userAgent == "JaykinBacon" );

var number_offsets = [];
number_offsets[0] = [5,0,56,100]; // x, y, w, h
number_offsets[1] = [80,0,34,100];
number_offsets[2] = [139,0,55,100]; 
number_offsets[3] = [203,0,58,100]; 
number_offsets[4] = [270,0,58,100]; 
number_offsets[5] = [337,0,59,100]; 
number_offsets[6] = [404,0,58,100]; 
number_offsets[7] = [474,0,57,100]; 
number_offsets[8] = [537,0,57,100]; 
number_offsets[9] = [604,0,57,100]; 		

var prev_hp = 100;
function setHealth( health )
{			
	var bar_pct = Math.max( 0, Math.min( 100, health ) );
	
	for ( var i = 0; i < 3; i++ )
	{
		var digit = (health+'')[i];
		var elem = $("#health #digit_"+(i+1));
		
		if ( digit == undefined )
		{
			elem.hide();
			continue;
		}
						
		var offset = number_offsets[digit];
		
		elem.css( { 
			'background-position' : -(offset[0])+'px',
			'width' : offset[2]+'px',
		} );
		
		elem.show();
	}		
	
	$("#mgshealth #bar").css({'width':bar_pct+'%'});	
	
	if ( prev_hp > health ) // If we lost health, do our animation 
	{
		$("#mgshealth #bar_red").animate({'width':bar_pct+'%'}, { duration: 500, easing: "easeInQuart", queue: false } );	
	}
	else
	{
		$("#mgshealth #bar_red").css({'width':bar_pct+'%'});		
	}
		
	prev_hp = health;	
}

function setArmour( armour )
{			
	if ( armour > 0 )
		$("#armour").show();
	else
		$("#armour").fadeOut( { duration: 500, queue: false } );
		
	for ( var i = 0; i < 3; i++ )
	{
		var digit = (armour+'')[i];
		var elem = $("#armour #digit_"+(i+1));
		
		if ( digit == undefined )
		{
			elem.hide();
			continue;
		}
						
		var offset = number_offsets[digit];
		
		elem.css( { 
			'background-position' : -offset[0]+'px',
			'width' : offset[2]+'px',
		} );
		
		elem.show();
	}
}

function updateScale()
{
	var w = Math.min(1, $(window).width()/1280);
	window.document.body.style.setProperty('zoom', w, 'important')	
}

$( function(){ 
	updateScale();
	setHealth( 100 );
	setArmour( 0 );
} );

$(window).resize(updateScale);

if ( !IS_GAME )
{
	var hp = 0;
	function loop(){
		var randomnumber=Math.floor(Math.random()*101);
		setHealth(randomnumber);
		var randomnumber2 = Math.floor(Math.random()*20);
		setArmour(randomnumber2);
		
		//setHealth(hp);
		hp++;
		if ( hp > 100 )
			hp = 0;
		
		setTimeout(loop,650);
	}

	loop();
}