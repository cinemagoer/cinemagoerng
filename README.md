# CinemagoerNG

CinemagoerNG (Next Generation) is a Python library and command-line utility
for retrieving data from the IMDb.

> [!Note]
> This project and its authors are not affiliated in any way
  to Internet Movie Database Inc.
  See the [`DISCLAIMER.txt`](https://raw.githubusercontent.com/cinemagoer/cinemagoerng/main/DISCLAIMER.txt)
  file for details about terms of use.

Usage example (subject to change):

```python

from cinemagoerng import web

movie = web.get_title("tt0133093")
print(movie.title)       # "The Matrix"
print(movie.sort_title)  # "Matrix"
print(movie.year)        # 1999
print(movie.runtime)     # 136

for genre in movie.genres:
   print(genre)          # "Action", "Sci-Fi"

for credit in movie.directors:
   print(credit.name)    # "Lana Wachowski", "Lilly Wachowski"

print(len(movie.taglines))  # 1
for tagline in movie.taglines:
   print(tagline)        # "Free your mind"

web.update_title(movie, page="taglines", keys=["taglines"])
print(len(movie.taglines))  # 15
```
