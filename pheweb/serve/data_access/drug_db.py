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


class DrugDB(abc.ABC):
    @abc.abstractmethod
    def get_drugs(self, gene) -> object:
        """
        Retrieve drugs for a given gene

        @param gene: gene name
        @return: information about drugs associated with the gene
        """

class DrugDao(DrugDB):
    """
        Drug DAO.

        DAO for fetch drug data from open targets.
    """

    def __init__(self):
        pass

    def _prettify_stage(self, stage):
        # Open Targets reports clinical stages as codes like "PHASE_3" or
        # "APPROVAL"; reformat those for display.
        return stage.replace('_', ' ').capitalize() if stage else None



    def query_endpoint(self, gene_name):
        """
        @param gene_name: gene name to search for
        @return: response from the GraphQL API
        """
        # see : https://platform-docs.opentargets.org/data-access/graphql-api
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

    def get_drugs(self, gene_name):
        """
        fetch drug information for gene.

        @param gene_name: gene name to search for
        @return: information
        """
        response = self.query_endpoint(gene_name)
        # the API assigns a score for the probability of the hit,
        # so we take the highest scoring result with the exact gene name match.
        hits = response.get('data', {}).get('search', {}).get('hits', [])
        hit = max(
            (h for h in hits if h.get('name') == gene_name),
            key=lambda h: h['score'],
            default=None,
        )
        if hit is None:
            return []

        target = hit.get('object') or {}
        target_classes = [tc['label'] for tc in target.get('targetClass', [])]
        candidates = target.get('drugAndClinicalCandidates', {}).get('rows', [])

        rows = []
        for candidate in candidates:
            drug = candidate.get('drug')
            # If the candidate has no drug, skip it
            if not drug:
                continue
            mechanisms = [
                m['mechanismOfAction']
                for m in drug.get('mechanismsOfAction', {}).get('rows', [])
                if m.get('mechanismOfAction')
            ]
            diseases = [d['disease'] for d in candidate.get('diseases', []) if d.get('disease')]

            # deduplicate the diseases here by name, because the API seems to give duplicates on some diseases
            seen = set()
            diseases = [d for d in diseases if d['name'] not in seen and not seen.add(d['name'])]

            for disease in diseases or [{}]:
                db_xrefs = disease.get('dbXRefs', [])
                rows.append({
                    'approvedName': drug.get('name'),
                    'diseaseName': disease.get('name'),
                    'EFOInfo': next((x for x in db_xrefs if x.startswith('EFO:')), None),
                    'drugId': drug.get('id'),
                    'drugType': drug.get('drugType'),
                    'maximumClinicalTrialPhase': self._prettify_stage(drug.get('maximumClinicalStage')),
                    'mechanismOfAction': '; '.join(dict.fromkeys(mechanisms)) or None,
                    'phase': self._prettify_stage(candidate.get('maxClinicalStage')),
                    'prefName': drug.get('name'),
                    'targetClass': target_classes,
                })
        return rows
