# Grabbed from https://developer.valvesoftware.com/wiki/VPK
# Modified by jimbomcb

# User settings (don't use the \ character)
def generate_vpk( vpk_name, vpk_folders ):
	vpk_path = "../../common/Source SDK Base 2013 Multiplayer/bin/vpk.exe"
	target_folders = vpk_folders
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
	 
	#subprocess.call([vpk_path, "-k", "jaykinbacon.publickey.vdf", "-K", "jaykinbacon.privatekey.vdf", "-P", "-M", "-c", "1", "a", vpk_name, "@" + response_path])
	subprocess.call([vpk_path, "-P", "-M", "-c", "1", "a", vpk_name, "@" + response_path])
	
generate_vpk( "jb_content", ["materials","models","sound","particles","scenes"] )