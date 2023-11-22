# Copyright 2023 H. Turgut Uyar <uyar@tekir.org>
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
from argparse import ArgumentParser, Namespace

from cinemagoerng import __version__, web
from cinemagoerng.model import TITLE_TYPE_NAMES


def get_item(args: Namespace) -> None:
    if args.type == "title":
        item = web.get_title(args.imdb_id)

        if args.taglines:
            item = web.update_title(item, infoset="taglines")

        type_name = TITLE_TYPE_NAMES[item.__class__]
        print(f"Title: {item.title} ({type_name})")

        if item.year is not None:
            print(f"Year: {item.year}")

        runtime: int | None = getattr(item, "runtime", None)
        if runtime is not None:
            print(f"Runtime: {runtime} min")

        if item.rating is not None:
            print(f"Rating: {item.rating} ({item.vote_count} votes)")

        if len(item.genres) > 0:
            genres = ", ".join(item.genres)
            print(f"Genres: {genres}")

        indent = "  "
        wrap = 72

        plot_en = item.plot.get("en-US", "Plot undisclosed.")
        if plot_en != "Plot undisclosed.":
            plot = textwrap.fill(plot_en, width=wrap, initial_indent=indent,
                                 subsequent_indent=indent)
            print(f"Plot:\n{plot}")

        if args.taglines and (len(item.taglines) > 0):
            subindent = "  "
            taglines = f"\n{indent}- ".join(
                textwrap.fill(t, width=wrap - len(indent) - len(subindent),
                              subsequent_indent=indent + subindent)
                for t in item.taglines
            )
            print(f"Taglines:\n{indent}- {taglines}")


def main(argv: list[str] | None = None) -> None:
    parser = ArgumentParser(description="Retrieve data from the IMDb.")
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(metavar="command", dest="command")
    subparsers.required = True

    subparser_get = subparsers.add_parser(
        "get",
        help="retrieve information about an item",
    )
    subparser_get.add_argument(
        "type", choices=["title"],
        help="type of item to retrieve",
    )
    subparser_get.add_argument(
        "imdb_id", type=int,
        help="IMDb id of item to retrieve",
    )
    subparser_get.add_argument(
        "--taglines", action="store_true",
        help="include taglines",
    )
    subparser_get.set_defaults(func=get_item)

    arguments = parser.parse_args(argv if argv is not None else sys.argv[1:])
    arguments.func(arguments)
