# John McBroom for JBEP3
import yaml
import wave
import os
from mutagen.mp3 import MP3

def getAudioLength( sFile ):
	szWavPath = "../sound/{0}".format(sFile)
	
	if ( "wav" in sFile ): 
		wfile = wave.open ( szWavPath, "r")
		return ( 1.0 * wfile.getnframes() ) / wfile.getframerate()
	else:
		f = MP3( szWavPath )
		return f.info.length

def parseYAMLData( sFile ):
	lYAMLData = yaml.load(open("vo_databases/{0}".format(sFile), "r"))

	sTemplateSoundscript = open("vo_internal/base.template.txt", "r").read()
	sTemplateVCD = open("vo_internal/base.template.vcd", "r").read()

	sOutputPath = "scripts/{0}.txt".format( lYAMLData["settings"]["output"] )
	lCategories = lYAMLData["categories"]
	sSoundscriptOutput = sTemplateSoundscript

	print "Outputting soundscript to {0}".format( sOutputPath )

	for (sTitle, lData) in lYAMLData["sounds"].items():

		if lData["category"] not in lCategories:
			print "Invalid category "+ lData["category"]
			
		lSoundCategory = lCategories[lData["category"]]
		bHasMultipleSounds = ( "waves" in lData )
		sPrefix = lData["wave_prefix"] if lData["wave_prefix"] is not None else ""
		
		# Sound category info
		sSoundscriptOutput += """
		"{0}"
		{{
			"channel"		"{1}"
			"volume"		"{2}"
			"pitch"			"{3}"
			"soundlevel"	"{4}"
	""".format( sTitle, lSoundCategory["channel"], lSoundCategory["volume"],
				lSoundCategory["pitch"], lSoundCategory["soundlevel"] )

		if ( not bHasMultipleSounds ):
		
			sSoundscriptOutput += """
			"wave"		"{0}{1}"
		""".format( sPrefix, lData["wave"] )
		
		else:
			
			sSoundscriptOutput += """
			"rndwave"		
			{"""
			
			for sWave in lData["waves"]:
				sSoundscriptOutput += """
				"wave"	"{0}" """.format(sWave)
		
			sSoundscriptOutput += """
			} """
			
		sSoundscriptOutput += """
		} """
		
	fSoundScriptHandle = open("../{0}".format( sOutputPath ),"w+")
	fSoundScriptHandle.write( sSoundscriptOutput )
	fSoundScriptHandle.close()

	print "Done."
	print "Generating VCDs"
		
	for (sTitle, lData) in lYAMLData["sounds"].items():
		if ( lData["vcd"] is None or lData["vcd"] is False ): continue
		
		bHasMultipleSounds = ( "waves" in lData )
		if ( bHasMultipleSounds ):
			print "Can't generate VCDs for random wave soundscripts yet."
			continue
		
		sVCDPath = "../scenes/{0}".format(lData["wave"]).replace(".wav",".vcd")
		( sVCDDirectory, sVCDFileName ) = os.path.split( sVCDPath )
		flWavDuration = getAudioLength( lData["wave"] )
		
		sVCDOutput = sTemplateVCD
		sVCDOutput = sVCDOutput.replace( "%SOUND_NAME%", sTitle )
		sVCDOutput = sVCDOutput.replace( "%SOUND_DURATION%", str(flWavDuration) )
		
		if ( not os.path.exists( sVCDDirectory ) ) :
			os.makedirs(sVCDDirectory)
		
		fVCDHandle = open( sVCDPath, "w+" )
		fVCDHandle.write( sVCDOutput )
		fVCDHandle.close()
		
	print "Done."

for root, _, files in os.walk("vo_databases"):
	for file in files:
		parseYAMLData( file )