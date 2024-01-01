#  Copyright 2009-2017 Davide Alberani <da@erlug.linux.it>
#            2009-2024 H. Turgut Uyar <uyar@tekir.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from types import MappingProxyType
from typing import Mapping


ARTICLES: Mapping[str, frozenset[str]] = MappingProxyType({
    "DE": frozenset({"das", "der", "die"}),
    "EN": frozenset({"a", "an", "the"}),
    "ES": frozenset({"el", "la", "las", "los"}),
    "FR": frozenset({"l'", "la", "le", "les"}),
    "IT": frozenset({"gli", "i", "il", "l'", "la", "le", "lo"}),
    "PT": frozenset({"a", "as", "o", "os"}),
    "SV": frozenset({"de", "den", "det"}),
})

MAIN_LANGUAGE: Mapping[str, frozenset[str]] = MappingProxyType({
    "DE": frozenset({"AT", "CH", "DDDE", "DE", "LI", "XWG"}),
    "EN": frozenset({"AG", "AU", "BB", "BS", "BW", "BZ", "CA", "FJ", "FM",
                     "GB", "GD", "GH", "GM", "GY", "IE", "JM", "KE", "KI",
                     "KN", "LC", "LR", "LS", "MT", "NA", "NG", "NZ", "SB",
                     "SL", "TT", "UG", "US", "VC", "ZA", "ZM", "ZW"}),
    "ES": frozenset({"AR", "BO", "CL", "CO", "CR", "CU", "DO", "EC", "ES",
                     "GQ", "GT", "HN", "MX", "NI", "PA", "PY", "PE", "SV",
                     "UY", "VE"}),
    "FR": frozenset({"BF", "BI", "BJ", "CD", "CF", "CG", "CI", "CM", "DM",
                     "FR", "GA", "GN", "HT", "KM", "LU", "MC", "MG", "ML",
                     "NE", "SN", "TD", "TG"}),
    "IT": frozenset({"IT", "SM", "VA"}),
    "PT": frozenset({"AO", "BR", "CV", "GW", "MZ", "PT", "ST"}),
    "SV": frozenset({"SE"}),
})

COUNTRY_LANGUAGE: Mapping[str, str] = MappingProxyType(
    {country: lang
     for lang in MAIN_LANGUAGE
     for country in MAIN_LANGUAGE[lang]}
)
