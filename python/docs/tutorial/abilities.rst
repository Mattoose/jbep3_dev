.. _tut-abilities:

**********************************
Abilities
**********************************
Abilities are used everywhere in Half-Life 2: Wars. You could see an ability as
an action, which usually involves units and mouse interaction of the player.
Several examples:

  * Producing an unit at a building
  * Ordering an unit to throw a grenade at a target location
  * Ordering an unit to construct a building
  * Using the *unitpanel* to directly spawn an unit at the mouse cursor
  * Throwing a nuke at the mouse cursor using the *abilitypanel*
  * Researching an upgrade at a building
  
AbilityBase Class
============================
The base ability class is like an empty template for creating
new abilities. Normally you do not want to directly derive
from this class, except when you want to do something different.
The class provides several common methods:

  * **TakeResources** - Takes the amount of resources specified in the costs field of the ability
  * **Refund** - Refunds the player after doing TakeResources. Usually done after canceling the ability
  * **Cancel** - Cancel the ability. Does not set a cooldown for the units executing this ability and 
    refunds the player (if resources taken and refundoncancel is set to True)
  * **Completed** - Completes the ability. Sets the cooldown time for the units executing this ability.
  * **OnLeftMouseButtonPressed** - Listen to left mouse pressed event
  * **OnLeftMouseButtonReleased** - Listen to left mouse released event
  * **OnRightMouseButtonPressed** - Listen to right mouse pressed event 
  * **OnRightMouseButtonReleased** - Listen to right mouse released event
  
When a new ability is created it is also instantiated on the client of the executing player.
This can be used to show visuals for the player executing the ability. For example you might
want to draw a circle on the terrain to indicate the target area.

The following picture is an overview of the available base classes:

.. image:: abilitiesoverview.png
   :align: center

See :mod:`core.abilities` for more information about 
the available ability classes and example usage.

