import typing
import click
from flask import Flask, send_from_directory, request, g
import logging
import json
import os
from pheweb.serve.components.colocalization.finngen_common_data_model.genomics import Variant, Locus
from pheweb.serve.components.colocalization.cli import data_cli
from pheweb.serve.components.colocalization.model_db import ColocalizationDAO
from pheweb.serve.components.colocalization.view import colocalization, development
import atexit
import sys

class Jeeves():
     def __init__(self, colocalization):
         self.colocalization = colocalization

app = Flask(__name__, static_folder='static')
app.register_blueprint(colocalization)
app.register_blueprint(development)

@app.before_first_request
def setup_datastore():
     db_url = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/tmp.db')
     print("db_url : {0} ".format(db_url))
     app.jeeves = Jeeves(ColocalizationDAO(db_url))

app.cli.add_command(data_cli)
