from flask import request
from pheweb.serve.components.model import ComponentCheck, ComponentStatus

class HomepageCheck(ComponentCheck):

    def get_status(self,) -> ComponentStatus:
        is_okay = True
        messages = []
        response = request.url_rule("").endpoint()
        return response

# def homepage(path):
# def api_404(path):
# def autoreport(phenocode):
# def autoreport_variants(phenocode,locus_id):
# def pheno(phenocode):
# def phenolist():
# def api_variant(query):
# def api_variant_pheno(query, phenocode):
# def api_pheno(phenocode):
# def api_gene_phenotypes(gene):
# def api_gene_functional_variants(gene):
# def api_lof():
# def api_lof_gene(gene):
# def api_top_hits():
# def download_top_hits():
# def api_pheno_qq(phenocode):
# def ukbb_ns(phenocode):
# def api_region_page(phenocode, region):
# def api_region(phenocode):
# def api_conditional_region(phenocode):
# def api_finemapped_region(phenocode):
# def api_gene_pqtl_colocalization(genename):
# def gene_api(genename):
# def gene_report(genename):
# def drugs(genename):
# def ncbi(endpoint):
