"""
Shared between ui and manager
"""
from srcbase import *

# Settings
MAXPLAYERS = 8          # Max number of players to show in the gamelobby
INVALID_POSITION = MAXPLAYERS

# Message types to the gamelobby loading panel
GLLP_PLAYERSTATUSUPDATE = 0
GLLP_SETSTATUS_WFP = 1  # Waiting for players
GLLP_SETSTATUS_CD = 2   # Count down

# Gamelobby slots types
GLTYPE_OPEN = 0
GLTYPE_CLOSED = 1
GLTYPE_NOTAVAILABLE = 2
GLTYPE_HUMAN = 3
GLTYPE_CPU = 4

# Teams
TEAM_UNASSIGNED = 0
TEAM_SPECTATOR = 1
TEAM_ONE = 2
TEAM_TWO = 3
TEAM_THREE = 4
TEAM_FOUR = 5

# Map teams
GL_TEAMSTEXT = {
    TEAM_UNASSIGNED : '-',
    TEAM_SPECTATOR : 'Spec',
    TEAM_ONE : '1',
    TEAM_TWO : '2',
    TEAM_THREE : '3',
    TEAM_FOUR : '4',
}

# Use a fixed set of colors
GL_COLORS = {
    'GRCOLOR_ORANGE' : Color(200, 120, 20, 255),
    'GRCOLOR_BLUE' : Color( 20, 100, 200, 255),
    'GRCOLOR_CYAN' : Color( 0, 255, 255, 255),
    'GRCOLOR_GREEN': Color( 0, 255, 0, 255),
    'GRCOLOR_RED' : Color( 255, 0, 0, 255),
    'GRCOLOR_GOLD' : Color( 204, 153, 51, 255),
    'GRCOLOR_TWILIGHT_BLUE': Color( 102, 102, 204, 255),
    'GRCOLOR_VIOLET': Color( 204, 102, 204, 255),
}

