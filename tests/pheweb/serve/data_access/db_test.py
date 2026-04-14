import gzip
import json
import os
import re
from pheweb.serve.data_access.db import (
    Variant,
    PhenoResult,
    optional_float,
    TabixResultLongDao,
)
import unittest

test_data_file_path = os.getcwd() + "/tests/mocked-data/mocked_data_long.tsv.gz"
test_pheno_list_path = os.getcwd() + "/tests/mocked-data/mocked-pheno-list.json"

# mock of the column configuration in pheweb
test_mocked_columns = {
    "pheno": "#pheno",
    "mlogp": "mlogp",
    "beta": "beta",
    "sebeta": "sebeta",
    "maf": "af_alt",
    "maf_cases": "af_alt_cases",
    "maf_controls": "af_alt_controls",
    "extra_2_renamed": "extra_2"
}

# This is the expected result for mocked_data_long.tsv.gz
expected_phenoresults = [
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 4393453048,
        'phenocode': 'AB1_ASPERGILLOSIS',
        'mlogp': 1.34969,
        'pval': 0.04470025493374374,
        'beta': 2.05148,
        'sebeta': 1.02193,
        'maf': 0.00598008,
        'maf_case': 0.00992459,
        'maf_control': 0.00597798,
        'extra_1': '1.0',
        'extra_2_renamed': '0.1'
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 439044448,
        'phenocode': 'AB1_DIBTHERIA',
        'mlogp': 1.94317,
        'pval': 0.011398035361393439,
        'beta': 5.647,
        'sebeta': 2.23179,
        'maf': 0.00596686,
        'maf_case': 0.0167393,
        'maf_control': 0.00596554,
        'extra_1': '2.0',
        'extra_2_renamed': '0.2'
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 439444048,
        'phenocode': 'CAMPYLOENTERITIS',
        'mlogp': 1.66483,
        'pval': 0.02163565262823381,
        'beta': 1.25355,
        'sebeta': 0.545803,
        'maf': 0.0059836,
        'maf_case': 0.00826492,
        'maf_control': 0.00597919,
        'extra_1': '3.0',
        'extra_2_renamed': '0.3'
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 43934048,
        'phenocode': 'CD2_BENIGN_ANUS_ANAL_CANAL',
        'mlogp': 1.35031,
        'pval': 0.04463648625553314,
        'beta': 1.08065,
        'sebeta': 0.538156,
        'maf': 0.00598633,
        'maf_case': 0.00807085,
        'maf_control': 0.00598227,
        'extra_1': '4.0',
        'extra_2_renamed': '0.4'
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 439044448,
        'phenocode': 'AB1_DIBTHERIA',
        'mlogp': 2.94317,
        'pval': 0.0011398035361393445,
        'beta': 5.647,
        'sebeta': 2.23179,
        'maf': 0.00596686,
        'maf_case': 0.0167393,
        'maf_control': 0.00596554,
        'extra_1': '5.0',
        'extra_2_renamed': '0.5'
    },
    {
        "category": "I Certain infectious and parasitic diseases (AB1_)",
        "category_index": 1,
        "phenostring": "Actinomycosis",
        "n_case": 124,
        "n_control": 439044448,
        'phenocode': 'AB1_DIBTHERIA',
        'mlogp': 6.94317,
        'pval': 1.1398035361393433e-07,
        'beta': 5.647,
        'sebeta': 2.23179,
        'maf': 0.00596686,
        'maf_case': 0.0167393,
        'maf_control': 0.00596554,
        'extra_1': '6.0',
        'extra_2_renamed': '0.6'
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
        self.mocked_pheno_list_data = lambda x: self.pheno_list_data[0]

    def validate_phenoresult(self, phenoresult, expected):
        phenoresult_dict = vars(phenoresult)
        columns_to_validate = ["category", "category_index", "phenostring", "n_case", "n_control",
                "phenocode", "mlogp", "pval", "beta", "sebeta", "maf", "maf_case", "maf_control", "extra_1", "extra_2_renamed"]
        for column in columns_to_validate:
            self.assertEqual(phenoresult_dict[column], expected[column], f"Mismatch in column '{column}'")

    def test_should_return_get_single_variant_results(self):
        # check get_single_variant_results
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        variant = Variant("1", "13670", "G", "A")
        results = tabix_results.get_single_variant_results(variant)
        self.assertTrue(len(results) > 0)
        self.assertTrue(isinstance(results, (list, tuple)))
        self.assertEqual(results[0], variant)
        variant_results = results[1]
        self.assertEqual(len(variant_results), 1)
        self.assertTrue(
            len(self.pheno_list_data[0][variant_results[0].phenocode]) > 0
        )
        self.validate_phenoresult(variant_results[0], expected_phenoresults[2])

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
        results = tabix_results.get_variant_results_range("1", 10000, 13667)
        self.assertEqual(results, [])

    def test_top_pheno_per_range_returns_empty_list_if_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        results = tabix_results.get_top_per_pheno_variant_results_range("1", 13678, 13680)
        self.assertEqual(results, [])

    def test_top_pheno_per_range_returns_correct_results(self):
        """There are three variants for AB1_DIBTHERIA in the test data, and we
        want to make sure that the one with lowest p in the range is found"""
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        results = tabix_results.get_top_per_pheno_variant_results_range("1", 13668, 13675)
        phenocodes_found = set(res.assoc.phenocode for res in results)
        self.assertIn('AB1_DIBTHERIA', phenocodes_found)
        self.assertIn('CD2_BENIGN_ANUS_ANAL_CANAL', phenocodes_found)
        self.assertIn('CAMPYLOENTERITIS', phenocodes_found)
        self.assertIn('AB1_ASPERGILLOSIS', phenocodes_found)
        self.assertEqual(len(results), 4)
        for res in results:
            if res.assoc.phenocode == 'AB1_DIBTHERIA':
                self.validate_phenoresult(res.assoc, expected_phenoresults[4])
                return
        self.fail("Expected phenocode 'AB1_DIBTHERIA' not found in results")
    
    def test_get_multiple_variants_results(self):
        var1 = Variant("1", "13668", "G", "A")
        var2 = Variant("1", "13677", "G", "A")
        no_results_var = Variant("1", "13680", "G", "A")
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        results = tabix_results.get_variants_results([var1, var2, no_results_var])
        self.assertEqual(len(results), 2)
        self.assertIn(var1, [r[0] for r in results])
        self.assertIn(var2, [r[0] for r in results])
        for res in results:
            if res[0] == var1:
                self.assertEqual(len(res[1]), 2)
            elif res[0] == var2:
                self.assertEqual(len(res[1]), 1)
            else:
                self.fail("Result variants don't match the input")
    
    def test_get_variant_range(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        results = tabix_results.get_variant_results_range("1", 13669, 13680)
        self.assertEqual(len(results), 3)
        var1 = Variant("1", "13670", "G", "A")
        var2 = Variant("1", "13675", "G", "A")
        var3 = Variant("1", "13677", "G", "A")
        variants = [res[0] for res in results]
        self.assertIn(var1, variants)
        self.assertIn(var2, variants)
        self.assertIn(var3, variants)
        for res in results:
            if res[0] == var1:
                self.assertEqual(len(res[1]), 1)
            elif res[0] == var2:
                self.assertEqual(len(res[1]), 2)
            elif res[0] == var3:
                self.assertEqual(len(res[1]), 1)
            else:
                self.fail("Variant outside of the variant range found")
    
    def test_p_mlogp(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        self.assertEqual(tabix_results.get_p_and_mlogp(None, None), (None, None))
        self.assertEqual(tabix_results.get_p_and_mlogp("0.01", "2"), ("0.01", "2"))
        self.assertEqual(tabix_results.get_p_and_mlogp(None, "2"), (0.01, "2"))
        self.assertEqual(tabix_results.get_p_and_mlogp("0.01", None), ("0.01", 2))
    
    def test_add_extra_attr(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        row = {
            "beta": 0,
            "sebeta": 0,
            "maf": 0,
            "maf_cases": 0,
            "maf_controls": 0,
            "pval": 0,
            "mlogp": 0,
            "extra_col1": "extra_value1",
            "extra_col2": "extra_value2"
        }
        phenoresult = PhenoResult("test_pheno",
            "Test Phenostring",
            "Test Category",
            1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, None)
        tabix_results.add_extra_columns(row, phenoresult)
        self.assertEqual(phenoresult.extra_col1, "extra_value1")
        self.assertEqual(phenoresult.extra_col2, "extra_value2")
        # Make sure standard columns are not added as extra attributes
        self.assertEqual(phenoresult.beta, 1.0)