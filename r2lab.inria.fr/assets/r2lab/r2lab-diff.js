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
    var a      = document.getElementById(id + '_a');
    var b      = document.getElementById(id + '_b');
    var diff = document.getElementById(id + '_diff');
    var style = 'diffLines'; // also available are diffChars and diffWords
    var jsdiff = JsDiff[style](a.textContent, b.textContent);

    var fragment = document.createDocumentFragment();
    for (var i=0; i < jsdiff.length; i++) {
	if (jsdiff[i].added && jsdiff[i + 1] && jsdiff[i + 1].removed) {
	    var swap = jsdiff[i];
	    jsdiff[i] = jsdiff[i + 1];
	    jsdiff[i + 1] = swap;
	}
	var type =   (jsdiff[i].removed) ? 'del'
	    : (jsdiff[i].added) ? 'ins' : 'code';
	var node = document.createElement(type);
	node.appendChild(document.createTextNode(jsdiff[i].value));
	fragment.appendChild(node);
	// passing e.g. lang='python' will enable prism
	// at least on the <code> tag
	if (lang) $(node).addClass('language-' + lang);
    }
    diff.textContent = '';
    diff.appendChild(fragment);
}
