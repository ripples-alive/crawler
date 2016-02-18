from underscore.underscore import _
from ctf import *
import json

def handle(data, *a):
    return _(data['courses']).map(lambda x, *a: (data['school'], x['name']))

data = json.load(open('courses.json'))
result = _(data).chain()
    .pluck('response')
    .map(lambda x, *a: json.loads(x))
    .map(handle)
    .flatten(True)
    .map(lambda x, *a: '\t'.join(x))
    .value()

print result
