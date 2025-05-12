
from flask.json.provider import DefaultJSONProvider
from datetime import datetime

class FGJSONEncoder(DefaultJSONProvider):
    def default(self, o):
        # Custom handling for datetime objects
        if isinstance(o, datetime):
            return o.isoformat()  # Convert to ISO format string
        # Call the parent class's method for other objects
        return super().default(o)