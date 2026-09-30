import abc
import importlib
import inspect
import unittest
from pathlib import Path

import pheweb.serve as serve_package


def _iter_module_names(package):
    """Yield every dotted module name under `package`, walking the filesystem
    directly rather than using pkgutil: several subpackages here (autocomplete,
    health, suplementary, configuration) have no __init__.py, and pkgutil's
    package discovery silently skips those implicit namespace packages."""
    root = Path(package.__file__).parent
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root)
        parts = rel.parts[:-1] if path.name == "__init__.py" else rel.with_suffix("").parts
        yield ".".join([package.__name__, *parts])


def discover_dao_classes():
    """This discovers all concrete DAOs, which are child classes of abc.ABC
    but not direct subclasses, which are the abstract interfaces.
    """
    # db.py and one of the colocalization modules import each other; importing
    # db.py first avoids hitting that circular import mid-walk.
    importlib.import_module("pheweb.serve.data_access.db")

    classes = {}
    for module_name in _iter_module_names(serve_package):
        try:
            module = importlib.import_module(module_name)
        except Exception:
            # optional dependency not installed, or an unrelated broken/
            # config-dependent module (e.g. server.py needs a real pheno
            # list) -- neither is this test's concern.
            continue
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__:
                continue  # only count classes where they're actually defined
            if not issubclass(cls, abc.ABC) or cls is abc.ABC:
                continue
            if abc.ABC in cls.__bases__:
                continue  # this is the interface itself, not an implementation
            classes[name] = cls
    return classes


DAO_CLASSES = discover_dao_classes()


class TestDAOClassesImplementAbstractInterfaces(unittest.TestCase):
    """This tries to create new instances of all discovered non-abstract DAO classes"""

    def test_dao_classes_fully_implement_their_abstract_interface(self):
        self.assertGreater(len(DAO_CLASSES), 10, "DAO discovery found suspiciously few classes")
        for name, cls in DAO_CLASSES.items():
            with self.subTest(cls=name):
                try:
                    cls.__new__(cls)
                except TypeError as e:
                    self.fail(f"{name} does not fully implement its abstract interface: {e}")
