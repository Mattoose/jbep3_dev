"Resource/HudLayout.res"
{
	
	JBHud	
	{
		"fieldName"				"JBHud"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}
	
	JBSpec	
	{
		"fieldName"				"JBSpec"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}
	
	HudVoiceSelfStatus
	{
		"fieldName" "HudVoiceSelfStatus"
		"visible" "1"
		"enabled" "1"
		"xpos" "r43"
		"ypos" "355"
		"wide" "24"
		"tall" "24"
	}

	HudVoiceStatus
	{
		"fieldName" "HudVoiceStatus"
		"visible" "1"
		"enabled" "1"
		"xpos" "r150"
		"ypos" "0"
		"wide" "100"
		"tall" "400"

		"item_tall"	"18"
		"item_wide"	"100"

		"item_spacing" "1"

		"icon_ypos"	"0"
		"icon_xpos"	"0"
		"icon_tall"	"18"
		"icon_wide"	"18"

		"text_xpos"	"5"

		"PaintBackgroundType" "3"
	}
		
	JBHudAnnouncer	
	{
		"fieldName"				"JBHudAnnouncer"
	}
		
	HudObjectives
	{
		"fieldName" "HudObjectives"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}
	
	HudPings
	{
		"fieldName" "HudPings"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}	
	
	HudHealthMGS
	{
		//"fieldName"		"HudHealthMGS"
		"xpos"	"10"
		"ypos"	"20"
		"wide"	"640"
		"tall"  	"480"
		"visible" "1"
		"enabled" "1"
		"BarScale"	"1.0"

	}
	
	VotingMenu
	{
		"fieldName"		"VotingMenu"
		//"xpos"	"350"
		//"ypos"	"0"
		//"wide"	"250"
		//"tall"  	"350"
		"xpox"		"0"
		"ypos"		"0"
		"wide"		"210"
		"tall"		"480"
		"visible" "1"
		"enabled" "1"	

		BackgroundWidth		200
	}
	
	Radar
	{
		"fieldName"		"Radar"
		"xpos"	"r260"
		"ypos"	"10"
		"wide"	"250"
		"tall"  	"150"
		//"xpos"	"0"
		//"ypos"	"0"
		//"wide"	"f0"
		//"tall"  	"480"
		"visible" "1"
		"enabled" "1"
		
		"PlayerViewconeDistanceStart"	"80"
		"PlayerViewconeDistance"		"380"
		"PlayerViewconeDuration"		"1.9"
		"PlayerIconSize"				"4"
		"PlayerViewconeDrawSelf"		"0"
		"PlayerViewconeColor"			"0 255 0"
		"PlayerViewconeAngle"			"90"
		
		"VisibleOutlineAlpha"		"255"
		"VisibleOutlineAlphaFaded"	"150"
		"VisibleOutlineColor"		"245 200 71"
		
		"VisibleBackgroundColor"	"81 46 6 80"
		
		"BackgroundColor"			"124 92 49 200"
		
		"AutoZoomBorder"			"250"
		
	}
	
	RoundIntro	
	{
		"fieldName"				"RoundIntro"
		
		"MainStart"				"0.35"
		"MainHeight"				"45"
		
		"BorderHeight"			"2"
		
		"TitleFont"				"HudRoundIntroTitle"
		
		"SubTitleFont"			"HudRoundIntroSubTitle"
		
		"ImageHeight"			"180"
	}
	
	JBHudScope	
	{
		"fieldName"				"JBHudScope"
	}
	
	JBHudHitsounds	
	{
		"fieldName"				"JBHudHitsounds"
	}
	
	JBHudTimeLeft
	{
		"fieldName"		"JBHudTimeLeft"
		
		"wide"	 "f0"
		"tall"	 "480"
		
		"visible" "1"
		"enabled" "1"
		
		"TextFont"		"Trebuchet24"
		"YPadding"	"0"
		
	}
	
	HudHealth
	{
		"fieldName"		"HudHealth"
		"xpos"	"10"
		"ypos"	"r50"
		"wide"	"250"
		"tall"  	"40"
		"visible" "1"
		"enabled" "1"

		HealthIconX	5
		HealthIconW	90
		HealthIconH	90
		
		PaddingIconToText 		10
		PaddingText 			0
		
		HealthNumbersX		100
		HealthNumbersHeight 	80
	}
	
	overview
	{
		"fieldname"				"overview"
		"visible"				"1"
		"enabled"				"1"
		"xpos"					"0"
		"ypos"					"480"
		"wide"					"0"
		"tall"					"0"
	}
	
	TargetID
	{
		"fieldName" "TargetID"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}

	HudSuit
	{
		"fieldName"		"HudSuit"
		"xpos"	"130"
		"ypos"	"r50"
		"wide"	"250"
		"tall"  	"40"
		"visible" "1"
		"enabled" "1"

		HealthIconX	5
		HealthIconW	90
		HealthIconH	90
		
		PaddingIconToText 		10
		PaddingText 			0
		
		HealthNumbersX		100
		HealthNumbersHeight 	80
	}

	HudAmmo
	{
		"fieldName" "HudAmmo"
		"xpos"	"r120"
		"ypos"	"r50"
		"wide"	"120"
		"tall"  "40"
		"visible" "1"
		"enabled" "1"

		"PaintBackgroundType"	"2"

		"text_xpos" "8"
		"text_ypos" "20"
		"digit_xpos" "44"
		"digit_ypos" "2"
		"digit2_xpos" "98"
		"digit2_ypos" "16"
		
		"PaddingBetweenAmmos"	"20"
		"Ammo2Scale"	"1.35"
	}

	HudAmmoSecondary
	{
		"fieldName" "HudAmmoSecondary"
		"xpos"	"r60"
		"ypos"	"r90"
		"wide"	"60"
		"tall"  "40"
		"visible" "1"
		"enabled" "1"
	}
	
	HudSuitPower
	{
		"fieldName" "HudSuitPower"
		"visible" "1"
		"enabled" "1"
		"xpos"	"16"
		"ypos"	"396"
		"wide"	"102"
		"tall"	"26"
		
		"AuxPowerLowColor" "255 0 0 220"
		"AuxPowerHighColor" "255 220 0 220"
		"AuxPowerDisabledAlpha" "70"

		"BarInsetX" "8"
		"BarInsetY" "15"
		"BarWidth" "92"
		"BarHeight" "4"
		"BarChunkWidth" "6"
		"BarChunkGap" "3"

		"text_xpos" "8"
		"text_ypos" "4"
		"text2_xpos" "8"
		"text2_ypos" "22"
		"text2_gap" "10"

		"PaintBackgroundType"	"2"
	}

	HudPosture
	{
		"fieldName" 		"HudPosture"
		"visible" 		"1"
		"PaintBackgroundType"	"2"
		"xpos"	"16"
		"ypos"	"316"
		"tall"  "36"
		"wide"	"36"
		"font"	"WeaponIconsSmall"
		"icon_xpos"	"10"
		"icon_ypos" 	"0"
	}
	
	HudFlashlight
	{
		"fieldName" "HudFlashlight"
		"visible" "1"
		"PaintBackgroundType"	"2"
		"xpos"	"270"		[$WIN32]
		"ypos"	"444"		[$WIN32]
		"xpos_hidef"	"293"		[$X360]		// aligned to left
		"xpos_lodef"	"c-18"		[$X360]		// centered in screen
		"ypos"	"428"		[$X360]				
		"tall"  "24"
		"wide"	"36"
		"font"	"WeaponIconsSmall"
		
		"icon_xpos"	"4"
		"icon_ypos" "-8"
		
		"BarInsetX" "4"
		"BarInsetY" "18"
		"BarWidth" "28"
		"BarHeight" "2"
		"BarChunkWidth" "2"
		"BarChunkGap" "1"
	}
	
	HudDamageIndicator
	{
		"fieldName" "HudDamageIndicator"
		"visible" "1"
		"enabled" "1"
		"DmgColorLeft" "255 0 0 0"
		"DmgColorRight" "255 0 0 0"
		
		"dmg_xpos" "30"
		"dmg_ypos" "100"
		"dmg_wide" "36"
		"dmg_tall1" "240"
		"dmg_tall2" "200"
	}

	HudZoom
	{
		"fieldName" "HudZoom"
		"visible" "1"
		"enabled" "1"
		"Circle1Radius" "66"
		"Circle2Radius"	"74"
		"DashGap"	"16"
		"DashHeight" "4"	[$WIN32]
		"DashHeight" "6"	[$X360]		
		"BorderThickness" "88"
	}
	HudWeaponSelection
	{
		"fieldName" "HudWeaponSelection"
		"ypos" 	"8"	[$WIN32]
		"visible" "1"
		"enabled" "1"
		
		"CategoryFont"	"Trebuchet24"
		"CategoryColor"	"255 170 0 220"
		"CategoryOffsetX"	"0"
		"CategoryOffsetY"	"0"
		
		"CategorySelectionColor"	"255 170 0 255"
		"CategorySelectionColor2"	"81 46 6 255"
		"CategorySelectionBorder"	"2"
		"CategoryFadeBias"	"0.7"
		"CategoryFadeMinimum"	"0"
		"CategoryInactiveRowTotalBoxes"	"5" // How many boxes should we display MAX in inactive rows
		"CategoryInactiveRowFadeMinimum"	"0.25"
		
		"BoxOffsetX"			"25"
		"BoxOffsetY"			"15"
		
		"BoxWidth"			"85"
		"BoxHeight"			"30"
		"BoxAlpha"			"185"
		"BoxAlphaNoAmmo"			"50"
		"BoxColor"			"124 92 49 255"
		"BoxColorNoAmmo"		"124 92 49 255"
		//"BoxColorNoAmmo"		"255 0 0 255"
		
		"BoxWidthPadding"			"4"
		"BoxHeightPadding"		"4"
		
		"BoxBottomHeight"		"15"
		"BoxBottomPadding"	"2"
		"BoxBottomColor"		"81 46 6 255"
		"BoxBottomAlphaBias"	"0.75"
		
		"BoxRightWidth"		"10"
		"BoxRightPadding"		"2"
		"BoxRightColor"		"245 200 71 255"
		"BoxRightColorNoAmmo"		"245 200 71 255"
		//"BoxRightColorNoAmmo"		"224 54 54 255"
		
		"WeaponNameOffsetY"	"0"
		
		"BoxTextAlphaBias"	"0.8"
		
		"BoxNotInSelectionScale"	"1.35" // Scale of the box when we're not selecting
		"BoxInSelectionScale"	"1.0" // And the scale of the boxes when we're selecting
		
		"BoxIconAlphaBias"	"0.8"
		"BoxIconScale"		"0.95"
		"BoxIconScaleSelection"	"1.0"
		"BoxIconAlpha"		"240"
		"BoxIconAlphaNoAmmo"	"50"
				
		"AmmoFont"				"HudWepSelectAmmoBig"
		"AmmoFontSelection"		"HudWepSelectAmmoSmall"
		"AmmoColor"				"245 200 71 255"
		"AmmoOffsetX"				"-2"
		
		"TextFont"				"HudWepSelectName"
	}

	HudCrosshair
	{
		"fieldName" "HudCrosshair"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}

	HudDeathNotice
	{
		"fieldName" "HudDeathNotice"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "800"
		"LineHeight" "15"
		"HeightPadding" "2"
		"LineSpacing"	"1"
		"MaxDeathNotices"	"6"
		"CornerRadius"		"2"
		"IconWidthPadding"	"5"
	}

	HudVehicle
	{
		"fieldName" "HudVehicle"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}

	Scores
	{
		"fieldName" "Scores"
		"visible" "1"
		"enabled" "1"
		//"wide"	 "400"
		"tall"	 "480"
		
		//"avatar_width"	"80"
		//"name_width"		"136"
		//"class_width"		"35"
		//"score_width"		"35"
		//"death_width"		"35"
		//"ping_width"		"23"
	}

	HudTrain
	{
		"fieldName" "HudTrain"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}

	HudMOTD
	{
		"fieldName" "HudMOTD"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}

	HudMessage
	{
		"fieldName" "HudMessage"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}
	
	HudGameMessage
	{
		"fieldName" "HudGameMessage"
		"visible" "0"
		"enabled" "0"
		"xpos"	 "10"
		"ypos"	 "152"
		"wide"	 "f0"
		"tall"	 "256"
	}
	HudMenu
	{
		"fieldName" "HudMenu"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}

	HudCloseCaption
	{
		"fieldName" "HudCloseCaption"
		"visible"	"1"
		"enabled"	"1"
		"xpos"		"c-250"
		"ypos"		"276"	[$WIN32]
		"ypos"		"236"	[$X360]
		"wide"		"500"
		"tall"		"136"	[$WIN32]
		"tall"		"176"	[$X360]

		"BgAlpha"	"128"

		"GrowTime"		"0.25"
		"ItemHiddenTime"	"0.2"  // Nearly same as grow time so that the item doesn't start to show until growth is finished
		"ItemFadeInTime"	"0.15"	// Once ItemHiddenTime is finished, takes this much longer to fade in
		"ItemFadeOutTime"	"0.3"
		"topoffset"		"0"		[$WIN32]
		"topoffset"		"0"	[$X360]
	}

	HudChat
	{
		"fieldName" "HudChat"
		"visible" "1"
		"enabled" "1"
		"xpos"	"10"
		"ypos"	"300"
		"wide"	 "400"
		"tall"	 "100"
	}

	HudHistoryResource
	{
		"fieldName" "HudHistoryResource"
		"visible" "1"
		"enabled" "1"
		"xpos"	"r252"
		"ypos"	"40"
		"wide"	 "248"
		"tall"	 "320"

		"history_gap"	"56"
		"icon_inset"	"38"
		"text_inset"	"36"
		"text_inset"	"26"
		"NumberFont"	"HudNumbersSmall"
	}

	HudGeiger
	{
		"fieldName" "HudGeiger"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}

	HUDQuickInfo
	{
		"fieldName" "HUDQuickInfo"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}

	HudWeapon
	{
		"fieldName" "HudWeapon"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
	}
	
	HudAnimationInfo
	{
		"fieldName" "HudAnimationInfo"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "480"
		"LabelFont"	"WeaponIconsSmall"
		"ItemFont"	"WeaponIconsSmall"
		
	}

	HudPredictionDump
	{
		"fieldName" "HudPredictionDump"
		"visible" "1"
		"enabled" "1"
		"wide"	 "f0"
		"tall"	 "f0"
	}

	HudHintDisplay
	{
		"fieldName"				"HudHintDisplay"
		"visible"				"0"
		"enabled"				"1"
		"xpos"					"c-240"
		"ypos"					"c60"
		"xpos"	"r148"	[$X360]
		"ypos"	"r338"	[$X360]
		"wide"					"480"
		"tall"					"100"
		"HintSize"				"1"
		"text_xpos"				"8"
		"text_ypos"				"8"
		"center_x"				"0"	// center text horizontally
		"center_y"				"-1"	// align text on the bottom
		"paintbackground"		"0"
	}	

	HudHintKeyDisplay
	{
		"fieldName"	"HudHintKeyDisplay"
		"visible"	"0"
		"enabled" 	"1"
		"xpos"		"r120"	[$WIN32]
		"ypos"		"r340"	[$WIN32]
		"xpos"		"r148"	[$X360]
		"ypos"		"r338"	[$X360]
		"wide"		"100"
		"tall"		"200"
		"text_xpos"	"8"
		"text_ypos"	"8"
		"text_xgap"	"8"
		"text_ygap"	"8"
		"TextColor"	"255 170 0 220"

		"PaintBackgroundType"	"2"
	}

	HudSquadStatus
	{
		"fieldName"	"HudSquadStatus"
		"visible"	"1"
		"enabled" "1"
		"xpos"	"r120"
		"ypos"	"380"
		"wide"	"104"
		"tall"	"46"
		"text_xpos"	"8"
		"text_ypos"	"34"
		"SquadIconColor"	"255 220 0 160"
		"IconInsetX"	"8"
		"IconInsetY"	"0"
		"IconGap"		"24"

		"PaintBackgroundType"	"2"
	}

	HudPoisonDamageIndicator
	{
		"fieldName"	"HudPoisonDamageIndicator"
		"visible"	"0"
		"enabled" "1"
		"xpos"	"16"
		"ypos"	"346"
		"wide"	"136"
		"tall"	"38"
		"text_xpos"	"8"
		"text_ypos"	"8"
		"text_ygap" "14"
		"TextColor"	"255 170 0 220"
		"PaintBackgroundType"	"2"
	}
	HudCredits
	{
		"fieldName"	"HudCredits"
		"TextFont"	"Default"
		"visible"	"1"
		"xpos"	"0"
		"ypos"	"0"
		"wide"	"f0"
		"tall"	"480"
		"TextColor"	"255 255 255 192"

	}
	
	HUDAutoAim
	{
		"fieldName" "HUDAutoAim"
		"visible" "1"
		"enabled" "1"
		"wide"	 "640"	[$WIN32]
		"tall"	 "480"	[$WIN32]
		"wide"	 "960"	[$X360]
		"tall"	 "720"	[$X360]
	}
	HudCommentary
	{
		"fieldName" "HudCommentary"
		"xpos"	"c-190"
		"ypos"	"350"
		"wide"	"380"
		"tall"  "40"
		"visible" "1"
		"enabled" "1"
		
		"PaintBackgroundType"	"2"
		
		"bar_xpos"		"50"
		"bar_ypos"		"20"
		"bar_height"	"8"
		"bar_width"		"320"
		"speaker_xpos"	"50"
		"speaker_ypos"	"8"
		"count_xpos_from_right"	"10"	// Counts from the right side
		"count_ypos"	"8"
		
		"icon_texture"	"vgui/hud/icon_commentary"
		"icon_xpos"		"0"
		"icon_ypos"		"0"		
		"icon_width"	"40"
		"icon_height"	"40"
	}
	
	HudHDRDemo
	{
		"fieldName" "HudHDRDemo"
		"xpos"	"0"
		"ypos"	"0"
		"wide"	"f0"
		"tall"  "480"
		"visible" "1"
		"enabled" "1"
		
		"Alpha"	"255"
		"PaintBackgroundType"	"2"
		
		"BorderColor"	"0 0 0 255"
		"BorderLeft"	"16"
		"BorderRight"	"16"
		"BorderTop"		"16"
		"BorderBottom"	"64"
		"BorderCenter"	"0"
		
		"TextColor"		"255 255 255 255"
		"LeftTitleY"	"422"
		"RightTitleY"	"422"
	}

	AchievementNotificationPanel	
	{
		"fieldName"				"AchievementNotificationPanel"
		"visible"				"1"
		"enabled"				"1"
		"xpos"					"0"
		"ypos"					"180"
		"wide"					"f10"	[$WIN32]
		"wide"					"f60"	[$X360]
		"tall"					"100"
	}

	
}