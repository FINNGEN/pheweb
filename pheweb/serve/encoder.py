
from flask.json.provider import DefaultJSONProvider

class FGJSONEncoder(DefaultJSONProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def default(self,o):
        try:
            rep =o.json_rep()
        except Exception as e:
            pass
        else:
            return rep
        return DefaultJSONProvider.default(self, o)
