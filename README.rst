CinemagoerNG
============

.. admonition::

   This project and its authors are not affiliated in any way
   to Internet Movie Database Inc.
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
   >>> matrix.sort_title
   'Matrix'
   >>> matrix.year
   1999
   >>> matrix.runtime
   136
   >>> matrix.genres
   ['Action', 'Sci-Fi']
   >>> len(matrix.directors)
   2
   >>> matrix.directors[0].name
   'Lana Wachowski'
   >>> matrix.taglines
   ['Free your mind']
   >>> web.update_title(matrix, page="taglines", keys=["taglines"])
   >>> len(matrix.taglines)
   15

.. _DISCLAIMER.txt: https://raw.githubusercontent.com/cinemagoer/cinemagoerng/main/DISCLAIMER.txt
