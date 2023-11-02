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
from argparse import ArgumentParser, Namespace

from cinemagoerng import __version__, web


def get_item(args: Namespace) -> None:
    if args.type == "title":
        item = web.get_title(args.imdb_id)
    if args.taglines:
        item = web.update_title(item, infoset="taglines")

    print(f"Title: {item.title} ({item.type_name})")

    year = getattr(item, "year", None)
    if year is not None:
        print(f"Year: {year}")

    runtime = getattr(item, "runtime", None)
    if runtime is not None:
        print(f"Runtime: {runtime} min")

    rating = getattr(item, "rating", None)
    if rating is not None:
        print(f"Rating: {rating} ({item.n_votes} votes)")

    if len(item.genres) > 0:
        genres = ", ".join(item.genres)
        print(f"Genres: {genres}")

    if args.taglines and (len(item.taglines) > 0):
        taglines = "\n  ".join(item.taglines)
        print(f"Taglines:\n  {taglines}")


def main(argv: list[str] | None = None) -> None:
    parser = ArgumentParser(description="Retrieve data from the IMDb.")
    parser.add_argument("--version", action="version", version=__version__)

    command = parser.add_subparsers(metavar="command", dest="command")
    command.required = True

    get_parser = command.add_parser("get",
                                    help="retrieve information about an item")
    get_parser.add_argument("type", choices=["title"],
                            help="type of item to retrieve")
    get_parser.add_argument("imdb_id", type=int,
                            help="IMDb id of item to retrieve")
    get_parser.add_argument("--taglines", action="store_true",
                            help="include taglines")
    get_parser.set_defaults(func=get_item)

    arguments = parser.parse_args(argv if argv is not None else sys.argv[1:])
    arguments.func(arguments)
