# CinemagoerNG

CinemagoerNG (Next Generation) is a Python library and command-line utility
for retrieving data from IMDb.
It provides a clean, modern API for accessing movie, TV show,
and celebrity information from IMDb.

> [!Note]
> This project and its authors are not affiliated
| with the Internet Movie Database Inc.
> See the [`DISCLAIMER.txt`](https://raw.githubusercontent.com/cinemagoer/cinemagoerng/main/DISCLAIMER.txt)
> file for details about terms of use.

## Features

- Retrieve comprehensive movie and TV show information.
- Support for alternate titles (AKAs).
- Taglines and parental guide information.
- Episode data for TV series.
- Synchronous and Asynchronous support for all operations
- Modern Python typing support.
- Clean, intuitive API.

## Installation

You can install CinemagoerNG using pip:

```bash
pip install cinemagoerng

# Or, for the latest version from GitHub:
pip install git+https://github.com/cinemagoer/cinemagoerng.git
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

# Async Usage
movie = await web.get_title_async("tt0133093")

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

# Async Usage
await web.update_title_async(movie, page="taglines", keys=["taglines"])

# Get alternate titles (AKAs)
web.update_title(movie, page="akas", keys=["akas"])
for aka in movie.akas:
    print(f"{aka.title} ({aka.country})")
```

### Configuring HTTPX Parameters

CinemagoerNG uses HTTPX for making HTTP requests. You can customize the HTTPX client configuration by passing parameters:

```python
# Using HTTP proxy
movie = web.get_title("tt0133093", httpx_kwargs={"proxy": "http://proxy.example.com:8080"})

# Using SOCKS5 proxy (requires httpx[socks] extra)
movie = web.get_title("tt0133093", httpx_kwargs={"proxy": "socks5://127.0.0.1:1080"})

# Configuring timeout and other parameters
movie = web.get_title("tt0133093", httpx_kwargs={
    "timeout": 60.0,
    "proxy": "http://proxy.example.com:8080",
    "follow_redirects": False
})

# Using with update
web.update_title(movie, page="episodes", keys=["episodes"], 
                httpx_kwargs={"timeout": 60.0})
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

## Advanced Usage Examples
For comprehensive examples of how to use CinemagoerNG's features, check out our test files in the [tests](tests) directory.

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/cinemagoer/cinemagoerng.git
cd cinemagoerng

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run type checks
mypy cinemagoerng

# Check code style
ruff check --preview cinemagoerng tests

# Format code
ruff format cinemagoerng tests
```

## Python Version Support

CinemagoerNG supports Python 3.10 and later versions, including:

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- PyPy 3.10

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
For major changes, please open an issue first to discuss what you would like
to change.

## License

This project is licensed under the
GNU General Public License v3 or later (GPLv3+) - see the
[LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

CinemagoerNG is a modern reimagining of the original Cinemagoer/IMDbPY project.
Special thanks to:

- All contributors to the original Cinemagoer (IMDbPY) project.
- The IMDb website for providing the data.
- The Python community for their invaluable feedback and contributions.
