CinemagoerNG
============

.. admonition::

   This project and its authors are not affiliated in any way
   to Internet Movie Dat abase Inc.
   See the `DISCLAIMER.txt`_ file for details about terms of use.

CinemagoerNG (Next Generation) is a Python library and command-line utility
for retrieving data from the IMDb.

Usage example (subject to change):

.. code-block:: python

   >>> from cinemagoerng import web
   >>> matrix = web.get_title("tt0133093")
   >>> type(matrix)
   <class 'cinemagoerng.model.Movie'>
   >>> matrix.title
   'The Matrix'
   >>> matrix.year
   1999
   >>> matrix.runtime
   136
   >>> matrix.genres
   ['Action', 'Sci-Fi']
   >>> matrix.sort_title
   'Matrix'
   >>> len(matrix.directors)
   2
   >>> matrix.directors[0].name
   'Lana Wachowski'
   >>> matrix.taglines
   []
   >>> web.update_title(matrix, page="taglines")
   >>> len(matrix.taglines)
   15
   >>> matrix.taglines[0]
   'Free your mind'
   >>> matrix_game = web.get_title("tt0390244")
   >>> type(matrix_game)
   <class 'cinemagoerng.model.VideoGame'>
   >>> matrix_game.title
   'The Matrix Online'
   >>> matrix_game.runtime
   AttributeError: 'VideoGame' object has no attribute 'runtime'
