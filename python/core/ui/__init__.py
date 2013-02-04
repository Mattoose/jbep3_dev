from core.usermessages import usermessage

if isclient:
    from scorescreen import scorescreeninst
    from winlosedialog import WinLoseDialog
    from resourcesdialog import resourcesdialoginst
    
# User messages 
@usermessage('showscorescreen')
def ShowScoreScreen(location, *args, **kwargs):
    pass #scorescreeninst.ShowScores(location)
    
@usermessage('showwinlosedialog')
def ShowWinLoseDialog(winners, losers, iswinner, *args, **kwargs):
    WinLoseDialog(winners, losers, iswinner)
    