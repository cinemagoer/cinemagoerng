# Copyright 2024 H. Turgut Uyar <uyar@tekir.org>
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CinemagoerNG; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys
import textwrap
from argparse import ArgumentParser

from cinemagoerng import __version__, web


_INDENT = "  "
_LINE_WIDTH = 72


def get_title(imdb_num: int, taglines: bool = False) -> None:
    item = web.get_title(f"tt{imdb_num:07d}")
    if item is None:
        print("No title with this IMDb number was found.")
        sys.exit()

    if taglines:
        item = web.update_title(item, page="taglines")

    print(f"Title: {item.title} ({item.__class__.__name__})")

    if item.year is not None:
        print(f"Year: {item.year}")

    runtime: int | None = getattr(item, "runtime", None)
    if runtime is not None:
        print(f"Runtime: {runtime} min")

    if len(item.genres) > 0:
        label = "Genre" if len(item.genres) == 1 else "Genres"
        genres = ", ".join(item.genres)
        print(f"{label}: {genres}")

    if len(item.country_codes) > 0:
        label = "Country" if len(item.country_codes) == 1 else "Countries"
        countries = ", ".join(item.countries)
        print(f"{label}: {countries}")

    if len(item.language_codes) > 0:
        label = "Language" if len(item.language_codes) == 1 else "Languages"
        languages = ", ".join(item.languages)
        print(f"{label}: {languages}")

    if item.rating is not None:
        print(f"Rating: {item.rating} ({item.vote_count} votes)")

    plot_en = item.plot.get("en-US", "Plot undisclosed.")
    if plot_en != "Plot undisclosed.":
        print("Plot:")
        plot_text = textwrap.fill(plot_en, width=_LINE_WIDTH,
                                  initial_indent=_INDENT,
                                  subsequent_indent=_INDENT)
        print(plot_text)

    if len(item.taglines) > 0:
        print("Taglines:")
        subindent = _INDENT + "  "
        for tagline in item.taglines:
            tagline_text = textwrap.fill("- " + tagline,
                                         width=_LINE_WIDTH,
                                         initial_indent=_INDENT,
                                         subsequent_indent=subindent)
            print(tagline_text)


def main(argv: list[str] | None = None) -> None:
    parser = ArgumentParser(description="Retrieve data from the IMDb.")
    parser.add_argument("--version", action="version", version=__version__)

    command = parser.add_subparsers(metavar="command")
    command.required = True

    parser_get = command.add_parser(
        "get",
        help="retrieve information about an item",
    )

    item_type = parser_get.add_subparsers(
        metavar="type",
        help="type of item to retrieve",
    )
    item_type.required = True

    parser_get_title = item_type.add_parser(
        "title",
        help="retrieve information about a title",
    )
    parser_get_title.add_argument(
        "imdb_num", type=int,
        help="IMDb number of title",
    )
    parser_get_title.add_argument(
        "--taglines", action="store_true",
        help="include taglines",
    )
    parser_get_title.set_defaults(handler=get_title)

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    arguments = vars(args)
    handler = arguments.pop("handler")
    handler(**arguments)
