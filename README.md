npyscreen2
==========

Python user interfaces while getting eaten by a grue

Rationale
---------

Perhaps I've gone a little mad, but I wanted to see what I could do if I took a
swing at rebuilding npyscreen to change some core components of implementation.
The main changes I am pursuing right now are: an implementation based on the
inheritance scheme Widget -> Container -> Form, integrated logging to help track
application actions, general refactoring, and simple use of live-updated
widgets.

Asynchronicity might also be explored in the future. 

If nothing else, this project has driven me to explore npyscreen in detail and
hopefully that experience might at least help there.

npyscreen - https://code.google.com/p/npyscreen/ - Nicholas Cole

npyscreen2 - https://github.com/SavinaRoja/npyscreen2 - Paul Barton
