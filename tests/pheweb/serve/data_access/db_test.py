import gzip
import json
import os
import re
from pheweb.serve.data_access.db import Variant, optional_float, AnnotationDB, ResultDB, TabixResultDao, TabixResultFiltDao, TabixResultCommonDao

# results_db_test.py
import unittest
from unittest.mock import MagicMock

test_data_file_path =  os.getcwd()+ '/tests/mocked-data/mocked.tsv.gz'
test_pheno_list_path =  os.getcwd()+ '/tests/mocked-data/mocked-pheno-list.json'
test_mocked_columns = {'pheno': '#pheno', 'mlogp': 'mlogp', 'beta': 'beta', 'sebeta': 'sebeta', 'maf': 'af_alt', 'maf_cases': 'af_alt_cases', 'maf_controls': 'af_alt_controls'}
test_variant = '1:13668:G:A'

def test_optional_float() -> None:
    """Test optional float.

    @return: None
    """
    assert optional_float(None) is None
    assert optional_float('NA') is None
    assert optional_float('') is None
    assert optional_float('1.0') == 1.0
    assert optional_float(1.0) == 1.0



class TestDBValidatedInterfacesImplemented(unittest.TestCase):
    def test_resultdb_interface_implemented(self):
        self.assertTrue(hasattr(ResultDB, 'get_single_variant_results'), "ResultDB should implement get_single_variant_results")
        self.assertTrue(hasattr(ResultDB, 'get_variant_results_range'), "ResultDB should implement get_variant_results_range")
        self.assertTrue(hasattr(ResultDB, 'get_top_per_pheno_variant_results_range'), "ResultDB should implement get_top_per_pheno_variant_results_range")
        self.assertTrue(hasattr(ResultDB, 'get_variants_results'), "ResultDB should implement get_variants_results")
        self.assertFalse(hasattr(ResultDB, 'not_implemented'), "ResultDB should not implement not_implemented")

    def test_tabixresults_interface_implemented(self):
        self.assertTrue(hasattr(TabixResultDao, 'get_single_variant_results'), "TabixResultDao should implement get_single_variant_results")
        self.assertTrue(hasattr(TabixResultDao, 'get_variant_results_range'), "TabixResultDao should implement get_variant_results_range")
        self.assertTrue(hasattr(TabixResultDao, 'get_top_per_pheno_variant_results_range'), "TabixResultDao should implement get_top_per_pheno_variant_results_range")
        self.assertTrue(hasattr(TabixResultDao, 'get_variants_results'), "TabixResultDao should implement get_variants_results")
        self.assertFalse(hasattr(TabixResultDao, 'not_implemented'), "TabixResultDao should not implement not_implemented")

    def test_tabixresultsfilt_interface_implemented(self):
        self.assertTrue(hasattr(TabixResultFiltDao, 'get_single_variant_results'), "TabixResultFiltDao should implement get_single_variant_results")
        self.assertTrue(hasattr(TabixResultFiltDao, 'get_variant_results_range'), "TabixResultFiltDao should implement get_variant_results_range")
        self.assertTrue(hasattr(TabixResultFiltDao, 'get_top_per_pheno_variant_results_range'), "TabixResultFiltDao should implement get_top_per_pheno_variant_results_range")
        self.assertTrue(hasattr(TabixResultFiltDao, 'get_variants_results'), "TabixResultFiltDao should implement get_variants_results")
        self.assertFalse(hasattr(TabixResultFiltDao, 'not_implemented'), "TabixResultFiltDao should not implement not_implemented")

    def test_tabixresultsfilt_interface_implemented(self):
        self.assertTrue(hasattr(TabixResultCommonDao, 'get_variant_columns_using_header'), "TabixResultCommonDao should implement get_variant_columns_using_header")
        self.assertTrue(hasattr(TabixResultCommonDao, 'get_variant_columns_using_header_offset'), "TabixResultCommonDao should implement get_variant_columns_using_header_offset")
        self.assertTrue(hasattr(TabixResultCommonDao, 'get_variant_common_columns'), "TabixResultCommonDao should implement get_variant_common_columns")
        self.assertTrue(hasattr(TabixResultCommonDao, 'get_common_pheno_results'), "TabixResultCommonDao should implement get_common_pheno_results")
        self.assertFalse(hasattr(TabixResultCommonDao, 'not_implemented'), "TabixResultCommonDao should not implement not_implemented")

    def test_annotationdb_interface_implemented(self):
        self.assertTrue(hasattr(AnnotationDB, 'add_variant_annotations'), "AnnotationDB should implement add_variant_annotations")
        self.assertTrue(hasattr(AnnotationDB, 'add_variant_annotations_range'), "AnnotationDB should implement add_variant_annotations_range")
        self.assertTrue(hasattr(AnnotationDB, 'add_single_variant_annotations'), "AnnotationDB should implement add_single_variant_annotations")
        self.assertTrue(hasattr(AnnotationDB, 'get_gene_functional_variant_annotations'), "AnnotationDB should implement get_gene_functional_variant_annotations")
        self.assertFalse(hasattr(AnnotationDB, 'not_implemented'), "AnnotationDB should not implement not_implemented")


class TestTabixResultFiltDao(unittest.TestCase):
    def setUp(self):
        # Load resources
        with open(test_pheno_list_path, 'r') as f:
            self.mocked_pheno_list_data = json.load(f)
        self.mocked_pheno_list_data = unittest.mock.MagicMock(return_value=self.mocked_pheno_list_data[0])
        self.split_query=re.split('-|:|/|_', test_variant)
        self.variant = Variant( self.split_query[0],  self.split_query[1],  self.split_query[2],  self.split_query[3])

    def test_get_single_variant_results(self):
        # check get_single_variant_results
        tabix_results = TabixResultFiltDao(self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns)
        results = tabix_results.get_single_variant_results(self.variant)
        self.assertTrue(len(results) > 0)
        self.assertTrue(isinstance(results, (list, tuple)))
    
    def should_have_called_get_variants_results(self):
        # check get_variants_results
        tabix_results = TabixResultDao(self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns)
        tabix_results.get_variants_results = unittest.mock.MagicMock()
        tabix_results.get_single_variant_results(self.variant)
        tabix_results.get_variants_results.assert_called_once()
    
    def should_have_called_get_variant_results_range(self):
        # check get_variant_results_range
        tabix_results = TabixResultDao(self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns)
        tabix_results.get_variant_results_range = unittest.mock.MagicMock()
        tabix_results.get_single_variant_results(self.variant)
        tabix_results.get_variant_results_range.assert_called_once()

class TestTabixResultCommonDao(unittest.TestCase):
    def setUp(self):
        # Load resources
        with gzip.open(test_data_file_path, 'r') as f:
            self.data = f.read().splitlines()
        self.header = self.data[0].decode('utf-8').split('\t')
        with open(test_pheno_list_path, 'r') as f:
            self.mocked_pheno_list_data = json.load(f)
        self.mocked_pheno_list_data = unittest.mock.MagicMock(return_value=self.mocked_pheno_list_data[0])
        self.split = self.data[1]
        self.phenos = [
            (h.split("@")[1], p_col_idx)
            for p_col_idx, h in enumerate(self.header)
            if h.startswith("pval")
        ]
        self.split_query=re.split('-|:|/|_', test_variant)
    
    def test_get_variant_common_columns(self):
        # check get_variant_common_columns
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data)
        results = tabix_result_common.get_variant_common_columns(self.split, self.phenos, None, test_mocked_columns, self.header)
        self.assertEqual(len(results), 8)
    
    def test_get_variant_columns_using_header(self):
        # check get_variant_columns_using_header
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data)
        results = tabix_result_common.get_variant_columns_using_header(self.split, self.header)
        self.assertEqual(len(results), 8)
    
    def test_get_common_pheno_results(self):
        # check get_common_pheno_results
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data)
        phenotype, beta, sebeta, maf, maf_case, maf_control, mlogp, pval = tabix_result_common.get_variant_columns_using_header(self.split, self.header)
        self.assertEqual(phenotype, self.split[0])
        common_phenoresults = tabix_result_common.get_common_pheno_results(phenotype, pval, beta, sebeta, maf, maf_case, maf_control, mlogp)
        self.assertIsNotNone(common_phenoresults)

    def test_get_common_variant_results_range(self):
        # check get_common_variant_results_range
        tabix_result_common = TabixResultCommonDao(self.mocked_pheno_list_data)
        variant_results_range = tabix_result_common.get_common_variant_results_range(self.split_query[0], int(self.split_query[1]), int(self.split_query[1]), test_data_file_path, self.header, test_mocked_columns, None, self.phenos)
        self.assertIsNotNone(variant_results_range)


if __name__ == '__main__':
    unittest.main()