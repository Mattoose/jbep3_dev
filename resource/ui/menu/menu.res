"Resource/UI/ScoreBoard.res"
{
	"JBNewMainMenu"
	{
		"xpos"			"0"
		"ypos"			"0"
		"wide"			"f"
		"tall"			"f"
		"visible"		"1"
		"enabled"		"1"
	}
	
	"HeaderImage"
	{	
		"ControlName"				"ImagePanel"
		"xpos"					"r250"
		"ypos"					"20"
		"wide"					"200"
		"tall"					"50"
		"visible"				"1"
		"enabled"				"1"
		"image"					"menu/bg_logo"
		"drawcolor"				"255 255 255 50"
		"scaleImage"				"1"
		"zpos"					"-1"
	}

	"BackgroundPanel"
	{	
		"ControlName"				"BackgroundPanel"
		"xpos"					"0"
		"ypos"					"0"
		"wide"					"f"
		"tall"					"f"
		"visible"				"1"
		"enabled"				"1"
		"zpos"					"-2"
	}
	
	"MenuContainer"
	{	
		"ControlName"				"MenuContainer"
		"xpos"					"40"
		"ypos"					"40"
		"wide"					"f80"
		"tall"					"400"
		"visible"				"1"
		"enabled"				"1"
		"SideBarwidth"			"3"
	
		"ButtonFindGame"
		{	
			"ControlName"				"MainMenuButton"
			"xpos"					"10"
			"ypos"					"20"
			"wide"					"f"
			"tall"					"30"
			"visible"				"1"
			"enabled"				"1"
			"font"					"Ray30"
			"labelText"				"#JB_Menu_FindServer"
			"command"				"OpenServerBrowser"
			"allcaps"				"1"
			"proportionalToParent"		"1"
			"textInsetX"				"50"
		}
		
		"ButtonCreateServer"
		{	
			"ControlName"				"MainMenuButton"
			"xpos"					"10"
			"ypos"					"50"
			"wide"					"f"
			"tall"					"30"
			"visible"				"1"
			"enabled"				"1"
			"font"					"Ray30"
			"labelText"				"#JB_Menu_CreateServer"
			"command"				"engine _jb_menu_createserver 1"
			"allcaps"				"1"
			"proportionalToParent"		"1"
			"textInsetX"				"50"
		}
		
		"ButtonCustomizePlayer"
		{	
			"ControlName"				"MainMenuButton"
			"xpos"					"10"
			"ypos"					"80"
			"wide"					"f"
			"tall"					"30"
			"visible"				"1"
			"enabled"				"1"
			"font"					"Ray30"
			"labelText"				"#JB_Menu_Customize"
			"command"				"CustomizePlayer"
			"allcaps"				"1"
			"proportionalToParent"		"1"
			"textInsetX"				"50"
		}
		
		"ButtonOptions"
		{	
			"ControlName"				"MainMenuButton"
			"xpos"					"10"
			"ypos"					"110"
			"wide"					"f"
			"tall"					"30"
			"visible"				"1"
			"enabled"				"1"
			"font"					"Ray30"
			"command"				"OpenOptionsDialog"
			"labelText"				"#JB_Menu_Options"
			"allcaps"				"1"
			"proportionalToParent"		"1"
			"textInsetX"				"50"
		}
		
		"ButtonDonate"
		{	
			"ControlName"				"MainMenuButton"
			"xpos"					"10"
			"ypos"					"140"
			"wide"					"f"
			"tall"					"30"
			"visible"				"1"
			"enabled"				"1"
			"font"					"Ray30"
			"labelText"				"#JB_Menu_Donate"
			"command"				"Donate"
			"allcaps"				"1"
			"proportionalToParent"		"1"
			"textInsetX"				"50"
		}
		
		"ButtonQuit"
		{	
			"ControlName"				"MainMenuButton"
			"xpos"					"10"
			"ypos"					"r50"
			"wide"					"f"
			"tall"					"30"
			"visible"				"1"
			"enabled"				"1"
			"font"					"Ray30"
			"labelText"				"#JB_Menu_Quit"
			"command"				"engine quit"
			"allcaps"				"1"
			"proportionalToParent"		"1"
			"textInsetX"				"50"
		}
	}
	
	"MenuContainerModels"
	{	
		"ControlName"				"MenuContainer"
		"xpos"					"r0"
		"ypos"					"40"
		"wide"					"f80"
		"tall"					"400"
		"visible"				"1"
		"enabled"				"1"
		"SideBarWidth"			"3"
		
		"Loading"
		{
			"ControlName"			"Label"
			"fieldName"				"Loading"
			"xpos"					"0"
			"ypos"					"0"
			"wide"					"f"
			"tall"					"350"
			
			"proportionalToParent"		"1"
			
			"font"					"Ray30"
			"labelText"				"#JB_Menu_Loading"
			"textAlignment"			"center"
			
		}
		
		"ModelPreview"
		{
			"ControlName"			"ImagePanel"
			"fieldName"				"ModelPreview"
			"xpos"					"0"
			"ypos"					"0"
			"wide"					"350"
			"tall"					"350"
		
			"visible"				"1"
			"enabled"				"1"
			"image"					"playerpreview/missing"
			"drawcolor"				"255 255 255 255"
			
		}
		
		
		"ModelListScroller"
		{
			"ControlName"			"ScrollableEditablePanel"
			"fieldName"				"ModelListScroller"
			"xpos"					"r360"
			"ypos"					"0"
			"wide"					"280"
			"tall"					"350"
			"PaintBackgroundType"		"2"
			//"bgcolor_override"		"255 0 0 255"
			
			"ModelList"
			{
				"ControlName"	"CButtonList"
				"fieldName"		"ModelList"
				"xpos"			"0"
				"ypos"			"0"
				"wide"			"f"
				"tall"			"f"
				"visible"		"1"
				//"PaintBackgroundType"		"2"
				//"bgcolor_override"			"255 0 0 10"
				"proportionalToParent"		"1"
			}
		}
		
		"ButtonBack"
		{	
			"ControlName"			"MainMenuButton"
			"xpos"					"10"
			"ypos"					"r50"
			"wide"					"f"
			"tall"					"30"
			"visible"				"1"
			"enabled"				"1"
			"font"					"Ray30"
			"labelText"				"#JB_Menu_Back"
			"command"				"ExitSubMenu"
			"allcaps"				"1"
			"proportionalToParent"		"1"
			"textInsetX"				"50"
		}
	}
}
