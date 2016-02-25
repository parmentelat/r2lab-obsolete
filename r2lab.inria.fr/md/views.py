import os.path
import re
import traceback

import markdown2

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.safestring import mark_safe

from django.conf import settings

# these markdown views require to be logged in
# xxx ugly hack for now
require_login_views = [ 'run.md' ]

# search for markdown input in the markdown/ subdir
# and code in the "code/" subdir
# xxx should be configurable
markdown_subdir = "markdown"
code_subdir = "code"

# accept names in .html or .md or without extension
def normalize(filename):
    """
    returns foo.md for an input that would be either foo, foo.md or foo.html
    """
    # do not support the .html extension now that we've migrated away from the old website
    #return filename.replace(".md", "").replace(".html", "") + ".md"
    return filename.replace(".md", "") + ".md"

metavar_re = re.compile("\A(?P<name>[\S_]+):\s*(?P<value>.*)\Z")


def match_meta(line):
    """
    for parsing the header that defines metavariables
    returns a tuple (name, value), or None 
    """
    # remove trailing newline
    match = metavar_re.match(line[:-1])
    if match:
        return match.group('name'), match.group('value')

def parse(markdown_file):
    """
    parse markdown content for metavars
    also deals with the << codediff file1 file2 >> tag
    returns a tuple metavars, markdown
    with the verbatim resolved
    """
    metavars = {}
    markdown = ""
    absolute_path = os.path.join(settings.BASE_DIR, markdown_subdir, markdown_file)
    with open(absolute_path, encoding='utf-8') as file:
        in_header = True
        for lineno, line in enumerate(file):
            if in_header:
                name_value_or_none = match_meta(line)
                if name_value_or_none:
                    name, value = name_value_or_none
                    metavars[name] = value
                    continue
                else:
                    in_header = False
            markdown += line
    markdown = resolve_codediff(markdown)
    return metavars, markdown

# could not figure out how to do this with the template engine system....
re_codediff = re.compile(r'<<\s*codediff\s+(?P<file1>\S+)(\s+(?P<file2>\S+))?\s*>>\s*\n')
def resolve_codediff(markdown):
    """
    looks for << codediff file1 file2 >> for inline inclusion and differences
    """
    end = 0
    resolved = ""
    for match in re_codediff.finditer(markdown):
        f1, f2 = match.group('file1'), match.group('file2')
        # bool(f1) is always True
        included1 = ""
        if f1:
            path1 = os.path.join(settings.BASE_DIR, code_subdir, f1)
            try:
                with open(path1) as input1:
                    included1 += input1.read()
            except:
                resolved += "codediff: mandatory included file {} not found".format(path1)
                traceback.print_exc()
        # this OTOH is optional
        included2 = ""
        if f2:
            path2 = os.path.join(settings.BASE_DIR, code_subdir, f2)
            try:
                with open(path2) as input2:
                    included2 += input2.read()
            except:
                resolved += "codediff: mandatory included file {} not found".format(path2)
                traceback.print_exc()
        resolved = resolved + markdown[end:match.start()]
        ### should compute diff
        # insert included text
        resolved += included2 if f2 else included1
        end = match.end()
    resolved = resolved + markdown[end:]
    return resolved
                      

@csrf_protect
def markdown_page(request, markdown_file, extra_metavars={}):
    """
    the view to render a URL that points at a markdown source
    e.g.
    if markdown_file is 'index' - or 'index.md', then we
     * look for the file markdown/index.md
     * extract any metavar in its header - they get passed to the template
     * and expand markdown to html - passed to the template as 'html_from_markdown'
    additional metavars can be passed along as well if needed
    """
    try:
        markdown_file = normalize(markdown_file)
        metavars, markdown = parse(markdown_file)
        ### fill in metavars: 'title', 'html_from_markdown',
        # and any other defined in header
        # convert and mark safe to prevent further escaping
        html = markdown2.markdown(markdown, extras=['markdown-in-html'])
        metavars['html_from_markdown'] = mark_safe(html)
        # set default for the 'title' metavar if not specified in header
        if 'title' not in metavars:
            metavars['title'] = markdown_file.replace(".md", "")
        # define the 'r2lab_context' metavar from current session
        r2lab_context = request.session.get('r2lab_context', {})
        if not r2lab_context and markdown_file in require_login_views:
                return HttpResponseRedirect("/index.md")
        metavars['r2lab_context'] = r2lab_context
        metavars.update(extra_metavars)
        return render(request, 'r2lab/r2lab.html', metavars)
    except Exception as e:
        previous_message = "<h1> Oops - could not render markdown_file = {}</h1>"\
            .format(markdown_file)
        if isinstance(e, FileNotFoundError):
            previous_message += str(e)
        else:
            import traceback
            stack = traceback.format_exc()
            print(stack)
            previous_message += "<pre>\n{}\n</pre>".format(stack)
        previous_message = mark_safe(previous_message)
        if settings.DEBUG:
            return HttpResponseNotFound(previous_message)
        else:
            return markdown_page(request, 'oops', {'previous_message': previous_message})
