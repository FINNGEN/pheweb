import gzip
import json
import os
import re
from pheweb.serve.data_access.db import (
    Variant,
    optional_float,
    TabixResultLongDao,
)
import unittest

test_data_file_path = os.getcwd() + "/tests/mocked-data/mocked.tsv.gz"
test_pheno_list_path = os.getcwd() + "/tests/mocked-data/mocked-pheno-list.json"
test_mocked_columns = {
    "pheno": "#pheno",
    "mlogp": "mlogp",
    "beta": "beta",
    "sebeta": "sebeta",
    "maf": "af_alt",
    "maf_cases": "af_alt_cases",
    "maf_controls": "af_alt_controls",
}
test_phenocode = "AB1_ACTINOMYCOSIS"
test_variant = "1:13668:G:A"
expected_phenoresults = [
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 4393453048,
        'phenocode': 'AB1_ASPERGILLOSIS',
        'mlogp': 1.34969,
        'beta': 2.05148,
        'sebeta': 1.02193,
        'maf': 0.00598008,
        'maf_case': 0.00992459,
        'maf_control': 0.00597798
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 439044448,
        'phenocode': 'AB1_DIBTHERIA',
        'mlogp': 1.94317,
        'beta': 5.647,
        'sebeta': 2.23179,
        'maf': 0.00596686,
        'maf_case': 0.0167393,
        'maf_control': 0.00596554
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 439444048,
        'phenocode': 'CAMPYLOENTERITIS',
        'mlogp': 1.66483,
        'beta': 1.25355,
        'sebeta': 0.545803,
        'maf': 0.0059836,
        'maf_case': 0.00826492,
        'maf_control': 0.00597919
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 43934048,
        'phenocode': 'CD2_BENIGN_ANUS_ANAL_CANAL',
        'mlogp': 1.35031,
        'beta': 1.08065,
        'sebeta': 0.538156,
        'maf': 0.00598633,
        'maf_case': 0.00807085,
        'maf_control': 0.00598227
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 439044448,
        'phenocode': 'AB1_DIBTHERIA',
        'mlogp': 2.94317,
        'beta': 5.647,
        'sebeta': 2.23179,
        'maf': 0.00596686,
        'maf_case': 0.0167393,
        'maf_control': 0.00596554
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 439044448,
        'phenocode': 'AB1_DIBTHERIA',
        'mlogp': 6.94317,
        'beta': 5.647,
        'sebeta': 2.23179,
        'maf': 0.00596686,
        'maf_case': 0.0167393,
        'maf_control': 0.00596554
    },
]


def test_optional_float() -> None:
    """Test optional float.

    @return: None
    """
    assert optional_float(None) is None
    assert optional_float("NA") is None
    assert optional_float("") is None
    assert optional_float("1.0") == 1.0
    assert optional_float(1.0) == 1.0


class TestDBValidatedInterfacesImplemented(unittest.TestCase):
    def setUp(self):
        # Load resources
        with open(test_pheno_list_path, "r") as f:
            self.pheno_list_data = json.load(f)
        self.mocked_pheno_list_data=lambda x:self.pheno_list_data[0]

    def test_resultdb_interface_implemented(self):
        tabix_result_long = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        with self.assertRaises(not NotImplementedError or AttributeError):
            tabix_result_long.mock_test()


class TestTabixResultLongDao(unittest.TestCase):
    def setUp(self):
        # Load resources
        with open(test_pheno_list_path, "r") as f:
            self.pheno_list_data = json.load(f)
        self.mocked_pheno_list_data=lambda x:self.pheno_list_data[0]
        self.split_query = test_variant.split(":")
        self.variant = Variant(
            self.split_query[0],
            self.split_query[1],
            self.split_query[2],
            self.split_query[3],
        )
        self.validation_value = {
            "beta":2.05148,
            "sebeta":1.02193,
            "maf":0.00598008,
            "maf_case":0.00992459,
            "maf_control":0.00597798,
            "mlogp":1.34969,
            "pval":0.04470025493374374
        }
    
    def validate_phenoresult(self, phenoresult, expected):
        columns_to_validate = ["category", "category_index", "phenostring", "n_case", "n_control",
                "phenocode", "mlogp", "beta", "sebeta", "maf", "maf_case", "maf_control"]
        for column in columns_to_validate:
            self.assertEqual(phenoresult[column], expected[column], f"Mismatch in column '{column}'")

    def test_should_return_get_single_variant_results(self):
        # check get_single_variant_results
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        results = tabix_results.get_single_variant_results(self.variant)
        self.assertTrue(len(results) > 0)
        self.assertTrue(isinstance(results, (list, tuple)))
        self.assertEqual(str(results[0]), test_variant)
        variant_results = [obj.__dict__ for obj in results[1]]
        self.assertEqual(len(variant_results), len(self.pheno_list_data[0]))
        self.assertTrue(
            len(self.pheno_list_data[0][variant_results[0]["phenocode"]]) > 0
        )
        self.validate_phenoresult(variant_results[0], expected_phenoresults[0])

    def test_single_should_return_none_if_variant_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        variant_not_found = Variant("1", "13668", "G", "C")
        results = tabix_results.get_single_variant_results(variant_not_found)
        self.assertEqual(results, None)

    def test_variants_results_returns_empty_list_if_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        variant_not_found = Variant("1", "13668", "G", "C")
        results = tabix_results.get_variants_results([variant_not_found])
        self.assertEqual(results, [])
    
    def test_variant_range_returns_empty_list_if_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        results = tabix_results.get_variant_results_range("1", 13669, 13670)
        self.assertEqual(results, [])

    def test_top_pheno_per_range_returns_empty_list_if_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        results = tabix_results.get_top_per_pheno_variant_results_range("1", 13669, 13670)
        self.assertEqual(results, [])

    # def test_top_pheno_per_range_returns_correct_result(self):
    #     """There are three variants for AB1_DIBTHERIA in the test data, and we
    #     want to make sure that the one with lowest p in the range is found"""
    #     tabix_results = TabixResultLongDao(
    #         self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
    #     )
    #     results = tabix_results.get_top_per_pheno_variant_results_range("1", 13668, 13675)
    #     phenocodes_found = set(res.assoc.phenocode for res in results)
    #     self.assertIn('AB1_DIBTHERIA', phenocodes_found)
    #     self.assertIn('CD2_BENIGN_ANUS_ANAL_CANAL', phenocodes_found)
    #     self.assertIn('CAMPYLOENTERITIS', phenocodes_found)
    #     self.assertEqual(len(results), 3)
    #     for res in results:
    #         if res.assoc.phenocode == 'AB1_DIBTHERIA':
    #             self.validate_phenoresult(res, expected_phenoresults[4])
    #             return
    #     self.fail("Expected phenocode 'AB1_DIBTHERIA' not found in results")
