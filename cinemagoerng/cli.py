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

from argparse import ArgumentParser, Namespace

from cinemagoerng import __version__, web


def get_item(args: Namespace) -> None:
    if args.type == "title":
        item = web.get_title(args.imdb_id)
    if args.taglines:
        item = web.update_title(item, infoset="taglines")
    print(f"Title: {item.title} ({item.type_name})")
    print(f"Year: {item.year}")
    if hasattr(item, "runtime"):
        print(f"Runtime: {item.runtime} min")
    print(f"Genres: {', '.join(item.genres)}")
    if args.taglines and (len(item.taglines) > 0):
        taglines = '\n  '.join(item.taglines)
        print(f"Taglines:\n  {taglines}")


def main() -> None:
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

    arguments = parser.parse_args()
    arguments.func(arguments)
