#!/usr/bin/env python3

# computes an index file in markdown/index.md from ./index.md with all the other md files referenced

import sys
import os
from glob import glob

source = "index.md"
output_dir = "markdown"

index_line_format = " * [{base}]({base}.html)\n"

def main():
    if not os.path.isfile(source):
        print("Source not found {}".format(source))
        sys.exit(1)

    output = os.path.join(output_dir, source)
    with open(output, 'w') as result:
        with open(source) as input:
            result.write(input.read())
        for other in glob("{}/*.md".format(output_dir)):
            base = os.path.basename(other).replace(".md", "")
            # skip index from the index...
            if base == source:
                continue
            result.write(index_line_format.format(base=base))
    print("(Over)wrote {}".format(output))

main()
