import os.path
import re
import traceback

import markdown2 as markdown_module

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.safestring import mark_safe

from django.conf import settings
from r2lab.settings import logger, sidecar_url

"""
Initially a simple view to translate a .md into html on the fly

with the reasonable addition of being able to define metavars at the beginning of the file
e.g.
title: the title for this page

Over time I've added features between << >> that suggest either
* the django templating system
* or markdown extensions

I'm sticking with the current approach for now though, because
all these things are quite fragile and using something entirely different
looks a little scary / time-consuming

"""

# pages that require login sohuld define the 'require_login' metavar

# search for markdown input in the markdown/ subdir
# and code in the "code/" subdir
# xxx should be configurable
markdown_subdir = "markdown"
code_subdir = "code"
templates_subdir = "templates"
include_paths = [ markdown_subdir, templates_subdir, code_subdir ]
    
# accept names in .html or .md or without extension
def normalize(filename):
    """
    returns foo.md for an input that would be either foo, foo.md or foo.html
    """
    # do not support the .html extension now that we've migrated away from the old website
    #return filename.replace(".md", "").replace(".html", "") + ".md"
    return filename.replace(".md", "") + ".md"

##########
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
    parse markdown content for
    * metavars
    * << tags >>
    returns a tuple metavars, markdown

    Supported tags

    << include file >>
       -> raw include 

    << codediff uniqueid file1 file2 >>
       -> a single visible <pre> (with 2 invisible ones) 
          that shows the differences between both files
          the uniqueid should indeed be unique

    << codeview uniqueid file1 [file2] >>
       -> a navpills <ul> with 'plain' and 'diff' options
          (or just one 'plain' if file1==file2)
          this asembles one <<include>> and one <<codediff>> items
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
    return metavars, markdown

def resolve_tags(input):
    # deal with supported tags
#    print("XXXXXXXXXXXXXXXXXXXX IN ", input)
    input = resolve_includes (input)
    input = resolve_codediffs(input)
    input = resolve_codeviews(input)
#    print("XXXXXXXXXXXXXXXXXXXX OUT ", input)
    return input

####################
# when searching for our tags,
# because this happens **after** markdown has triggered
# we can typically find:
# &lt;<  instead of << - and sometimes even <p>&lt;
# and
# >&gt; or >&gt;</p> instead of >>
def post_markdown(pattern):
    return pattern\
        .replace("<<", "(<p>)?(&lt;|<)(&lt;|<)")\
        .replace(">>", "(&gt;|>)(&gt;|>)(</p>)?")

re_include = re.compile(post_markdown(
    r'<<\s*include\s+(?P<file>\S+)\s*>>\s*\n'))
def resolve_includes(markdown):
    """
    Looks for << include file >> tags and resolves them
    """
    end = 0
    resolved = ""
    for match in re_include.finditer(markdown):
        filename = match.group('file')
        resolved = resolved + markdown[end:match.start()]
        resolved += implement_include(filename, "include")
        end = match.end()
    resolved = resolved + markdown[end:]
    # print("resolve_includes <- {} chars".format(len(resolved)))
    return resolved

re_codediff = re.compile(post_markdown(
    r'<<\s*codediff\s+(?P<id>\S+)\s+(?P<file1>\S+)(\s+(?P<file2>\S+))\s*>>\s*\n'))
def resolve_codediffs(markdown):
    """
    looks for << codediff id file1 file2 >> for inline inclusion and differences

    id should be unique identifier for that codediff, and
       will be used to attach ids to the DOM elements, and link them with the js code

    file1 and file2 are mandatory

    this features relies on 
      * diff.js from http://kpdecker.github.io/jsdiff/diff.js
      * related style
      * our own wrapper r2lab-diff.js     
    """
    end = 0
    resolved = ""
    for match in re_codediff.finditer(markdown):
        id, f1, f2 = match.group('id'), match.group('file1'), match.group('file2')
        resolved = resolved + markdown[end:match.start()]
        resolved += implement_codediff(id, f1, f2)
        end = match.end()
    resolved = resolved + markdown[end:]
    return resolved
                      
#
# THIS FOR NOW IS BROKEN
#
# the problem is that when we include a code file,
# it gets then fed into markdown - while it should be kept verbatim
#
# safely stay away from that for now...
# 

re_codeview = re.compile(post_markdown(
    r'<<\s*codeview\s+(?P<id>\S+)\s+(?P<file1>\S+)(\s+(?P<file2>\S+))?\s*>>\s*\n'))
def resolve_codeviews(markdown):
    """
    looks for << codeview id file1 [file2] >> and shows a nav-pills bar
    with 2 components 'plain' and 'diff'
    except if file2 is ommitted, in which case only the 'plain' button shows up

    in other words this essentially shows 
    the result of <<include>> and <<codediff>> in a togglable env

    """
    end = 0
    resolved = ""
    for match in re_codeview.finditer(markdown):
        id, f1, f2 = match.group('id'), match.group('file1'), match.group('file2')
        resolved = resolved + markdown[end:match.start()]
        resolved += implement_codeview(id, f1, f2)
        end = match.end()
    resolved = resolved + markdown[end:]
    return resolved
                      
####################
# could not figure out how to do this with the template engine system....
def implement_include(f, tag):
    if not f:
        return ""
    for path in include_paths:
        p = os.path.join(settings.BASE_DIR, path, f)
        try:
            # print("implement_include : trying", p)
            with open(p) as i:
                # print("implement_include: using p=", p)
                return i.read()
        except:
            pass
    return "**include file {} not found in {} tag**".format(f, tag)



def implement_codediff(id, f1, f2, lang='python'):
    """
    the html code to generate for one codediff
    """

    i1, i2 = implement_include(f1, 'codediff'), implement_include(f2, 'codediff')

    ########## two files must be provided
    result = ""
    # create 2 invisible <pres> for storing both contents
    result += '<pre id="{id}_a" style="display:none">{i1}</pre>\n'\
                .format(id=id, i1=i1)
    result += '<pre id="{id}_b" style="display:none">{i2}</pre>\n'\
                 .format(id=id, i2=i2)
    # create a <pre> to receive the result
    result += '<pre id="{id}_diff" class="r2lab-diff"></pre>\n'\
                .format(id=id)
    # arm a callback for when the document is fully loaded
    # this callback with populate the <pre> tag with elements
    # tagges either <code>, <ins> or <del> 
    result += '<script>$(function(){{r2lab_diff("{id}", "{lang}");}})</script>\n'\
                .format(id=id, lang=lang)
    
    return result


def implement_codeview(id, f1, f2, lang='python'):
    """
    the html code to generate for one codeview
    """

    result = ""

    # the part to start up with
    # only f1 : start with plain
    # f1 & f2 : start with diff
    if not f2:
        plain_header_class = 'active'
        diff_header_class  = ''
        plain_body_class   = 'in active'
        diff_body_class    = ''
        focus              = f1
    else:
        plain_header_class = ''
        diff_header_class  = 'active'
        plain_body_class   = ''
        diff_body_class    = 'in active'
        focus              = f2

    ########## the nav pills
    result += """
<ul class="nav nav-pills">
<li class="{plain_header_class}"><a href="#view-{id}-plain">{focus}</a></li>
<li class="navbar-right"><a class="default-click" href="/code/{focus}" download target="_blank">
<span class='fa fa-cloud-download'></span> {focus}</a></li>
""".format(**locals())
    if f2:
        result += """
<li class="{diff_header_class}"><a href="#view-{id}-diff">{f1} ➾ {f2}</a></li>
""".format(**locals())
    result += "</ul>"

    ########## the contents
    result += """
<div class="tab-content" markdown="0">
<div id="view-{id}-plain" class="tab-pane fade {plain_body_class}" markdown="0">
""".format(**locals())

    if not f2:
        result += "<pre>\n"
        result += implement_include(f1, "codeview")
        result += "</pre>\n"
    else:
        result += implement_codediff('plain-'+id, f2, f2)
        

    result += """
</pre>
</div>""".format(**locals())

    if f2:
        result += """<div id="view-{id}-diff" class="tab-pane fade {diff_body_class}">"""\
                              .format(**locals())
        result += implement_codediff('diff-' + id, f1, f2)
        result += "</div>".format(**locals())

    result += "</div><!-- pills targets-->"
    return result


####################
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
        ### fill in metavars: 'title', 'html_from_markdown',
        # and any other defined in header
        metavars, markdown = parse(markdown_file)
        # convert markdown
        html = markdown_module.markdown(markdown, extras=['markdown-in-html'])
        # handle our tags
        html = resolve_tags(html)
        # and mark safe to prevent further escaping
        metavars['html_from_markdown'] = mark_safe(html)
        # set default for the 'title' metavar if not specified in header
        if 'title' not in metavars:
            metavars['title'] = markdown_file.replace(".md", "")
        # define the 'r2lab_context' metavar from current session
        r2lab_context = request.session.get('r2lab_context', {})
        if not r2lab_context and 'require_login' in metavars:
                return HttpResponseRedirect("/index.md")
        metavars['r2lab_context'] = r2lab_context
        metavars['sidecar_url'] = sidecar_url
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
