import json
import re

from flask import Blueprint, current_app as app, g, request
from pheweb.serve.components.colocalization.finngen_common_data_model.genomics import Variant, Locus
from pheweb.serve.components.colocalization.model import CausalVariantVector, SearchSummary, SearchResults, PhenotypeList, ColocalizationDB

colocalization = Blueprint('colocalization', __name__)
development = Blueprint('development', __name__)

@colocalization.route('/api/colocalization', methods=["GET"])
def get_phenotype():
    app_dao = app.jeeves.colocalization
    if app_dao:
        flags = {}
        phenotypes = app_dao.get_phenotype(flags=flags)
    else:
        phenotypes = PhenotypeList([])
    return json.dumps(phenotypes.json_rep())

@colocalization.route('/api/colocalization/<string:phenotype>/<string:locus>', methods=["GET"])
def get_locus(phenotype: str,
              locus: str):
    app_dao = app.jeeves.colocalization
    if app_dao:
        flags = request.args.to_dict()
        result = app_dao.get_locus(phenotype=phenotype,
                                   region = Locus.from_str(locus),
                                   flags=flags)
    else:
        result = SearchResults(colocalizations=[],
                               count=0)
    return json.dumps(result.json_rep(), default=lambda o: None)


@colocalization.route('/api/colocalization/<string:phenotype>/<string:locus>/summary', methods=["GET"])
def do_summary_colocalization(phenotype: str,
                              locus : str):
  app_dao = app.jeeves.colocalization
  print(app_dao)
  if app_dao:
      flags = request.args.to_dict()
      summary = app_dao.get_locus_summary(phenotype=phenotype,
                                          region = Locus.from_str(locus),
                                          flags=flags)
  else:
      summary = SearchSummary(count=0,
                              unique_phenotype2 = 0,
                              unique_tissue2 = 0)
  return json.dumps(summary.json_rep(), default=lambda o: None)


@colocalization.route('/api/colocalization/<string:phenotype>/lz-results/', methods=["GET"])
def get_locuszoom_results(phenotype: str):
    filter_param = request.args.get('filter')
    groups = re.match(r"analysis in 3 and chromosome in +'(.+?)' and position ge ([0-9]+) and position le ([0-9]+)", filter_param).groups()
    chromosome, start, stop = int(groups[0]), int(groups[1]), int(groups[2])
    flags = request.args.to_dict()
    locus=Locus(chromosome=chromosome,
                start=start,
                stop=stop)
    return get_locuszoom(phenotype, str(locus))

@colocalization.route('/api/colocalization/<string:phenotype>/<string:locus>/finemapping', methods=["GET"])
def get_locuszoom(phenotype: str,
                  locus : str,
                  flags = None):
    app_dao = app.jeeves.colocalization
    if app_dao:
        flags = flags or request.args.to_dict()
        locus = Locus.from_str(locus)
        variants = app_dao.get_locuszoom(phenotype=phenotype, region = locus, flags=flags)
        variants = {k: v.json_rep() for k, v in variants.items()} if variants else []
    else:
        variants = {}
    return json.dumps(variants)
