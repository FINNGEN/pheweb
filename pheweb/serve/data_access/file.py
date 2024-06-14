"""
This module provides Data Access Object (DAO) classes for managing
file path resources with customizable headers.  It includes classes
for handling standard file paths, JSON file paths, and compressed file
paths with Brotli encoding.

Classes:
    - FilePathResultDao: Base class for managing file path resources
      and their associated headers.  
    - ManhattanFileResultDao: Subclass for handling file results with
      a default JSON content type.
    - ManhattanCompressedResultDao: Subclass for handling compressed
      file results with Brotli encoding and JSON content type.
"""
from typing import Optional, Dict
from flask import send_file
from pheweb.file_utils import common_filepaths

class FilePathResultDao():
    """
    A Data Access Object (DAO) class to manage file path resources and
    their associated headers.

    :param file_template: A template string for the file path, default is None.
    :type file_template: str, an optional python format string to generate the
                         file path.
    :param headers: A dictionary of http headers to include in the response, 
                    default is None.
    :type headers: Optional[Dict[str, str]], optional
    """
    def __init__(self,
                 file_template : str=None,
                 headers: Optional[Dict[str,str]] = None):
        """
        Initialize the FilePathResultDao with a file template and headers.

        :param file_template: A template string for the file path, default is None.
        :type file_template: str, optional
        :param headers: A dictionary of headers to include in the response, default is None.
        :type headers: Optional[Dict[str, str]], optional
        """
        self.file_template = file_template
        self.headers=headers

    def get_resource(self,
                     key : str,
                     **parameters: str):
        """
        Retrieve the resource file based on the key and parameters provided.

        :param key: The key to identify the resource.
        :type key: str
        :param parameters: Additional parameters to format the file template.
        :type parameters: str
        :return: The response object containing the file and headers.
        :rtype: Response
        """
        if self.file_template is None:
            file_path=key
        else:
            file_path=self.file_template.format(key, **parameters)
        print(f"{file_path}")
        response = send_file(file_path)
        if self.headers is not None:
            for header_name,header_value in self.headers.items():
                response.headers[header_name] = header_value
        return response

class ManhattanFileResultDao(FilePathResultDao):
    """
    A subclass of FilePathResultDao specifically for handling file
    results with a default JSON content type.

    :param file_template: A template string for the file path, default is None.
    :type file_template: str, optional
    :param headers: A dictionary of headers to include in the response, default is None.
                    If not provided, it defaults to {'Content-Type': 'application/json'}.
    :type headers: Optional[Dict[str, str]], optional
    """
    def __init__(self,
                 file_template : str=None,
                 headers: Optional[Dict[str,str]] = None):
        """
        Initialize the ManhattanFileResultDao with a file template and
        headers. If no headers are provided, the default Content-Type
        is set to 'application/json'.

        :param file_template: A template string for the file path, default is None.
        :type file_template: str, optional
        :param headers: A dictionary of headers to include in the response, default is None.
                        If not provided, it defaults to {'Content-Type': 'application/json'}.
        :type headers: Optional[Dict[str, str]], optional
        """
        default_headers={ 'Content-Type' : 'application/json' }
        super().__init__(file_template,
                         default_headers if headers is None else headers)

class ManhattanCompressedResultDao(FilePathResultDao):
    """
    A subclass of FilePathResultDao specifically for handling
    compressed file results with Brotli encoding and a default JSON
    content type.

    :param file_template: A template string for the file path, default is "{}.br".
    :type file_template: str, optional
    :param headers: A dictionary of headers to include in the response, default is None.
                    If not provided, it defaults to 
                    {'Content-Encoding': 'br',
                     'Content-Type': 'application/json'}.
    :type headers: Optional[Dict[str, str]], optional
    """
    def __init__(self,
                 file_template : str = common_filepaths['compressed-manhattan'],
                 headers: Optional[Dict[str,str]] = None):
        default_headers={ 'Content-Encoding' : 'br' ,
                          'Content-Type' : 'application/json' }
        super().__init__(file_template,
                         default_headers if headers is None else headers)
