from core.usermessages import usermessage

if isclient:
    from info import HudInfo
    from abilities import BaseHudAbilities
    from buildings import HudBuildConstruction
    from infobox import BaseHudInfo, AbilityHudInfo, UnitHudInfo, QueueUnitHudInfo
    from minimap import BaseHudMinimap
    from portrait import BaseHudPortrait
    from units import HudUnitsContainer, BaseHudUnits, BaseHudSingleUnit, BaseHudSingleUnitCombat
    from resourceindicator import HudResourceIndicator, hudresourceindicator
    from notifier import HudNotifier, NotifierLine, hudnotifier
    from groups import BaseHudGroups
    from abilitybutton import AbilityButton
    from rallyline import FXRallyLine
    
    from player_names import HudPlayerNames
    import cunit_display # TODO: Make optional?
    from sandbox import HudSandbox, HudDirectControl
    
    from vgui import localize, images
    from core.abilities import GetAbilityInfo
    
# User messages 
@usermessage('resourceindicator')
def InsertResourceIndicator(origin, *args, **kwargs):
    hudresourceindicator.Get().Add(origin, args[0] if len(args) > 0 else '1')
    
@usermessage(messagename='notifier_insertmsg')
def NotifierInsertMessage(text, **kwargs):
    if text and text[0] == '#':
        localizedtext = localize.Find(text)
        if localizedtext:
            text = localizedtext.encode('ascii')
    hudnotifier.Get().InsertMessage(
        NotifierLine(hudnotifier.Get(), text)
    )
    
@usermessage(messagename='notifier_insertabimsg')
def NotifierInsertAbilityMessage(ability, text, **kwargs):
    info = GetAbilityInfo(ability)
    if not info:
        icon = images.GetImage('vgui/units/unit_unknown.vmt')
    else:
        icon = info.image
    
    if text and text[0] == '#':
        localizedtext = localize.Find(text)
        if localizedtext:
            text = localizedtext.encode('ascii')
            
    hudnotifier.Get().InsertMessage(
        NotifierLine(hudnotifier.Get(), text, icon=icon)
    )