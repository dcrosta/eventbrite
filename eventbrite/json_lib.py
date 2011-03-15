"""Abstracted away libraries used for JSON serialization"""

# Attempt to use built-in JSON library provided in Python 2.6+
try:
    import json
    builtin_json_lib = json
except ImportError:
    builtin_json_lib = None

# Attempt to use simplejson if provided if you would like to get faster JSON deserialization
# See http://pypi.python.org/pypi/simplejson/
try:
    import simplejson
    fast_json_lib = simplejson
except ImportError:
    fast_json_lib = None

chosen_json_lib = fast_json_lib or builtin_json_lib
if not chosen_json_lib:
    raise ImportError("No valid JSON library found")

dumps = chosen_json_lib.dumps
dump = chosen_json_lib.dump

loads = chosen_json_lib.loads
load = chosen_json_lib.load

