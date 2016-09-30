########################################
#
########## micro doc tool - to provide online help

# sort of decorators to define the doc-* functions
#
# define-doc-category cat message
#    will define 3 functions
#    help-cat : user-oriented, to get help on that category
#    doc-cat  : devel-oriented, to add a line in that help
#    dac-cat-sep : same, but to insert separators

function define-doc-category () {
    category="$1"; shift
    # initialize docstring for this category
    varname=_doc_$category
    # initialize docstring with rest of arguments to define-doc-category
    assign="$varname=\"#################### $@\""
    eval "$assign"
    # define help-<> function
    defun="function help-$category() { echo -e \$$varname; }"
    eval "$defun"
    # define doc-<> function
    defun="function doc-$category() { -doc-helper $category \"\$@\"; }"
    eval "$defun"
    # define doc-<>-sep function
    defun="function doc-$category-sep() { -doc-helper-sep $category \"\$@\"; }"
    eval "$defun"
}

#
# augment-help-with cat
#
# will define a help alias that shows bash native help, then this category's help
#
function augment-help-with() {
    category=$1; shift
    defalias="alias help=\"echo '#################### Native bash help'; \\help; help-$category\""
    eval "$defalias"
}
    

### private stuff, not to be used from the outside
# -doc-helper <category> 
function -doc-helper () {
    category=$1; shift
    varname=_doc_$category
    fun=$1; shift;
    docstring="$*"
    [ "$docstring" == 'alias' ] && docstring=$(alias $fun)
    [ "$docstring" == 'function' ] && docstring=$(type $fun)
    length=$(wc -c <<< $fun)
    [ $length -ge 16 ] && docstring="\n\t\t$docstring"
    assign="$varname=\"${!varname}\n$fun\r\t\t$docstring\""
    eval "$assign"
}

function -doc-helper-sep() {
    varname=$1; shift
    contents="$@"; shift
    if [ -z "$contents" ] ; then
	assign="$varname=\"${!varname}\n---------------\""
    else
	assign="$varname=\"${!varname}\n============================== $contents\""
    fi
    eval "$assign"
} 

########################################
#
### do not document : a simple utility for the oai*.sh stubs
#
function define-main() {
    function main() {
	if [[ -z "$@" ]]; then
	    # help
	    echo subcommand expected
	    return
	fi
	subcommand="$1"; shift
	# accept only subcommands that match a function
	case $(type -t $subcommand) in
	    function)
		$subcommand "$@" ;;
	    *) 
		echo "$subcommand not a function - exiting" ;;
	esac
    }
}

