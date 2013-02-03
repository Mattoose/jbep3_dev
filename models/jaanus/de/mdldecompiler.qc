$cd "E:\Steam\steamapps\sourcemods\hljb\models\jaanus\de"
$modelname "jaanus\v_drilldo.mdl"
$model "studio" "drilldo.smd"

$cdmaterials "jaanus\"
$cdmaterials "models\Weapons\V_hand\"
$hboxset "default"
$hbox 0 "ValveBiped.Bip01_Spine4" 0.000  0.000  -1.938  2.033  1.001  0.000
$hbox 0 "ValveBiped.Bip01_R_Forearm" -1.936  -3.134  -2.710  11.482  2.550  3.047
$hbox 0 "ValveBiped.Bip01_R_Hand" -0.847  -2.781  -2.009  6.115  1.043  2.113
$hbox 0 "objdrilldo_drilldo_auv01" -1.310  -11.342  -5.621  1.480  5.305  5.054
$hbox 0 "ValveBiped.Bip01_R_Finger0" 0.000  -0.468  -0.000  2.212  0.962  1.217
$hbox 0 "ValveBiped.Bip01_R_Finger01" 0.000  -0.358  -0.568  1.261  1.035  0.696
$hbox 0 "ValveBiped.Bip01_R_Finger02" 0.000  -6.017  -6.562  3.085  0.657  0.563
$hbox 0 "objdrilldo_dildo_auv01" -1.426  -15.985  0.000  1.576  0.000  4.647
$attachment "muzzle" "ValveBiped.muzzle" 0.00 0.00 -0.00 rotate -0.00 0.00 0.00
$attachment "1" "ValveBiped.eject" -1.00 -0.00 -0.00 rotate -0.00 90.00 180.00
$surfaceprop "default"
$illumposition 19.554 -5.247 -15.855
$sequence idle01 "idle01" loop ACT_VM_IDLE 1 fps 30.00 node 0
$sequence idle01empty "idle01empty" loop ACT_VM_IDLE_EMPTY 1 fps 30.00 node 0
$sequence fire "fire" ACT_VM_PRIMARYATTACK 1 fps 60.00
$sequence fire1 "fire1" ACT_VM_RECOIL1 1 fps 60.00
$sequence fire2 "fire2" ACT_VM_RECOIL2 1 fps 60.00
$sequence fire3 "fire3" ACT_VM_RECOIL3 1 fps 60.00
$sequence fireempty "fireempty" ACT_VM_DRYFIRE 1 fps 30.00 node 2
$sequence draw "draw" ACT_VM_DRAW 1 fps 30.00 node 0
$sequence drawempty "drawempty" fps 30.00 node 0
$sequence reload "reload" ACT_VM_RELOAD 1 fps 30.00 node 0
$sequence holster "holster" ACT_VM_HOLSTER 1 fps 30.00 node 0
$sequence holsterempty "holsterempty" ACT_VM_HOLSTER 1 fps 30.00 node 0
$sequence idletolow "idletolow" ACT_VM_LOWERED_TO_IDLE 1 fps 30.00 transition 0 1
$sequence lowtoidle "lowtoidle" ACT_VM_IDLE_TO_LOWERED 1 fps 30.00 transition 1 0
$sequence lowidle "lowidle" loop ACT_VM_IDLE_LOWERED 1 fps 30.00 node 1
