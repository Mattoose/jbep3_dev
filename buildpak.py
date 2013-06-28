# User settings (don't use the \ character)
target_folders = [ "maps", "materials", "models", "particles", "scenes", "html", "sound", "scripts",
"resource", "media" ]
file_types = [ "vmt", "vtf", "mdl", "phy", "vtx", "vvd", "ani",
"pcf", "vcd", "bsp", "html", "js", "jpg", "webm", "wav", "mp3",
"cache", "txt", "res" ]
vpk_path = "../../common/Source SDK Base 2013 Multiplayer/bin/vpk.exe"
 
# Script begins
import os,subprocess
from os.path import join
response_path = join(os.getcwd(),"vpk_list.txt")
 
out = open(response_path,'w')
len_cd = len(os.getcwd()) + 1
 
for user_folder in target_folders:
	for root, dirs, files in os.walk(join(os.getcwd(),user_folder)):
		for file in files:
			if len(file_types) and file.rsplit(".")[-1] in file_types:
				out.write(os.path.join(root[len_cd:].replace("/","\\"),file) + "\n")
 
out.close()
 
subprocess.call([vpk_path, "-c", "10", "-M", "a", "jb_content", "@" + response_path])