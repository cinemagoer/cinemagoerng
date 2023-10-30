CinemagoerNG
============

CinemagoerNG (Next Generation) is a Python module and command-line utility
for retrieving data from the IMDb.

Usage example (subject to change):

.. code-block:: Python

   from cinemagoerng import web

   matrix = web.get_title(133093)
   print(type(matrix))     # class: Movie
   print(matrix.year)      # 1999
   print(matrix.genres)    # ["Action", "Sci-Fi"]
   print(matrix.taglines)  # []
   matrix = web.update_title(matrix, infoset="taglines")
   print(matrix.taglines)  # ["Free your mind", ...]

   blink = web.get_title(1000252)
   print(type(blink))      # class: TVEpisode
