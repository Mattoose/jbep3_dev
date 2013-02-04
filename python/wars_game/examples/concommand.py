""" Purpose: Example of how to create a concommand """

# The gameinterface module contains the ConCommand class
from gameinterface import ConCommand

# The method that will be called when the command is executed
# It gets one argument: the arguments of the command
def test_callback( args ):
    # Print a message
    print("Message from test_callback")

# Creation of the command.
# ConCommand takes four arguments. The first argument is the name.
# By this name the command will be known when you execute it in the console.
# The second argument is the method that is called when being executed.
# The third argument is the help string.
# The fourth argument are the flags.
# You must assign the ConCommand to a name. As long as python has a reference to
# the command, the command will exist. When this module reloads it's automatically 
# cleaned up.
example_command = ConCommand( "test_callback", test_callback, "Help string", 0 )