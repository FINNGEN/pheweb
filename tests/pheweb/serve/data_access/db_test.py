import gzip
import json
import os
import re
from pheweb.serve.data_access.db import (
    Variant,
    optional_float,
    TabixResultDao,
    TabixResultFiltDao,
    TabixResultCommonDao,
)
import unittest
from unittest.mock import MagicMock

test_data_file_path = os.getcwd() + "/tests/mocked-data/mocked.tsv.gz"
test_wide_data_file_path = os.getcwd() + "/tests/mocked-data/mocked-wide.tsv.gz"
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
test_phenocode = "AB1_ASPERGILLOSIS"
test_variant = "1:13668:G:A"

mocked_pheno_result = {
    "mlogp": 83,
    "beta": 80,
    "sebeta": 69,
    "maf": None,
    "maf_case": None,
    "maf_control": None,
    "pval": None,
}


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
        self.mocked_pheno_list_data = unittest.mock.MagicMock(
            return_value=self.pheno_list_data[0]
        )

    def test_resultdb_interface_implemented(self):
        tabix_result = TabixResultDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        tabix_result_filt = TabixResultFiltDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        with self.assertRaises(not NotImplementedError or AttributeError):
            tabix_result.mock_test()
            tabix_result_filt.mock_test()


class TestTabixResultDao(unittest.TestCase):
    def setUp(self):
        # Load resources
        with open(test_pheno_list_path, "r") as f:
            self.pheno_list_data = json.load(f)
        self.mocked_pheno_list_data = unittest.mock.MagicMock(
            return_value=self.pheno_list_data
        )
        self.split_query = re.split("-|:|/|_", test_variant)
        self.variant = Variant(
            self.split_query[0],
            self.split_query[1],
            self.split_query[2],
            self.split_query[3],
        )

    def test_should_return_get_single_variant_results_tabix_result(self):
        # check get_single_variant_results for TestTabixResultDao
        tabix_results = TabixResultDao(
            self.mocked_pheno_list_data, test_wide_data_file_path, test_mocked_columns
        )
        results = tabix_results.get_single_variant_results(self.variant)
        self.assertTrue(len(results) > 0)
        self.assertTrue(isinstance(results, (list, tuple)))
        self.assertEqual(str(results[0]), test_variant)
        variant_results = [obj.__dict__ for obj in results[1]]
        result_phenotype = next((i for i, d in enumerate(variant_results) if d.get('phenocode') == test_phenocode), None)
        self.assertIsNotNone(variant_results[result_phenotype]['phenocode'])
        self.assertEqual(variant_results[result_phenotype]['phenocode'], test_phenocode)


class TestTabixResultFiltDao(unittest.TestCase):
    def setUp(self):
        # Load resources
        with open(test_pheno_list_path, "r") as f:
            self.pheno_list_data = json.load(f)
        self.mocked_pheno_list_data = unittest.mock.MagicMock(
            return_value=self.pheno_list_data[0]
        )
        self.split_query = re.split("-|:|/|_", test_variant)
        self.variant = Variant(
            self.split_query[0],
            self.split_query[1],
            self.split_query[2],
            self.split_query[3],
        )

    def test_should_return_get_single_variant_results(self):
        # check get_single_variant_results
        tabix_results = TabixResultFiltDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns
        )
        results = tabix_results.get_single_variant_results(self.variant)
        self.assertTrue(len(results) > 0)
        self.assertTrue(isinstance(results, (list, tuple)))
        self.assertEqual(str(results[0]), test_variant)
        variant_results = [obj.__dict__ for obj in results[1]]
        self.assertEqual(len(variant_results), len(self.pheno_list_data[0]))
        phenolist_values = [list(d.values())[0] for d in self.pheno_list_data]
        self.assertTrue(
            len(self.pheno_list_data[0][variant_results[0]["phenocode"]]) > 0
        )
        self.assertEqual(
            variant_results[0]["phenostring"], str(phenolist_values[0]["phenostring"])
        )
        self.assertEqual(
            variant_results[0]["category"], phenolist_values[0]["category"]
        )
        self.assertEqual(
            variant_results[0]["category_index"], phenolist_values[0]["category_index"]
        )
        self.assertEqual(variant_results[0]["n_case"], phenolist_values[0]["num_cases"])
        self.assertEqual(
            variant_results[0]["n_control"], phenolist_values[0]["num_controls"]
        )


class TestTabixResultCommonDao(unittest.TestCase):
    def setUp(self):
        # Load resources
        with gzip.open(test_data_file_path, "r") as f:
            self.data = f.read().splitlines()
        self.header = self.data[0].decode("utf-8").split("\t")
        with open(test_pheno_list_path, "r") as f:
            self.mocked_pheno_list_data = json.load(f)
        self.mocked_pheno_list_data = unittest.mock.MagicMock(
            return_value=self.mocked_pheno_list_data[0]
        )
        self.split = self.data[1]
        self.phenos = [
            (h.split("@")[1], p_col_idx)
            for p_col_idx, h in enumerate(self.header)
            if h.startswith("pval")
        ]
        self.split_query = re.split("-|:|/|_", test_variant)

    def test_should_return_variant_common_columns(self):
        # check get_variant_common_columns
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data)
        phenotype, beta, sebeta, maf, maf_case, maf_control, mlogp, pval = (
            tabix_result_common.get_variant_common_columns(
                self.split, self.phenos, None, test_mocked_columns, self.header
            )
        )
        self.assertEqual(phenotype, self.split[0])
        self.assertEqual(beta, mocked_pheno_result["beta"])
        self.assertEqual(sebeta, mocked_pheno_result["sebeta"])
        self.assertEqual(maf, mocked_pheno_result["maf"])
        self.assertEqual(maf_case, mocked_pheno_result["maf_case"])
        self.assertEqual(maf_control, mocked_pheno_result["maf_control"])
        self.assertEqual(mlogp, mocked_pheno_result["mlogp"])
        self.assertEqual(pval, mocked_pheno_result["pval"])

    def test_should_return_variant_columns_using_header(self):
        # check get_variant_columns_using_header
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data)
        results = tabix_result_common.get_variant_columns_using_header(
            self.split, self.header
        )
        self.assertEqual(len(results), 8)

    def test_should_return_common_pheno_results(self):
        # check get_common_pheno_results
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data)
        phenotype, beta, sebeta, maf, maf_case, maf_control, mlogp, pval = (
            tabix_result_common.get_variant_columns_using_header(
                self.split, self.header
            )
        )
        self.assertEqual(phenotype, self.split[0])
        self.assertEqual(beta, mocked_pheno_result["beta"])
        self.assertEqual(sebeta, mocked_pheno_result["sebeta"])
        self.assertEqual(maf, mocked_pheno_result["maf"])
        self.assertEqual(maf_case, mocked_pheno_result["maf_case"])
        self.assertEqual(maf_control, mocked_pheno_result["maf_control"])
        self.assertEqual(mlogp, mocked_pheno_result["mlogp"])
        self.assertEqual(pval, mocked_pheno_result["pval"])
        # check common phenoresults
        common_phenoresults = tabix_result_common.get_common_pheno_results(
            phenotype, pval, beta, sebeta, maf, maf_case, maf_control, mlogp
        )
        self.assertIsNotNone(common_phenoresults)
        self.assertEqual(common_phenoresults.beta, mocked_pheno_result["beta"])
        self.assertEqual(common_phenoresults.sebeta, mocked_pheno_result["sebeta"])
        self.assertEqual(common_phenoresults.maf, mocked_pheno_result["maf"])
        self.assertEqual(common_phenoresults.maf_case, mocked_pheno_result["maf_case"])
        self.assertEqual(
            common_phenoresults.maf_control, mocked_pheno_result["maf_control"]
        )
        self.assertEqual(common_phenoresults.mlogp, mocked_pheno_result["mlogp"])
        self.assertEqual(common_phenoresults.pval, mocked_pheno_result["pval"])

    def test_should_return_common_variant_results_range(self):
        # check get_common_variant_results_range
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data)
        variant_results_range = tabix_result_common.get_common_variant_results_range(
            self.split_query[0],
            int(self.split_query[1]),
            int(self.split_query[1]),
            test_data_file_path,
            self.header,
            test_mocked_columns,
            None,
            self.phenos,
        )
        self.assertIsNotNone(variant_results_range)
        self.assertEqual(list(variant_results_range), [])


if __name__ == "__main__":
    unittest.main()
