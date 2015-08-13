#!/usr/bin/env python3

import json
import glob


# I prefer writing python code rather than JSON natively
# plus, this might be the place to inject subindexes for the tutorials page some day

hard_wired_meta = {
   # '*' means this is visible to all input files unless overridden
   # in a more specific location
   '*' : { 'logos_height': '18px'}
   }

title_header = 'title:'

def tuto_contents(md):
   """
   input is a markdown filename
   which is expected to define title:
   output is a tuple (name, title)
   with name having its '.md' removed
   and title being said title
   """
   basename = md.replace('.md', '')
   title = 'No title set'
   with open(md) as input:
      for line in input.readlines():
         if line.startswith(title_header):
            title = line[len(title_header):].strip()
   return (basename, title)

def main():

   meta = hard_wired_meta
   
   # enrich it
   # get the list of tutorials
   tuto_files = glob.glob("tuto*.md")
   # make sure the '*' key is present
   wildcard = meta.setdefault('*', None)
   wildcard['tutos'] = [ tuto_contents(tf) for tf in tuto_files]

   # save
   with open('markdown/meta.json', 'w') as output:
      json.dump(meta, output)

   
if __name__ == '__main__':
   main()
