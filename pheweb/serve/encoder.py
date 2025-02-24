from flask import Flask, jsonify, json
import numpy as np
from json import JSONEncoder

class FGJSONEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def default(self, o):
        try:
            rep = o.json_rep()
        except Exception:
            pass
        else:
            return rep
        # Handle NaN values deeply by traversing the data structure
        return self._convert_nans(o)

    def _convert_nans(self, obj):
        """Recursively replace NaN values with None in nested structures."""
        if isinstance(obj, float) and (np.isnan(obj) or obj != obj):  # NaN check
            return None
        elif isinstance(obj, dict):  # Traverse dictionaries
            return {key: self._convert_nans(value) for key, value in obj.items()}
        elif isinstance(obj, list):  # Traverse lists
            return [self._convert_nans(item) for item in obj]
        elif isinstance(obj, tuple):  # Handle tuples (convert to lists)
            return tuple(self._convert_nans(item) for item in obj)
        return obj  # Return unchanged if not NaN or a nested structure

