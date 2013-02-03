import os, datetime, time, shutil, commands

ourDir = time.strftime( "%d_%m_%y-%H_%M_%S" )
codeDir = os.environ["JB_CODE_DIR"]

print "Backing up PDBs from " + codeDir

os.chdir("PDBs")
os.mkdir(ourDir)
os.chdir(ourDir)

shutil.copy( "../../bin/server.dll", "." )
shutil.copy( "../../bin/client.dll", "." )
shutil.copy( codeDir + "/game/server/release/server.pdb", "." )
shutil.copy( codeDir + "/game/client/release/client.pdb", "." )

os.chdir("../../")

print "Pushing..."

os.system('git push')

print "Done."

raw_input()