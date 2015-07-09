#!/usr/bin/env python3

import json

# I prefer writing python code rather than JSON natively
# plus, this might be the place to inject subindexes for the tutorials page some day

# none of these
meta = {
    'markdown' : { 'logos_height' : '28px'},
    '.' : { 'logos_height' : '28px'},
    '' : { 'logos_height' : '28px'},
    'logos_height' : '28px',
}

with open('markdown/meta.json', 'w') as output:
   json.dump(meta, output)

   
    
