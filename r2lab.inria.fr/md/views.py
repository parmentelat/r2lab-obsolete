import os.path
import re

from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader

from .models import Page

import markdown2
from django.utils.safestring import mark_safe

########## xxx dummy index - based on the db but we don't need the db ...
def index(request):
    pages = Page.objects.order_by('markdown_file')
    return HttpResponse("not sure this page is useful")
#    return render(request, 'r2lab/index.html', locals())

# accept names in .html or .md or without extension
def normalize(filename):
    return filename.replace(".md", "").replace(".html", "") + ".md"

# search for markdown input in the markdown/ subdir
# xxx should be configurable
markdown_subdir = "markdown"

metavar_re = re.compile("\A(?P<name>[\S_]+):\s*(?P<value>.*)\Z")

def match_meta(line):
    """
    return a tuple (name, value), or None 
    """
    # remove trailing newline
    match = metavar_re.match(line[:-1])
    if match:
#        print("MATCH")
        return match.group('name'), match.group('value')

# parse markdown content for metavars
def parse(markdown_file):
    metavars = {}
    markdown = ""
    with open(os.path.join(markdown_subdir, markdown_file), encoding='utf-8') as file:
        in_header = True
        for lineno, line in enumerate(file):
#            if lineno <= 10:
#                print("{}:{}: in_header={} - line={}".format(markdown_file, lineno+1, in_header, line))
            if in_header:
                name_value_or_none = match_meta(line)
                if name_value_or_none:
                    name, value = name_value_or_none
                    metavars[name] = value
                    continue
                else:
                    in_header = False
            markdown += line
    return metavars, markdown

def show(request, markdown_file):
    try:
        markdown_file = normalize(markdown_file)
        metavars, markdown = parse(markdown_file)
        ### fill in metavars: 'title', 'html_from_markdown', and any other defined in header
        # convert and mark safe to prevent further escaping
        html = markdown2.markdown(markdown, extras=['markdown-in-html'])
        metavars['html_from_markdown'] = mark_safe(html)
        if 'title' not in metavars:
            metavars['title'] = markdown_file.replace(".md", "")
        return render(request, 'r2lab/r2lab.html', metavars)
    except:
        import traceback
        exc = traceback.format_exc()
        return HttpResponse("Could not render markdown_file = {} <pre>\n{}\n</pre>".format(markdown_file, exc))
