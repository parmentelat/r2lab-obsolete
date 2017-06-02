// -*- js-indent-level:4 -*-

/* for eslint */
/*global $*/
/*global JsDiff*/   /* from diff.min.js */

/*exported r2lab_diff*/

"use strict";

// protocol is as follows
// each codediff is assigned an id by in the markdown source
// together with the mandatatory 'a' file, and the optional 'b' file
// the python code will create 2 elements named <id>_a and <id>_b
// that hold the codes for the a and b versions of that code
// python also creates an empty element named <id>_diff
// 
// the r2lab_diff function is invoked only when 2 files are provided
// it is charge of locating both codes, invoking jsdiff, and
// populating the <id>_diff element (expected to be a <pre>)
// with elements <ins>, <del> or <code>
//
// see markdown/views.md to see how this is used to create the tuto pages

function r2lab_diff(id, lang) {
    let a      = document.getElementById(id + '_a');
    let b      = document.getElementById(id + '_b');
    let diff = document.getElementById(id + '_diff');
    let style = 'diffLines'; // also available are diffChars and diffWords
    let jsdiff = JsDiff[style](a.textContent, b.textContent);

    let fragment = document.createDocumentFragment();
    for (let i=0; i < jsdiff.length; i++) {
	if (jsdiff[i].added && jsdiff[i + 1] && jsdiff[i + 1].removed) {
	    let swap = jsdiff[i];
	    jsdiff[i] = jsdiff[i + 1];
	    jsdiff[i + 1] = swap;
	}
	let type =   (jsdiff[i].removed) ? 'del'
	    : (jsdiff[i].added) ? 'ins' : 'code';
	let node = document.createElement(type);
	node.appendChild(document.createTextNode(jsdiff[i].value));
	fragment.appendChild(node);
	// passing e.g. lang='python' will enable prism
	// at least on the <code> tag
	if (lang) $(node).addClass('language-' + lang);
    }
    diff.textContent = '';
    diff.appendChild(fragment);
}
