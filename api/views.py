# Create your views here.
import inspect

from api import handlers
from utils.utils import render_to

@render_to("api/docs.html")
def doc(request):
    a = inspect.getmembers(handlers)
    documentation = []
    for c in a:
        if inspect.isclass(c[1]):
            if c[1].__module__ == 'api.handlers':
                #print c[1].__doc__
                ms = inspect.getmembers(c[1])
                for m in ms:
                    if inspect.ismethod(m[1]) and m[1].__name__=="read":
#                        print m[1].__doc__
                        documentation.append({'main':c[1].__doc__, "read":m[1].__doc__})
    return locals()
