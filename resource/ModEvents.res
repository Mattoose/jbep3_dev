// No spaces in event names, max length 32
// All strings are case sensitive
//
// valid data key types are:
//   string : a zero terminated string
//   bool   : unsigned int, 1 bit
//   byte   : unsigned int, 8 bit
//   short  : signed int, 16 bit
//   long   : signed int, 32 bit
//   float  : float, 32 bit
//   local  : any data, but not networked to clients
//
// following key names are reserved:
//   local      : if set to 1, event is not networked to clients
//   unreliable : networked, but unreliable
//   suppress   : never fire this event
//   time	: firing server time
//   eventid	: holds the event ID

"sdkevents"
{
	"player_death"
	{
		"userid"	"short"   	// user ID who died				
		"attacker"	"short"	 	// user ID who killed
		"weapon"	"string" 	// weapon name killed used
		"weaponid"	"short" 	// weapon id being used
		"customkill" "short"	//flags for custom kills
		"damagebits" "long"		//Some bits or something idk
		"bodygroup" "short"	//flags for custom kills
		"npc_killer" "short"	
		"npc_name"	 "string"   
	}
	
	"player_team"				// player change his team
	{
		"userid"	"short"		// user ID on server
		"team"		"byte"		// team id
		"oldteam" "byte"		// old team id
		"disconnect" "bool"	// team change because player disconnects
		"silent" "bool"
		"autobalance"	"bool"
		"name"	"string"
	}
	
	"player_hurt"
	{
		"userid"	"short"   	// user ID who was hurt			
		"attacker"	"short"	 	// user ID who attacked
		"weapon"	"string" 	// weapon name attacker used
	}
	
	"player_changeclass"
	{
		"userid"	"short"		// user ID who changed class
		"class"		"short"		// class that they changed to
	}

	"spec_target_updated"
	{
	}
	
	"npc_death" //deprecated
	{
		"name"				"string" 	// name of the killed NPC
		"attacker"			"short"	
		"attacker_name"		"string"   	// user ID who killed the npc
		"weapon_name"		"string"   	// weapon used to kill (if it was a player)
	}
	
	"entity_visible"
	{
		"userid"		"short"		// The player who sees the entity
		"subject"		"short"		// Entindex of the entity they see
		"classname"		"string"	// Classname of the entity they see
		"entityname"	"string"	// name of the entity they see
	}
	
	//"killstreak"
	//{
	//	"userid"			"short"		// Who
	//	"kills"				"short"		// and how many.
	//}
	
	"intermission" // Scoreboard opens, waits x seconds (mp_chattime) and changes to nextlevel.
	{
	}
	
	"jb_broadcast_sound" // audio broadcast, plays locally on given team (OR EVERYONE IF TEAM = 0)
	{
		"team"			"short"
		"sound"			"string"
		"music"			"bool"
	}
	
	//"jb_stop_sounds" // temp fix to stop any remaining looping sound bugs on some round reloads, going to be properly fixed soon
	//{
	//}
	
	"jb_force_scoreboard_update"
	{
	}
	
	//"jb_start_roundintro"
	//{
	//}
	
	"jb_round_cleanup"
	{
	}
	
	"vote_map_transmit"
	{
		"map"		"string"
	}
	
	//
	// CLIENT EVENTS
	//
	
	"jb_ping_update" 	// Called when there's a new ping entity we should take notice of.
	{
		"entity"			"short" // Ent index of the ping ent
		"active"			"bool"
	}
	
	
	"jb_timer_update" // Signals that the timer has been updated and the client should handle it.
	{
		"entity"			"short"
	}
	
	"game_newmap"				// send when new map is completely loaded
	{
		"mapname"	"string"	// map name
	}
	
	"hud_headshot"				// When either the local player was involved in a headshot for hud display
	{
		"victim"	"bool"		// Will be true if we were the victim, otherwise we were the source.
	}
	
	"jb_radar_sensor_update"
	{
		"creation"		"bool"
		"entity"			"short"
	}
	
	"jb_new_objective"
	{
		"entid"			"short"
		"type"			"string"
	}
	
	//
	// Instructor Events
	//
	
	// SERVER
	"explain_frog"
	{
		"entid"			"short"
	}
	
	"pickup_visible"
	{
		"userid"			"short"
		"type"			"short"
	}
	
	"pickup_visible"
	{
		"userid"			"short"
		"subject"		"short"
		"type"			"short"
	}
	
	"pickup_pickedup"
	{
		"userid"			"short"
		"pickup"			"short"
	}
	
	// CLIENT
	"weapon_deploy"
	{
		"weapon"			"string"
	}
	
	"weapon_box_invisible"
	{
		"is_invisible"	"bool"
		"is_crouched"		"bool"
	}
	
	"position_state_update" // Changed between standing, ducking and crouching.
	{
		"state"			"short" // 0 = standing, 1 = ducking, 2 = diving
	}
	
	"weapon_fired" // We fired our weapon
	{
		"secondary"		"bool" // True if it was our secondary attack
	}
	
	"rcrowbar_impacted" // We hit something with our rocket crowbar
	{
		"wasplayer"		"bool"
	}
	
}
