# Grabbed from https://developer.valvesoftware.com/wiki/VPK
# Modified by jimbomcb

# User settings (don't use the \ character)
vpk_path = "../../common/Source SDK Base 2013 Multiplayer/bin/vpk.exe"
#target_folders = [ "maps", "materials", "models", "particles", "scenes", "html", "sound", "scripts", "resource", "media" ]
target_folders = [ "materials/halflife" ]
file_types_exclude = [ "cache" ]
 
# Script begins
import os,subprocess
from os.path import join
response_path = join(os.getcwd(),"vpk_list.txt")
 
out = open(response_path,'w')
len_cd = len(os.getcwd()) + 1
 
for user_folder in target_folders:
	for root, dirs, files in os.walk(join(os.getcwd(),user_folder)):
		for file in files:
			if len(file_types_exclude) and file.rsplit(".")[-1] not in file_types_exclude:
				out.write(os.path.join(root[len_cd:].replace("/","\\"),file) + "\n")
 
out.close()
 
subprocess.call([vpk_path, "-c", "10", "-M", "a", "jb_content", "@" + response_path])