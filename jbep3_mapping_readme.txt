You can find the .fgd in this same folder.

FAQ:

Q: What are the player bounds?
A: 	Standing: 	Width 32 	Height 72	Eye Height 58
	Ducking: 	Width 32	Height 36	Eye Height 28
	Prone:		Width 32	Height 22	Eye Height 10
	
Q: What spawns should I use?
SVT: jb_spawn_svt_snake + jb_spawn_svt_terrorist
DM: jb_spawn_all
TDM: jb_spawn_deathmatch_red jb_spawn_deathmatch_blue
Everything else: jb_spawn_all

Q: How do I use custom SvT round music/set terrorist skins?
A: jb_gamerules entity - has outputs for various round events and KV for terrorist skin.

Q: How do I do the ricochet style jump pads?
A: jb_trigger_jump, targeting an info_target. Raising the apex value will increase the arc.
	
Need help with anything not listed? Email jimbomcb@gmail.com