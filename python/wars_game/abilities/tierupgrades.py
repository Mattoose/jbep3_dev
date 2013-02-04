from core.abilities import AbilityUpgrade

class Tier2UpgradeInfo(AbilityUpgrade):
    name = 'or_tier2_research'
    displayname = '#AbilityTier2Research_Name'
    description = '#AbilityTier2Research_Description'
    image_name = "vgui/abilities/tier2combine.vmt"
    buildtime = 0.0
    costs = [('kills', 20)]
    successorability = 'or_tier3_research'
    
class Tier3UpgradeInfo(AbilityUpgrade):
    name = 'or_tier3_research'
    displayname = '#AbilityTier3Research_Name'
    description = '#AbilityTier3Research_Description'
    image_name  = "vgui/abilities/tier3combine.vmt"
    buildtime = 0.0
    costs = [('kills', 20)]
