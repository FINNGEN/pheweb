# -*- coding: utf-8 -*-

"""
Unit test for drug db module.

See: pheweb/serve/data_access/drug_db.py

"""
import json
from unittest.mock import patch

import pytest

from pheweb.serve.data_access.drug_db import DrugDB, DrugDao


def _response(hits):
    return {"data": {"search": {"hits": hits}}}


def _hit(name, score, target):
    return {"name": name, "score": score, "object": target}


def _target(target_class=None, candidates=None):
    return {
        "targetClass": target_class or [],
        "drugAndClinicalCandidates": {"rows": candidates or []},
    }


def _candidate(drug=None, diseases=None, max_clinical_stage=None):
    return {
        "maxClinicalStage": max_clinical_stage,
        "drug": drug,
        "diseases": [{"disease": d} for d in (diseases or [])],
    }


def _drug(drug_id="CHEMBL1", name="ASPIRIN", drug_type="Small molecule",
          max_clinical_stage=None, mechanisms=None):
    return {
        "id": drug_id,
        "name": name,
        "drugType": drug_type,
        "maximumClinicalStage": max_clinical_stage,
        "mechanismsOfAction": {
            "rows": [{"mechanismOfAction": m} for m in (mechanisms or [])]
        },
    }


def _disease(name, db_xrefs=None):
    return {"name": name, "dbXRefs": db_xrefs or []}


def _dao_with_response(response):
    dao = DrugDao()
    dao.query_endpoint = lambda gene_name: response
    return dao


# --- DrugDB / DrugDao ---------------------------------------------------------

def test_drug_db_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        DrugDB()


def test_drug_dao_is_a_drug_db():
    assert isinstance(DrugDao(), DrugDB)


# --- DrugDao.query_endpoint -----------------------------------------------------

def test_query_endpoint_posts_query_and_returns_parsed_response():
    fixture_response = _response([_hit("DBH", 1, _target())])
    with patch("pheweb.serve.data_access.drug_db.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = json.dumps(fixture_response)

        response = DrugDao().query_endpoint("DBH")

    assert response == fixture_response
    _, kwargs = mock_post.call_args
    assert mock_post.call_args.args[0] == "https://api.platform.opentargets.org/api/v4/graphql"
    assert kwargs["json"]["variables"] == {"gene_name": "DBH"}
    assert "drugAndClinicalCandidates" in kwargs["json"]["query"]


def test_query_endpoint_raises_on_non_200_response():
    with patch("pheweb.serve.data_access.drug_db.requests.post") as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "{}"
        with pytest.raises(AssertionError):
            DrugDao().query_endpoint("DBH")


# --- DrugDao._prettify_stage -----------------------------------------------------

def test_prettify_stage_none_stays_none():
    # This is important because the API might give us None values
    assert DrugDao()._prettify_stage(None) is None

def test_prettify_stage_formats_phase_codes():
    dao = DrugDao()
    assert dao._prettify_stage("PHASE_3") == "Phase 3"
    assert dao._prettify_stage("APPROVAL") == "Approval"


# --- DrugDao.get_drugs -----------------------------------------------------------

def test_get_drugs_empty_response_returns_no_rows():
    dao = _dao_with_response({})
    assert dao.get_drugs("PCSK9") == []


def test_get_drugs_no_matching_hit_returns_no_rows():
    dao = _dao_with_response(_response([_hit("SOMEOTHERGENE", 10, _target())]))
    assert dao.get_drugs("PCSK9") == []


def test_get_drugs_picks_the_highest_scoring_matching_hit():
    low_score_target = _target(candidates=[_candidate(drug=_drug(name="LOW_SCORE_DRUG"))])
    high_score_target = _target(candidates=[_candidate(drug=_drug(name="HIGH_SCORE_DRUG"))])
    dao = _dao_with_response(_response([
        _hit("PCSK9", 1, low_score_target),
        _hit("PCSK9", 99, high_score_target),
    ]))

    rows = dao.get_drugs("PCSK9")

    assert len(rows) == 1
    assert rows[0]["approvedName"] == "HIGH_SCORE_DRUG"


def test_get_drugs_candidate_without_a_drug_is_skipped():
    target = _target(candidates=[_candidate(drug=None, diseases=[_disease("some disease")])])
    dao = _dao_with_response(_response([_hit("PCSK9", 1, target)]))
    assert dao.get_drugs("PCSK9") == []


def test_get_drugs_maps_a_full_row():
    drug = _drug(
        drug_id="CHEMBL3137349",
        name="BOCOCIZUMAB",
        drug_type="Antibody",
        max_clinical_stage="PHASE_3",
        mechanisms=["Subtilisin/kexin type 9 inhibitor"],
    )
    disease = _disease("hyperlipidemia", db_xrefs=["MESH:D006949", "EFO:0004911"])
    target = _target(
        target_class=[{"label": "Enzyme"}, {"label": "Protease"}],
        candidates=[_candidate(drug=drug, diseases=[disease], max_clinical_stage="PHASE_3")],
    )
    dao = _dao_with_response(_response([_hit("PCSK9", 1, target)]))

    rows = dao.get_drugs("PCSK9")

    assert rows == [{
        "approvedName": "BOCOCIZUMAB",
        "diseaseName": "hyperlipidemia",
        "EFOInfo": "EFO:0004911",
        "drugId": "CHEMBL3137349",
        "drugType": "Antibody",
        "maximumClinicalTrialPhase": "Phase 3",
        "mechanismOfAction": "Subtilisin/kexin type 9 inhibitor",
        "phase": "Phase 3",
        "prefName": "BOCOCIZUMAB",
        "targetClass": ["Enzyme", "Protease"],
    }]


def test_get_drugs_emits_one_row_per_disease():
    drug = _drug()
    target = _target(candidates=[_candidate(
        drug=drug,
        diseases=[_disease("disease A"), _disease("disease B")],
    )])
    dao = _dao_with_response(_response([_hit("PCSK9", 1, target)]))

    rows = dao.get_drugs("PCSK9")

    assert [r["diseaseName"] for r in rows] == ["disease A", "disease B"]
    assert all(r["drugId"] == drug["id"] for r in rows)


def test_get_drugs_deduplicates_repeated_diseases():
    target = _target(candidates=[_candidate(
        drug=_drug(),
        diseases=[_disease("disease A"), _disease("disease A")],
    )])
    dao = _dao_with_response(_response([_hit("PCSK9", 1, target)]))

    rows = dao.get_drugs("PCSK9")

    assert len(rows) == 1
    assert rows[0]["diseaseName"] == "disease A"


def test_get_drugs_candidate_with_no_diseases_still_emits_a_row():
    target = _target(candidates=[_candidate(drug=_drug(name="SOLO_DRUG"), diseases=[])])
    dao = _dao_with_response(_response([_hit("PCSK9", 1, target)]))

    rows = dao.get_drugs("PCSK9")

    assert len(rows) == 1
    assert rows[0]["approvedName"] == "SOLO_DRUG"
    assert rows[0]["diseaseName"] is None
    assert rows[0]["EFOInfo"] is None


def test_get_drugs_missing_optional_fields_become_none():
    drug = {"id": "CHEMBL1", "name": "PLAINDRUG"}  # no drugType, no stage, no mechanisms
    target = _target(candidates=[_candidate(drug=drug, diseases=[_disease("disease A")])])
    dao = _dao_with_response(_response([_hit("PCSK9", 1, target)]))

    rows = dao.get_drugs("PCSK9")

    assert len(rows) == 1
    row = rows[0]
    assert row["drugType"] is None
    assert row["maximumClinicalTrialPhase"] is None
    assert row["mechanismOfAction"] is None
    assert row["phase"] is None
    assert row["EFOInfo"] is None


def test_get_drugs_joins_deduplicated_mechanisms_of_action():
    drug = _drug(mechanisms=["Inhibitor", "Antagonist", "Inhibitor"])
    target = _target(candidates=[_candidate(drug=drug, diseases=[_disease("disease A")])])
    dao = _dao_with_response(_response([_hit("PCSK9", 1, target)]))

    rows = dao.get_drugs("PCSK9")

    assert rows[0]["mechanismOfAction"] == "Inhibitor; Antagonist"
