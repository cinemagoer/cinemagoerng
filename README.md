# CinemagoerNG

CinemagoerNG is a Python library and command-line utility
for parsing IMDb data.
It provides a clean, modern API for accessing movie, TV show,
and celebrity information from the IMDb.

> [!Note]
> This project and its authors are not affiliated
> with the Internet Movie Database Inc.
> See the [`DISCLAIMER.txt`](DISCLAIMER.txt)
> file for details about terms of use.

## Features

- Parse comprehensive movie and TV show information.
- Support for alternate titles (AKAs).
- Taglines and parental guide information.
- Episode data for TV series.
- Modern Python typing support.
- Clean, intuitive API.

## Important notice

*As of April 2026, due to WAF policies on the IMDb web site,
CinemagoerNG no longer contains any code to retrieve the pages.
In order to use the library, you have to provide a function that will
return the content for a given IMDb URL:*

```python
def fetch_custom(url: str) -> str:
    """Somehow return the contents of the URL."""

import cinemagoerng.web

cinemagoerng.web.fetcher.set(fetch_custom)
```

This function does not necessarily have to make an HTTP/HTTPS connection;
it could also read the content from some files or database
that have been populated earlier.

## Installation

CinemagoerNG supports Python 3.11 and later versions.
You can install it using pip:

```bash
pip install cinemagoerng
```

## Basic usage

Here's a simple example of parsing movie information:

```python
from cinemagoerng import web as imdb

# Get basic movie information
movie = imdb.get_title("tt0133093")  # The Matrix
print(movie.title)       # "The Matrix"
print(movie.sort_title)  # "Matrix"
print(movie.year)        # 1999
print(movie.runtime)     # 136

# Access movie genres
for genre in movie.genres:
    print(genre)         # "Action", "Sci-Fi"

# Get director information
for credit in movie.directors:
    print(credit.name)   # "Lana Wachowski", "Lilly Wachowski"
```

### Parsing additional information

You can fetch additional details using the relevant `set_` functions:

```python
# Set all taglines
imdb.set_taglines(movie)
for tagline in movie.taglines:
    print(tagline)

# Get alternate titles (AKAs)
imdb.set_akas(movie)
for aka in movie.akas:
    print(f"{aka.title} ({aka.country})")
```

## Available data

CinemagoerNG can parse various types of information:

### Basic information

- Title
- Year
- Runtime
- Genres
- Plot summary
- Rating
- Number of votes

### Credits

- Directors
- Writers
- Producers
- Cast members
- Crew members

### Additional details

- Taglines
- Alternative titles (AKAs)
- Episode information (for TV series)
- Parental guide

## Development

It is recommended to use `uv` for development:

```bash
# Clone the repository
git clone https://github.com/cinemagoer/cinemagoerng.git
cd cinemagoerng

# Set up environment
uv sync

# Run tests
uv run pytest

# Run type checks
uv run mypy src tests

# Check code style
uv run ruff check src tests

# Test under all supported Python versions
uv run tox
```

## License

This project is licensed under the GNU General Public License v3 - see the
[`LICENSE.txt`](LICENSE.txt) file for details.

## Acknowledgments

CinemagoerNG is a modern reimagining of the original
[Cinemagoer/IMDbPY](https://github.com/cinemagoer/cinemagoer) project.
Special thanks to:

- All contributors to the original Cinemagoer (IMDbPY) project.
- The IMDb website for providing the data.
