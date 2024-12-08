# CinemagoerNG

CinemagoerNG (Next Generation) is a Python library and command-line utility for retrieving data from IMDb. It provides a clean, modern API for accessing movie, TV show, and celebrity information from IMDb.

> [!Note]
> This project and its authors are not affiliated in any way with Internet Movie Database Inc.
> See the [`DISCLAIMER.txt`](https://raw.githubusercontent.com/cinemagoer/cinemagoerng/main/DISCLAIMER.txt)
> file for details about terms of use.

## Features

- Retrieve comprehensive movie and TV show information
- Support for alternate titles (AKAs)
- Taglines and parental guide information
- Episode data for TV series
- Proxy support (HTTP/SOCKS4/SOCKS5)
- Modern Python typing support
- Clean, intuitive API

## Installation

You can install CinemagoerNG using pip:

```bash
# Basic installation
pip install cinemagoerng

# With proxy support (for SOCKS proxies)
pip install cinemagoerng[socks]

# For development
pip install cinemagoerng[dev]
```

## Basic Usage

Here's a simple example of retrieving movie information:

```python
from cinemagoerng import web

# Get basic movie information
movie = web.get_title("tt0133093")  # The Matrix
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

### Retrieving Additional Information

You can fetch additional details using the `update_title` method:

```python
# Get all taglines
web.update_title(movie, page="taglines", keys=["taglines"])
for tagline in movie.taglines:
    print(tagline)

# Get alternate titles (AKAs)
web.update_title(movie, page="akas", keys=["akas"])
for aka in movie.akas:
    print(f"{aka.title} ({aka.country})")
```

### Using Proxies

CinemagoerNG supports HTTP and SOCKS proxies for accessing IMDb. To use this feature, first install with proxy support:

```bash
pip install cinemagoerng[proxy]
```

Then you can use proxies in your code:

```python
# Using HTTP proxy
movie = web.get_title("tt0133093", proxy_url="http://proxy.example.com:8080")

# Using SOCKS5 proxy
movie = web.get_title("tt0133093", proxy_url="socks5://127.0.0.1:1080")

# Using authenticated proxy
movie = web.get_title("tt0133093", proxy_url="http://user:pass@proxy.example.com:8080")

# Update with proxy
web.update_title(movie, page="episodes", keys=["episodes"], 
                proxy_url="socks5://127.0.0.1:1080")
```

## Available Data

CinemagoerNG can retrieve various types of information:

### Basic Information
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
- Cast members
- Producers
- Composers

### Additional Details
- Taglines
- Alternative titles (AKAs)
- Episode information (for TV series)
- Parental guide
- Reference information

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/cinemagoer/cinemagoerng.git
cd cinemagoerng

# Install development dependencies
pip install -e .[dev]

# Install socks dependencies (optional)
pip install -e .[socks]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run type checks
mypy cinemagoerng

# Check code style
ruff check --config pyproject.toml

# Format code
ruff format --config pyproject.toml
```

## Python Version Support

CinemagoerNG supports Python 3.10 and later versions, including:
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- PyPy 3.10

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the GNU General Public License v3 or later (GPLv3+) - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

CinemagoerNG is a modern reimagining of the original Cinemagoer/IMDbPY project. Special thanks to:
- All contributors to the original IMDbPY project
- The IMDb website for providing the data
- The Python community for their invaluable feedback and contributions