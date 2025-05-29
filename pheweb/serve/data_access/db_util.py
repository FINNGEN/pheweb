import importlib.machinery
import typing
import abc
import pymysql
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)

def load_mysql_authentication(obj : object, authentication_file : str) -> object:
    loader = importlib.machinery.SourceFileLoader('mysql_auth', authentication_file)
    auth_module = loader.load_module()
    obj.user = getattr(auth_module, 'mysql')['user']
    obj.password = getattr(auth_module, 'mysql')['password']
    obj.host = getattr(auth_module, 'mysql')['host']
    obj.db = getattr(auth_module, "mysql")['db']
    obj.port = getattr(auth_module, "mysql").get('port', None)
    obj.release = getattr(auth_module, "mysql").get('release', None)
    return obj

def create_connection(obj : object) -> object:
    kwargs = {'port': int(obj.port) } if obj.port is not None else {}
    connection = pymysql.connect(
            host=obj.host,
            user=obj.user,
            password=obj.password,
            db=obj.db,
            **kwargs
        )
    return connection

class MysqlDAO:
    def __init__(self, authentication_file : str):
        logger.info(f"authentication_file:'{authentication_file}'")
        self.authentication_file = authentication_file
        load_mysql_authentication(self,
                                  self.authentication_file)
    
    def get_connection(self):
        return create_connection(self)

    @staticmethod
    def format_cpra_row(r : typing.Dict[str, typing.Dict[str, typing.Union[str,None,int,float]]]) -> str:
        variant = Variant(chromosome=data['chromosome'],
                          position = data['position'],
                          reference = data['reference'],
                          alternate = data['alternate'])
        return str(variant)
