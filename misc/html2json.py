#! /usr/bin/env python

import sys
from pathlib import Path

from lxml.html import fromstring as parse_html


infile = Path(sys.argv[1])
content = infile.read_text(encoding="utf-8")
root = parse_html(content)
payload = root.xpath("//script[@id='__NEXT_DATA__']/text()")[0]

outfile = infile.with_suffix(".json")
outfile.write_text(payload, encoding="utf-8")
