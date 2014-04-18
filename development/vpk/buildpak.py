# By John McBroom
# Generates VPKs using SteamPipe friendly way, based on
# the scripts at https://forums.alliedmods.net/showthread.php?t=214845

import os,subprocess
import time,sys
from os.path import join
import math
import shutil
import hashlib
from datetime import datetime

def md5sum(filename, blocksize=65536):
    hash = hashlib.md5()
    with open(filename, "r+b") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            hash.update(block)
    return hash.hexdigest()
	
def fancy_progress(txt,current,max):
	pct = float( current ) / float( max )
	segments = int(round( pct * 20.0, 1))
	fmt = '[{0}{1}] {2}/{3}'.format('#'*segments, ' '* (20-segments), current, max )
	sys.stdout.write("\r"+txt+fmt)
	
def buildvpk( vpk_path, vpk_name, root_path, target_folders ):
	current_dir = os.getcwd()
	os.chdir( root_path )
	root_dir = os.getcwd()
	os.chdir( current_dir )
	
	vpk_exe_path = root_dir+"/../../common/Source SDK Base 2013 Multiplayer/bin/vpk.exe"
	
	file_types_exclude = [ "cache" ]
	kv_path = join(os.getcwd(),vpk_name+"_kv.txt")
	kv_path_backup = join(os.getcwd(),vpk_name+"_kv.txt.bak")
	
	do_kv_build = True
	do_vpk_build = True
	do_md5 = True
	 
	if ( do_kv_build ):
		# Build our files KV file
		kv_files = {}
		len_cd = len(root_dir) + 1
		total_files = 0
		current_file = 0
		
		print "Counting files"
		for user_folder in target_folders:
			for root, dirs, files in os.walk(join(os.getcwd(),root_dir+"\\"+user_folder)):
				total_files += len(files)
		
		print "Calculating file MD5s"
		for user_folder in target_folders:
			for root, dirs, files in os.walk(join(os.getcwd(),root_dir+"\\"+user_folder)):
				for file in files:
					if len(file_types_exclude) and file.rsplit(".")[-1] not in file_types_exclude:
						fancy_progress( "", current_file, total_files )
						full_path = os.path.join(root.replace("/","\\"), file)
						relative_path = os.path.join(root[len_cd:].replace("/","\\"), file)
						kv_files[ full_path ] = {}
						kv_files[ full_path ][ "destpath" ] = relative_path
						
						if ( do_md5 ):
							kv_files[ full_path ][ "md5" ] = md5sum( full_path )
						
						current_file += 1

		# Write to file
		print "\nWriting KV file"
		out = open(kv_path,'w')
		
		for srcpath,data in kv_files.iteritems():
			out.write( '"file"\n{\n\t"srcpath" "'+srcpath+'"\n\t"destpath" "'+data["destpath"]+'"\n' )			
			if ( "md5" in data ): out.write( '\t"MD5" "'+data["md5"]+'"\n' )
			out.write( '}\n' )
		
		out.close()
	 
	# run the VPK
	if ( do_vpk_build ):
		print "Running VPK tool"
		vpk_result = subprocess.call([vpk_exe_path, "-P", "-c", "90", 
			"-K", "C:\Code\jbep3-2013\keys\jaykinbacon.privatekey.vdf", 
			"-k", "C:\Code\jbep3-2013\keys\jaykinbacon.publickey.vdf", 
			"k", vpk_path+vpk_name, kv_path ])
		
		# panic if the vpk didn't run :(
		if ( vpk_result != 0 ):
			sys.exit("\n\n\n!!!VPK build failed!!!\n\n")
			
		# back up KV file
		if ( os.path.isfile(kv_path_backup) ):
			backup_path = join(os.getcwd(),"backup/")
			if ( not os.path.isdir( backup_path ) ): os.mkdir(backup_path)
			shutil.move(kv_path_backup, backup_path+"/"+vpk_name+"_kv.txt.bak."+datetime.now().strftime("%d.%m.%Y-%H.%M.%S"))
			
		shutil.move(kv_path, kv_path_backup)
		

buildvpk( "..\\..\\content\\", "jb_content", "..\\..\\", ["materials","models","sound","particles","scenes"] )