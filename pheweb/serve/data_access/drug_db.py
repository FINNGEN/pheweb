import json
import abc
import requests
from typing import Union, Dict

"""
This package queries `opentargets<https://www.opentargets.org/>`
and returns the drug information related to the gene name.

There is a `playground<https://api.platform.opentargets.org/api/v4/graphql/browser>`
to develop the graphql queries.

Documentation on how to query :
`tutorial <https://genetics-docs.opentargets.org/data-access/graphql-api>`
`presentation <https://platform-docs.opentargets.org/data-access/graphql-api>`
`training <https://www.ebi.ac.uk/training/events/getting-started-open-targets-platform-graphql-api/>`
`blog post <https://clarewest.github.io/blog/post/crash-course-in-open-targets-part-1/>`
"""


class DrugDB(object):
    @abc.abstractmethod
    def get_drugs(self, gene) -> object:
        """
        Retrieve drugs for a given gene

        @param gene: gene name
        @return: information about drugs associated with the gene
        """
        raise NotImplementedError


def nvl_attribute(name: str, obj: Union[None, Dict], default):
    """
    Given an name and a value return
    the dictionary lookup of the name
    if the value is a dictionary.
    The default is returned if not
    found.

    @param name: name to lookup
    @param obj: object to look into
    @param default: value to return if not found.
    @return: value if found otherwise default
    """
    return obj[name] if obj and name in obj else default


def copy_attribute(name, src, dst):
    """
    Given a name copy attribute from
    source object to destination object
    @param name: field name
    @param src: source object
    @param dst: destination object
    @return: destination object
    """
    if src and name in src:
        dst[name] = src[name]
    return dst


def prettify_stage(stage):
    """
    Open Targets reports clinical stages as codes like
    "PHASE_3" or "APPROVAL". Reformat those for display.

    @param stage: raw stage code, or None
    @return: human-readable stage, or None
    """
    return stage.replace('_', ' ').capitalize() if stage else stage


def extract_rows(response, gene_name):
    """
    The Open Targets schema reports known drugs as a list of
    drug/target pairs (`drugAndClinicalCandidates`), each with its own
    list of associated diseases, rather than one flat row per
    drug-disease evidence entry. Flatten that back into one row per
    (drug, disease) pair, carrying the target's overall target classes
    along with each row since they're no longer reported per-drug.

    @param response:
    @param gene_name:
    @return: flattened list of drug/disease rows
    """
    data = nvl_attribute('data', response, {})
    search = nvl_attribute('search', data, {})
    hits = nvl_attribute('hits', search, [])
    hits = sorted(hits, key=lambda x: x['score'], reverse=True)
    hit = next((h for h in hits if h['name'] == gene_name), {})
    target = nvl_attribute('object', hit, {})
    target_classes = [tc['label'] for tc in nvl_attribute('targetClass', target, []) if tc]
    candidates = nvl_attribute('drugAndClinicalCandidates', target, {})
    candidate_rows = nvl_attribute('rows', candidates, [])

    rows = []
    for candidate in candidate_rows:
        diseases = [d['disease'] for d in nvl_attribute('diseases', candidate, []) if d.get('disease')]
        for disease in diseases or [None]:
            rows.append({
                'phase': candidate.get('maxClinicalStage'),
                'targetClass': target_classes,
                'drug': candidate.get('drug'),
                'disease': disease,
            })
    return rows


def reshape_row(row):
    """
    The response object needs to be reshaped
    to a list of rows:

    the fields of the rows are


    approvedName: string
    diseaseName: string
    drugId: string
    drugType: string
    maximumClinicalTrialPhase: string
    mechanismOfAction: string
    phase: string
    prefName: string
    targetClass: array[string]


    @param row:
    @return: reshaped row
    """
    result = {}
    if row.get('disease'):
        disease = row['disease']
        if 'name' in disease:
            result['diseaseName'] = disease['name']
        db_xrefs = disease['dbXRefs'] if 'dbXRefs' in disease else []
        efo_info = next((d for d in db_xrefs if d.startswith('EFO:')), None)
        if efo_info:
            result['EFOInfo'] = efo_info
    if row.get('drug'):
        drug = row['drug']
        if 'id' in drug:
            result['drugId'] = drug['id']
        if 'name' in drug:
            # the new schema no longer distinguishes a separate "preferred
            # name" from the drug's generic name, so both map to it.
            result['prefName'] = drug['name']
            result['approvedName'] = drug['name']
        copy_attribute('drugType', drug, result)
        if drug.get('maximumClinicalStage'):
            result['maximumClinicalTrialPhase'] = prettify_stage(drug['maximumClinicalStage'])
        moa_rows = nvl_attribute('rows', nvl_attribute('mechanismsOfAction', drug, {}), [])
        mechanisms = [m['mechanismOfAction'] for m in moa_rows if m.get('mechanismOfAction')]
        if mechanisms:
            result['mechanismOfAction'] = '; '.join(dict.fromkeys(mechanisms))
    if row.get('phase'):
        result['phase'] = prettify_stage(row['phase'])
    copy_attribute('targetClass', row, result)
    return result


def query_endpoint(gene_name):
    """

    @param gene_name:
    @return:
    """
    # see : https://platform-docs.opentargets.org/data-access/graphql-api
    # `knownDrugs` was removed from the schema; known drugs are now reported
    # per drug/target pair via `drugAndClinicalCandidates`, each with its own
    # list of associated diseases (see extract_rows for the flattening back
    # into drug/disease rows).
    query_string = """
            query search($gene_name: String!) {
              search( queryString : $gene_name , entityNames:["target"] ) {
                hits {
                  score
                  name
                  object {
                    __typename ... on Target { id
                    approvedSymbol
                        approvedName
                        targetClass { label }
                        drugAndClinicalCandidates { rows {
                                            # overall clinical stage reached by this drug against this target
                                            maxClinicalStage
                                            drug {
                                                   id
                                                   name
                                                   drugType
                                                   maximumClinicalStage
                                                   mechanismsOfAction { rows { mechanismOfAction } }
                                            }
                                            diseases {
                                                disease { dbXRefs , name }
                                            }
                        } }
                    }

                  }
                }
              }
            }
        """
    variables = {"gene_name": gene_name}
    # Set base URL of GraphQL API endpoint
    base_url = "https://api.platform.opentargets.org/api/v4/graphql"

    # Perform POST request and check status code of response
    r = requests.post(base_url,
                      json={"query": query_string, "variables": variables})
    assert r.status_code == 200, f"failed fetching drugs : ${r}"
    response = json.loads(r.text)
    return response


def fetch_drugs(gene_name):
    """
    fetch drug information for gene.

    @param gene_name: gene name to search for
    @return: information
    """
    response = query_endpoint(gene_name)
    rows = extract_rows(response, gene_name)
    rows = list(map(reshape_row, rows))
    return rows


class DrugDao(DrugDB):
    """
        Drug DAO.

        DAO for fetch drug data from open targets.
    """

    def __init__(self):
        pass

    def get_drugs(self, gene_name):
        """
        Get drugs.

        Get drug information for gene.

        @param gene_name: gene name
        @return: information if there is any.
        """
        return fetch_drugs(gene_name)
