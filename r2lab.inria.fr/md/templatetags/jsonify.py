from django.template import Library
import json

def jsonify(object):
    return json.dumps(object)

register = Library()
register.filter('jsonify', jsonify)
