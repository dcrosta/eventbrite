try:
    import json
    builtin_json_lib = json
except ImportError:
    builtin_json_lib = None

try:
    import simplejson
    fast_json_lib = simplejson
except ImportError:
    fast_json_lib = None

chosen_json_lib = fast_json_lib or builtin_json_lib
if not chosen_json_lib:
    raise ImportError("PyEventbrite requires a JSON library")

dumps = chosen_json_lib.dumps
dump = chosen_json_lib.dump

loads = chosen_json_lib.loads
load = chosen_json_lib.load

