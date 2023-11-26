# Copyright (C) 2023 H. Turgut Uyar <uyar@tekir.org>
#
# Piculet is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Piculet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Piculet.  If not, see <http://www.gnu.org/licenses/>.


def parse_type_id(value: str) -> str:
    first, *rest = value.split(" ")
    return "".join([first.lower()] + rest)


def parse_runtime(value: str) -> int:
    return int(value.replace(" min", ""))


def parse_vote_count(value: str) -> int:
    return int(value[1:-1].replace(",", ""))   # remove parens around value
