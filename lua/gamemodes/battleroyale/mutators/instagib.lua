local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeInsta_Title"
mutator.Description = "#JB_BR_RoundTypeInsta_Desc"

mutator.ItemPool = {
	"weapon_handgun_insta",
	"weapon_goldengun",
	"weapon_railgun_insta",
	"weapon_neszapper",
}

mutators:Register( "instagib", mutator )

