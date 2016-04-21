import os.path
import re
import traceback

import markdown2

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.safestring import mark_safe

from django.conf import settings
from r2lab.settings import logger

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
    markdown = resolve_codediffs(markdown)
    return metavars, markdown

# could not figure out how to do this with the template engine system....
re_codediff = re.compile(r'<<\s*codediff\s+(?P<id>\S+)\s+(?P<file1>\S+)(\s+(?P<file2>\S+))?\s*>>\s*\n')
def resolve_codediffs(markdown):
    """
    looks for << codediff id file1 file2 >> for inline inclusion and differences

    id is mandatory; it chould be unique identifier for that codediff, and
       will be used to attach ids to the DOM elements, and link them with the js code

    file1 is mandatory too; this is the 'previous' code, and only code in
       the first code for one series of experiments

    file2 is optional
       when provided, the diffs between file2 and file2 are highlighted
       otherwise, it's just file1 that is shown standalone

    this fetaures relies on 
      * diff.js from http://kpdecker.github.io/jsdiff/diff.js
      * related style
      * our own wrapper r2lab-diff.js     
    """
    end = 0
    resolved = ""
    for match in re_codediff.finditer(markdown):
        id, f1, f2 = match.group('id'), match.group('file1'), match.group('file2')
        resolved = resolved + markdown[end:match.start()]
        resolved += resolve_codediff(id, f1, f2)
        end = match.end()
    resolved = resolved + markdown[end:]
    return resolved
                      
def resolve_codediff(id, f1, f2, lang='python'):
    """
    the html code to generate for one codediff
    """

    # by design of re_codediff, bool(f1) is always True
    # while OTOH f2 is optional

    def get_included_file(f):
        if not f:
            return ""
        p = os.path.join(settings.BASE_DIR, code_subdir, f)
        try:
            with open(p) as i:
                return i.read()
        except:
            return "codediff: mandatory included file {} not found".format(p)
            
    i1, i2 = get_included_file(f1), get_included_file(f2)

    ########## one file : the simple case - simply use prism
    # for highlighting the code in python with line numbers
    if not f2:
        return \
'''<pre class="line-numbers">
<code class="language-{lang}">
{i1}
</code>
</pre>'''.format(**locals())

    ########## else : two files are provided
    resolved = ""
    # create 2 invisible <pres> for storing both contents
    resolved += '<pre id="{id}_a" style="display:none">{i1}</pre>\n'\
                .format(id=id, i1=i1)
    resolved += '<pre id="{id}_b" style="display:none">{i2}</pre>\n'\
                 .format(id=id, i2=i2)
    # create a <pre> to receive the result
    resolved += '<pre id="{id}_diff" class="r2lab-diff"></pre>\n'\
                .format(id=id)
    # arm a callback for when the document is fully loaded
    # this callback with populate the <pre> tag with elements
    # tagges either <code>, <ins> or <del> 
    resolved += '<script>$(function(){{r2lab_diff("{id}", "{lang}");}})</script>\n'\
                .format(id=id, lang=lang)
    
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
    logger.info("Rendering markdown page {}".format(markdown_file))
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
            stack = traceback.format_exc()
            logger.info("Storing stacktrace in previous_message - {}".format(stack))
            previous_message += "<pre>\n{}\n</pre>".format(stack)
        previous_message = mark_safe(previous_message)
        if settings.DEBUG:
            return HttpResponseNotFound(previous_message)
        else:
            return markdown_page(request, 'oops', {'previous_message': previous_message})
