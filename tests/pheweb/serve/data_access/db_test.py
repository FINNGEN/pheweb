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
test_phenocode = "AB1_ACTINOMYCOSIS"
test_variant = "1:13668:G:A"
test_wide_columns = {
    "pval": "pval",
    "mlogp": "mlogp",
    "beta": "beta",
    "sebeta": "sebeta",
    "maf": "af_alt",
    "maf_cases": "af_alt_cases",
    "maf_controls": "af_alt_controls",
}
mocked_offset_header = {
    "pval": 0,
    "mlogp": 1,
    "beta": 2,
    "sebeta": 3,
    "af_alt": 4,
    "af_alt_cases": 5,
    "af_alt_controls": 6,
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
        self.mocked_pheno_list_data=lambda x:self.pheno_list_data[0]

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
        self.mocked_pheno_list_data=lambda x:self.pheno_list_data[0]
        self.split_query = test_variant.split(":")
        self.variant = Variant(
            self.split_query[0],
            self.split_query[1],
            self.split_query[2],
            self.split_query[3],
        )
        with gzip.open(test_wide_data_file_path, "rt",encoding="utf-8") as f:
            self.data = f.read().splitlines()
        self.row = self.data[1].split("\t")

    def test_should_return_get_single_variant_results_tabix_result(self):
        # check get_single_variant_results for TestTabixResultDao
        tabix_results = TabixResultDao(
            self.mocked_pheno_list_data, test_wide_data_file_path, test_wide_columns
        )
        tabix_results.header_offset = mocked_offset_header
        results = tabix_results.get_single_variant_results(self.variant)
        self.assertTrue(len(results) > 0)
        self.assertTrue(isinstance(results, (list, tuple)))
        self.assertEqual(str(results[0]), test_variant)
        variant_results = [obj.__dict__ for obj in results[1]]
        result_phenotype = next(
            (
                i
                for i, d in enumerate(variant_results)
                if d.get("phenocode") == test_phenocode
            ),
            None,
        )
        self.assertIsNotNone(variant_results[result_phenotype]["phenocode"])
        self.assertEqual(variant_results[result_phenotype]["phenocode"], test_phenocode)
        self.assertEqual(str(variant_results[result_phenotype]["pval"]), self.row[6])
        self.assertEqual(str(variant_results[result_phenotype]["mlogp"]), self.row[7])
        self.assertEqual(str(variant_results[result_phenotype]["beta"]), self.row[8])
        self.assertEqual(str(variant_results[result_phenotype]["sebeta"]), self.row[9])
        self.assertEqual(str(variant_results[result_phenotype]["maf"]), self.row[10])
        self.assertEqual(str(variant_results[result_phenotype]["af_alt_cases"]), self.row[11])
        self.assertEqual(str(variant_results[result_phenotype]["af_alt_controls"]), self.row[12])


class TestTabixResultFiltDao(unittest.TestCase):
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
        self.assertEqual(variant_results[0]["phenocode"],"AB1_ASPERGILLOSIS")
        self.assertEqual(variant_results[0]["pval"],self.validation_value["pval"])
        self.assertEqual(variant_results[0]["beta"],self.validation_value["beta"])
        self.assertEqual(variant_results[0]["sebeta"],self.validation_value["sebeta"])
        self.assertEqual(variant_results[0]["maf"],self.validation_value["maf"])
        self.assertEqual(variant_results[0]["maf_case"],self.validation_value["maf_case"])
        self.assertEqual(variant_results[0]["maf_control"],self.validation_value["maf_control"])
        self.assertEqual(variant_results[0]["mlogp"],self.validation_value["mlogp"])


class TestTabixResultCommonDao(unittest.TestCase):
    def setUp(self):
        # Load resources
        with gzip.open(test_data_file_path, "rt",encoding="utf-8") as f:
            self.data = f.read().splitlines()
        self.header = self.data[0].split("\t")
        with open(test_pheno_list_path, "r") as f:
            mocked_pheno_list_data = json.load(f)
        self.mocked_pheno_list_data=lambda x:mocked_pheno_list_data[0]

        self.split = self.data[1].split("\t")
        self.phenos=["AB1_ASPERGILLOSIS"]

        self.split_query = test_variant.split(":")

        self.validation_value = {
            "beta":"2.05148",
            "sebeta":"1.02193",
            "maf":"0.00598008",
            "maf_case":"0.00992459",
            "maf_control":"0.00597798",
            "mlogp":"1.34969",
            "pval":None
        }

    def test_should_return_variant_common_columns(self):
        # check get_variant_common_columns
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data(0))
        phenotype, beta, sebeta, maf, maf_case, maf_control, mlogp, pval = (
            tabix_result_common.get_variant_common_columns(
                self.split, self.phenos, None, test_mocked_columns, self.header
            )
        )
        
        self.assertEqual(phenotype, self.split[0])
        self.assertEqual(beta, self.validation_value["beta"])
        self.assertEqual(sebeta, self.validation_value["sebeta"])
        self.assertEqual(maf, self.validation_value["maf"])
        self.assertEqual(maf_case, self.validation_value["maf_case"])
        self.assertEqual(maf_control, self.validation_value["maf_control"])
        self.assertEqual(mlogp, self.validation_value["mlogp"])
        self.assertEqual(pval, self.validation_value["pval"])

    def test_should_return_variant_columns_using_header(self):
        # check get_variant_columns_using_header
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data(0))
        results = tabix_result_common.get_variant_columns_using_header(
            self.split, self.header,test_mocked_columns
        )
        self.assertEqual(len(results), 8)

    def test_should_return_common_pheno_results(self):
        # check get_common_pheno_results
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data(0))
        phenotype, beta, sebeta, maf, maf_case, maf_control, mlogp, pval = (
            tabix_result_common.get_variant_columns_using_header(
                self.split, self.header,test_mocked_columns
            )
        )
        self.assertEqual(phenotype, self.split[0])
        self.assertEqual(beta, self.validation_value["beta"])
        self.assertEqual(sebeta, self.validation_value["sebeta"])
        self.assertEqual(maf, self.validation_value["maf"])
        self.assertEqual(maf_case, self.validation_value["maf_case"])
        self.assertEqual(maf_control, self.validation_value["maf_control"])
        self.assertEqual(mlogp, self.validation_value["mlogp"])
        self.assertEqual(pval, self.validation_value["pval"])
        # check common phenoresults
        common_phenoresults = tabix_result_common.get_common_pheno_results(
            phenotype, pval, beta, sebeta, maf, maf_case, maf_control, mlogp
        )
        self.assertIsNotNone(common_phenoresults)
        self.assertEqual(common_phenoresults.beta, float(self.validation_value["beta"]))
        self.assertEqual(common_phenoresults.sebeta, float(self.validation_value["sebeta"]) )
        self.assertEqual(common_phenoresults.maf, float(self.validation_value["maf"]))
        self.assertEqual(common_phenoresults.maf_case, float(self.validation_value["maf_case"]))
        self.assertEqual(
            common_phenoresults.maf_control, float(self.validation_value["maf_control"])
        )
        self.assertEqual(common_phenoresults.mlogp, float(self.validation_value["mlogp"]))
        self.assertEqual(common_phenoresults.pval, self.validation_value["pval"])

    def test_should_return_common_variant_results_range(self):
        # check get_common_variant_results_range
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data(0))
        variant_results_range = list(tabix_result_common.get_common_variant_results_range(
            self.split_query[0],
            int(self.split_query[1]),
            int(self.split_query[1]),
            test_data_file_path,
            self.header,
            test_mocked_columns,
            None,
            self.phenos,
        ))
        
        self.assertIsNotNone(variant_results_range)
        self.assertEqual(Variant(*self.split_query),variant_results_range[0][0])
        #TODO: test that Phenoresult results are coherent

if __name__ == "__main__":
    unittest.main()
