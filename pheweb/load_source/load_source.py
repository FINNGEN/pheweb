from importlib import import_module
import importlib.util

def load_source(modname, filename):
     loader = importlib.machinery.SourceFileLoader(modname, filename)
     spec = importlib.util.spec_from_file_location(modname, filename, loader=loader)
     module = importlib.util.module_from_spec(spec)
     # The module is always executed and not cached in sys.modules.
     # Uncomment the following line to cache the module.
     # sys.modules[module.__name__] = module
     loader.exec_module(module)
     return module

