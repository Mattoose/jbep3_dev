#========= Copyright 2006-2008, HL2Wars Corporation, All rights reserved. ============//
#
# Purpose: Example of how to create a concommand
#
#=============================================================================//
# The gameinterface module contains the ConVar class
from gameinterface import ConVar
    
# Called when the convar value changes    
def test_callback(var, old_value, f_old_value):
    print('test_callback')
    # Convar instance
    print var
    
    # Old string value
    print old_value
    
    # Old float value
    print f_old_value
    
example_convar = ConVar('test_convar', 'test_default_value', 0, 'Halp!!', test_callback)