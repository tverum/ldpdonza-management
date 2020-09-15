from .common import *
try:
    from .local import *
except ImportError:
    import sys
    sys.path.insert('/home/ubuntu/.local/lib/python3.6/site-packages/')
    from .production import *