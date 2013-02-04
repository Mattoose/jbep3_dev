.. _tut-gamepackages:

**********************************
Gamepackages
**********************************
In the previous topic we modified the game package *tutorial*. In 
Half-Life 2: Wars all game related code is organized into game packages.
These packages are actual just normal Python packages (see 
`python.org <http://docs.python.org/tutorial/modules.html#packages>`_) 
with the difference they are registered in the
gamemgr module and define methods for loading, unloading and reloading
code.

.. image:: gamepackageoverview.png

Let us take a look at the __init__.py file of the *tutorial* gamepackage::

    from gamemgr import RegisterGamePackage
    from srcmgr import ImportSubMods, ReloadSubMods

    RegisterGamePackage(
            name=__name__,
            dependencies=['core']
    )

    def LoadGame():
        import gamerules
        import units
        import abilities
        
        ImportSubMods(gamerules)
        ImportSubMods(units)
        ImportSubMods(abilities)
        
    def UnloadGame():  
        pass 
        
    def ReloadGame():
        ReloadSubMods(gamerules)
        ReloadSubMods(units)
        ReloadSubMods(abilities)
        
**RegisterGamePackage** will register our gamepackage inside the gamemgr module. It uses 
the name of the module (*__name__* is a special variable) and furthermore says we have
a dependency on the core game package.

Then it defines three methods for loading, unloading and reloading respectively.
Inside the **LoadGame** method you must import all the modules that contain units,
abilities or other things to make them register within the gamepackage. You can 
use the method *ImportSubMods* to import all modules inside a directory. This way
you do not have to worry if the module is imported.

The **UnloadGame** is called when the game package is unloaded and you usually do not have
to do anything here.

The **ReloadGame** method is for developing. Here you reload your code. Again a convenient
method *ReloadSubMods* is available to reload a whole directory. However in case you have
dependencies you will need to use the normal *reload* method (see the *core* and *wars_game*
gamepackages for examples on how to do this).

The *gamemgr* module will do the following when you execute ''load_gamepackage tutorial''
when *tutorial* is not loaded yet:

1. Import the package. The import is supposed to make the gamepackage register.
2. Call LoadGamepackage on all dependencies of the gamepackage.
3. Call the LoadGame method of the gamepackage. The LoadGame is supposed to import 
   (and register by doing so) the units, abilities, huds, etc.
4. Dispatch a *gamepackagechanged* signal.
5. Send message to all clients to load this gamepackage (and then repeats the above process on those clients).

Core and Wars Gamepackage
============================
The *core* gamepackage defines most of the baseclasses for Half-life 2: Wars. Most of
the time when creating a new units, ability, or anything you will use this gamepackage.

The *wars_game* gamepackage defines the actual game and contains all the rebels and 
combine units, buildings, the different gamemodes and the huds.
