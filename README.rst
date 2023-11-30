CinemagoerNG
============

CinemagoerNG (Next Generation) is a Python library and command-line utility
for retrieving data from the IMDb.

Usage example (subject to change):

.. code-block:: python

   from cinemagoerng import web

   matrix = web.get_title("tt0133093")
   print(type(matrix))     # class: Movie
   print(matrix.title)     # "The Matrix"
   print(matrix.year)      # 1999
   print(matrix.runtime)   # 136
   print(matrix.genres)    # ["Action", "Sci-Fi"]
   print(matrix.taglines)  # []

   matrix = web.update_title(matrix, page="taglines")
   print(matrix.taglines)  # ["Free your mind", ...]

   game = web.get_title("tt0390244")
   print(type(game))       # class: VideoGame
   print(game.title)       # "The Matrix Online"
   print(game.runtime)     # raises AttributeError
