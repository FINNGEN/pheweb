from flask import Blueprint, current_app as app, request, jsonify, abort
from itertools import chain
import requests
from pheweb.serve.components.model import ComponentCheck, ComponentStatus, ComponentDTO, CompositeCheck
import json
import logging
import random

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.ERROR)

configuration = Blueprint("configuration", __name__)

@configuration.route("/api/configuration", methods=["GET"])
def get_configuration():
    # this is the simplest configuration can be improved upon
    return dict(dbs_fact=app.jeeves.dbs_fact is None,
                annotation=app.jeeves.annotation_dao is None,
                gnomad=app.jeeves.gnomad_dao is None,
                lof=app.jeeves.lof_dao is None,
                result=app.jeeves.result_dao is None,
                ukbb=app.jeeves.ukbb_dao is None,
                ukbb_matrix=app.jeeves.ukbb_matrixdao is None,
                coding=app.jeeves.coding_dao is None,
                finemapping=app.jeeves.finemapping_dao is None,
                knownhits=app.jeeves.knownhits_dao is None,
                autoreporting=app.jeeves.autoreporting_dao is None,
                colocalization=app.jeeves.colocalization is None,
                variant_phenotype=app.jeeves.variant_phenotype is None,
                autocompleter=app.jeeves.autocompleter_dao is None,
                pqtl_colocalization=app.jeeves.pqtl_colocalization is None,
                health=app.jeeves.health_dao is None,
    )

# Helper methods
def get_random_phenocode():
    from pheweb.serve.server import active_phenolist
    phenotype=random.choice(active_phenolist())
    phenocode=phenotype["phenocode"]
    return phenocode

def get_random_variant():
    from pheweb.serve.server import api_pheno
    phenocode=get_random_phenocode()
    variant=random.choice(api_pheno(phenocode)["unbinned_variants"])
    return variant

def get_random_gene():
    from pheweb.utils import get_gene_tuples
    gene_tuple=next(chain((x for x in get_gene_tuples() if random.randint(1, 100) == 1),  get_gene_tuples()))
    return gene_tuple[-1]

def get_random_region():
    variant=get_random_variant()
    chromosome=variant['chrom']
    position=variant['pos']
    width=200 * 1000
    start_position = max(0, position - width)
    end_position = position + width
    return dict(chromosome=chromosome,
                start_position=start_position,
                end_position=end_position)
    

# Endpoint checks
class HomePageCheck(ComponentCheck):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import homepage
        response=homepage("")
        return ComponentStatus(response.status_code == 200, [ f"status {response.status_code}"])    

class AutoreportCheck(ComponentCheck):
    def get_status(self,) -> ComponentStatus:
        dao = app.jeeves.autoreporting_dao
        if dao is None:
            return ComponentStatus(True, ["autoreporting not configured"])
        else:
            from pheweb.serve.server import phenolist
            from pheweb.serve.server import autoreport
            phenocode=get_random_phenocode()            
            response=autoreport(phenocode)
            return ComponentStatus(response.status_code == 200 and response.get_json() is not None, [])

class AutoreportVariantsCheck(ComponentCheck):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import autoreport_variants
        dao = app.jeeves.autoreporting_dao
        if dao is None:
            return ComponentStatus(True, ["autoreporting not configured"])
        else:
            variant=get_random_variant()
            locus_id=f"{variant['chrom']}:{variant['pos']}:{variant['ref']}:{variant['alt']}"
            phenocode=get_random_phenocode()
            response=autoreport_variants(phenocode,locus_id)
            return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])

class PhenocodeCheck(ComponentCheck):
    
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import pheno
        phenocode=get_random_phenocode()
        response=pheno(phenocode) 
        return ComponentStatus(response.status_code == 200 and response.get_json() is not None, [ f"status {response.status_code}"])    

class PhenolistCheck(ComponentCheck):
    
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import phenolist
        response=phenolist()
        return ComponentStatus(response.status_code == 200 and response.get_json() is not None, [ f"status {response.status_code}"])
    
class VariantCheck(ComponentCheck):
    # def api_variant(query):
    def get_status(self,) -> ComponentStatus:
         from pheweb.serve.server import api_variant
         variant=get_random_variant()
         query=f"{variant['chrom']}:{variant['pos']}:{variant['ref']}:{variant['alt']}"
         response=api_variant(query)
         return ComponentStatus(response is not None , [ ])

class VariantPhenoCheck(ComponentCheck):
    # def api_variant_pheno(query, phenocode):
    def get_status(self,) -> ComponentStatus:
         from pheweb.serve.server import api_variant_pheno
         variant=get_random_variant()
         query=f"{variant['chrom']}:{variant['pos']}:{variant['ref']}:{variant['alt']}"
         phenocode=get_random_phenocode()
         response=api_variant_pheno(query, phenocode)
         return ComponentStatus(response is not None , [ ])

class PhenoCheck(ComponentCheck):
    
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_pheno
        phenocode=get_random_phenocode()
        response=api_pheno(phenocode)
        return ComponentStatus(response is not None , [ ])    

class GenePhenotypesCheck(ComponentCheck):
    
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_gene_phenotypes
        genename=get_random_gene()
        response=api_gene_phenotypes(genename)
        return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    
    
class GeneFunctionalVariantsCheck(ComponentCheck):
    # def api_gene_functional_variants(gene):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_gene_functional_variants
        genename=get_random_gene()
        response=api_gene_functional_variants(genename)
        return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])
    
class LofCheck(ComponentCheck):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_lof
        dao = app.jeeves.lof_dao
        if dao is None:
            return ComponentStatus(True, ["loss of function not configured"])
        else:
            response=api_lof()
            return ComponentStatus(response.status_code == 200 and response.get_json() is not None, [ f"status {response.status_code}"])

class LOFGeneCheck(ComponentCheck):
    # def api_lof_gene(gene):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_lof_gene
        genename=get_random_gene()
        response=api_lof_gene(genename)
        return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    
        
class TopHitCheck(ComponentCheck):
    # def api_top_hits():
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_top_hits
        response=api_top_hits()
        return ComponentStatus(response.status_code == 200 and response.get_json() is not None, [ f"status {response.status_code}"])

class DownloadTopHitCheck(ComponentCheck):
    # def download_top_hits():
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import download_top_hits
        response=download_top_hits()
        return ComponentStatus(response.status_code == 200 and response.get_json() is not None, [ f"status {response.status_code}"])

class ApiPhenoQQCheck(ComponentCheck):
    # def api_pheno_qq(phenocode):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_pheno_qq
        phenocode=get_random_phenocode()
        response=api_pheno_qq(phenocode) 
        return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    
    
    
class UKBBNSCheck(ComponentCheck):
    # def ukbb_ns(phenocode):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import ukbb_ns
        phenocode=get_random_phenocode()
        response=ukbb_ns(phenocode) 
        return ComponentStatus(response is not None, [ ])    
    
class RegionPageCheck(ComponentCheck):
    # def api_region_page(phenocode, region):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_region_page
        phenocode=get_random_phenocode()
        region=get_random_region()
        region=f"""{region["chromosome"]}:{region["start_position"]}-{region["end_position"]}"""
        response=api_region_page(phenocode, region)
        return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    

class RegionCheck(ComponentCheck):
    # def api_region(phenocode):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_region_page
        phenocode=get_random_phenocode()
        response=api_region_page(phenocode)
        return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    


class ApiConditionalRegionCheck(ComponentCheck):
    # def api_conditional_region(phenocode, filter_param : Optional[str] = None):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_conditional_region
        dao = app.jeeves.finemapping_dao
        if dao is None:
            return ComponentStatus(True, ["finemapping not configured"])
        else:
            region=get_random_region()
            filter_param=f"""analysis in 3 and chromosome in '{region["chromosome"]}' and position ge {region["start_position"]} and position le {region["end_position"]}"""
            response=api_conditional_region(phenocode, filter_param)
            return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    

class ApiFinemapedRegionCheck(ComponentCheck):
    # def api_finemapped_region(phenocode : str, filter_param : Optional[str] = None):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_finemapped_region
        dao = app.jeeves.finemapping_dao
        if dao is None:
            return ComponentStatus(True, ["finemapping not configured"])
        else:
            region=get_random_region()
            filter_param=f"""analysis in 3 and chromosome in '{region["chromosome"]}' and position ge {region["start_position"]} and position le {region["end_position"]}"""
            response=api_finemapped_region(phenocode, filter_param)
            return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    

class GenePQTLColocalizationCheck(ComponentCheck):
    # def api_gene_pqtl_colocalization(genename):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import api_gene_pqtl_colocalization
        dao=app.jeeves.pqtl_colocalization
        if dao is None:
            return ComponentStatus(True, ["autoreporting not configured"])
        else:
            genename=get_random_gene()
            response=api_gene_pqtl_colocalization(genename)
            return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    

class GeneReportCheck(ComponentCheck):
    # def gene_report(genename):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import gene_report
        genename=get_random_gene()
        response=gene_report(genename)
        return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    
        
class DrugsCheck(ComponentCheck):
    # def drugs(genename):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import drugs
        genename=get_random_gene()
        response=drugs(genename)
        return ComponentStatus(response.status_code == 200 , [ f"status {response.status_code}"])    

class NCBICheck(ComponentCheck):
    # def ncbi(endpoint):
    def get_status(self,) -> ComponentStatus:
        from pheweb.serve.server import ncbi
        region=get_random_region()
        endpoint="esearch.fcgi"
        args=dict(db='clinvar',
                  retmode='json',
                  term=f"""{region["chromosome"]}[chr]{region["start_position"]}:{region["end_position"]}[chrpos]"clinsig pathogenic"[Properties]""",
                  retmax=500)
        response=ncbi(endpoint, args)
        return ComponentStatus(response is not None, [])
        
# TODO
# 1. configuration
# 2. filter
# 3. check all optional
# 4. unit test

all_checks=[
    HomePageCheck(),
    AutoreportCheck(),
    AutoreportVariantsCheck(),
    PhenocodeCheck(),
    PhenolistCheck(),
    VariantCheck(),    
    VariantPhenoCheck(),
    PhenoCheck(),
    GenePhenotypesCheck(),
    GeneFunctionalVariantsCheck(),
    LofCheck(),
    LOFGeneCheck(),
    TopHitCheck(),
    DownloadTopHitCheck(),
    ApiPhenoQQCheck(),
    UKBBNSCheck(),
    RegionPageCheck(),
    RegionCheck(),
    ApiConditionalRegionCheck(),
    ApiFinemapedRegionCheck(),
    GenePQTLColocalizationCheck(),
    GeneReportCheck(),
    DrugsCheck(),
    NCBICheck(),
]

class ConfigurationCheck(CompositeCheck):

    def __init__(self, allowed_checks=None):
        super().__init__()
        for check in all_checks:
            self.add_check(check)
            
    def get_name(self,) -> str:
        return "configuration"

    
component = ComponentDTO(configuration, ConfigurationCheck())

def scan_endpoints():
    from flask import Flask
    app = Flask(__name__)
    with app.app_context():
        # static paths
        
        # phenotypes
        from pheweb.serve.server import active_phenolist, api_pheno
        for phenotype in active_phenolist():
            phenocode=phenotype["phenocode"]
            from pheweb.serve.server import pheno
            response=pheno(phenocode)
            assert response.status_code == 200, f"pheno {phenocode}"
            from pheweb.serve.server import autoreport
            response=autoreport(phenocode)
            assert response.status_code == 200, f"pheno {phenocode}"
            for variant in (api_pheno(phenocode)["unbinned_variants"])[0:5]:
                from pheweb.serve.server import autoreport_variants
                locus_id=f"{variant['chrom']}:{variant['pos']}:{variant['ref']}:{variant['alt']}"
                response=autoreport_variants(phenocode,locus_id)
                assert response.status_code == 200, f"pheno {phenocode} variant {locus_id}"
