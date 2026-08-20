import gzip
import json
import os
import re
from pheweb.serve.data_access.db import (
    Variant,
    PhenoResult,
    PhenoResults,
    optional_float,
    TabixResultLongDao
)
import unittest
import pytest

test_data_file_path = os.getcwd() + "/tests/mocked-data/mocked_data_long.tsv.gz"
test_pheno_list_path = os.getcwd() + "/tests/mocked-data/mocked-pheno-list.json"
mock_sites_file_path = os.getcwd() + "/tests/mocked-data/sites_mocked.tsv.gz"

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
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
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
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )
        variant = Variant("1", "13670", "G", "A")
        results = tabix_results.get_single_variant_results(variant)
        self.assertTrue(len(results) > 0)
        self.assertTrue(isinstance(results, (list, tuple)))
        self.assertEqual(results[0], variant)
        variant_results = results[1]
        self.assertEqual(len(variant_results), 5)
        self.assertTrue(
            len(self.pheno_list_data[0][variant_results[0].phenocode]) > 0
        )
        self.validate_phenoresult(variant_results[0], expected_phenoresults[2])

    def test_single_should_return_none_if_variant_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )
        variant_not_found = Variant("1", "13668", "G", "C")
        results = tabix_results.get_single_variant_results(variant_not_found)
        self.assertEqual(results, None)

    def test_variants_results_returns_empty_list_if_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )
        variant_not_found = Variant("1", "13668", "G", "C")
        results = tabix_results.get_variants_results([variant_not_found])
        self.assertEqual(results, [])
    
    def test_variants_results_returns_empty_list_if_chromosome_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )
        variant_not_found = Variant("25", "13668", "G", "C")
        results = tabix_results.get_variants_results([variant_not_found])
        self.assertEqual(results, [])

    def test_variant_range_returns_empty_list_if_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )
        results = tabix_results.get_variant_results_range("1", 10000, 13667)
        self.assertEqual(results, [])

    def test_top_pheno_per_range_returns_empty_list_if_not_found(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )
        results = tabix_results.get_top_per_pheno_variant_results_range("1", 13678, 13680)
        self.assertEqual(results, [])

    def test_top_pheno_per_range_returns_correct_results(self):
        """There are three variants for AB1_DIBTHERIA in the test data, and we
        want to make sure that the one with lowest p in the range is found"""
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
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

    def test_top_pheno_per_range_is_ordered_most_significant_first(self):
        """Issue #656: the gene page picks phenotypes[0] for its LocusZoom plot.
        In the mocked data AB1_ASPERGILLOSIS sits at the first position in the
        range but is the least significant, so tabix order and significance
        order disagree."""
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )
        results = tabix_results.get_top_per_pheno_variant_results_range("1", 13668, 13675)
        self.assertEqual(
            [res.assoc.phenocode for res in results],
            ['AB1_DIBTHERIA', 'CAMPYLOENTERITIS',
             'CD2_BENIGN_ANUS_ANAL_CANAL', 'AB1_ASPERGILLOSIS'],
        )
        mlogps = [res.assoc.mlogp for res in results]
        self.assertEqual(mlogps, sorted(mlogps, reverse=True))

    def test_get_multiple_variants_results(self):
        var1 = Variant("1", "13668", "G", "A")
        var2 = Variant("1", "13677", "G", "A")
        no_results_var = Variant("1", "13680", "G", "A")
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )
        results = tabix_results.get_variants_results([var1, var2, no_results_var])
        self.assertEqual(len(results), 2)
        self.assertIn(var1, [r[0] for r in results])
        self.assertIn(var2, [r[0] for r in results])
        for res in results:
            if res[0] == var1:
                self.assertEqual(len(res[1]), 5)
            elif res[0] == var2:
                self.assertEqual(len(res[1]), 5)
            else:
                self.fail("Result variants don't match the input")
    
    def test_get_variant_range(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
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

    def test_add_extra_attr(self):
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
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
        tabix_results._add_extra_columns(row, phenoresult)
        self.assertEqual(phenoresult.extra_col1, "extra_value1")
        self.assertEqual(phenoresult.extra_col2, "extra_value2")
        # Make sure standard columns are not added as extra attributes
        self.assertEqual(phenoresult.beta, 1.0)

    def test_existing_variant_found(self):
        variant = Variant("1", "14842", "G", "T")
        dao = TabixResultLongDao(self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path)
        self.assertTrue(dao._variant_exists(variant))
    
    def test_non_existing_variant_not_found(self):
        variant = Variant("1", "14842", "G", "A")
        dao = TabixResultLongDao(self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns,mock_sites_file_path)
        self.assertFalse(dao._variant_exists(variant))
    
    def test_non_existing_chromosome_returns_false(self):
        variant = Variant("25", "14842", "G", "T")
        dao = TabixResultLongDao(self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns,mock_sites_file_path)
        self.assertFalse(dao._variant_exists(variant))

    def test_variant_corner_cases(self):
        one_before = Variant("1", "14841", "G", "A")
        variant = Variant("1", "14842", "G", "T")
        one_after = Variant("1", "14843", "G", "A")
        
        dao = TabixResultLongDao(self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns,mock_sites_file_path)
        self.assertFalse(dao._variant_exists(one_before))
        self.assertTrue(dao._variant_exists(variant))
        self.assertFalse(dao._variant_exists(one_after))
    
    def test_single_variant_in_sites_without_phenos_returns_placeholders(self):
        variant = Variant("1", "14842", "G", "T")
        dao = TabixResultLongDao(self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path)
        results = dao.get_single_variant_results(variant)
        self.assertEqual(results[0], variant)
        self.assertEqual(len(results[1]), 5)
        for res in results[1]:
            self.assertEqual(res.mlogp, None)
            self.assertEqual(res.pval, None)
            self.assertEqual(res.beta, None)
            self.assertEqual(res.sebeta, None)
            self.assertEqual(res.maf, None)
            self.assertEqual(res.maf_case, None)
            self.assertEqual(res.maf_control, None)

    def test_chromosome_X_Y(self):
        # This tests the translations from letter to numbers in chromosome names. X exists in the data, Y does not.
        tabix_results = TabixResultLongDao(
            self.mocked_pheno_list_data, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )
        results_x = tabix_results.get_variant_results_range("X", 10000, 20000)
        assert len(results_x) == 1
        assert results_x[0][0].chr == 23
        results_23 = tabix_results.get_variant_results_range("23", 10000, 20000)
        assert len(results_23) == 1
        assert results_23[0][0].chr == 23
        results_y = tabix_results.get_variant_results_range("Y", 10000, 20000)
        assert len(results_y) == 0
        results_24 = tabix_results.get_variant_results_range("24", 10000, 20000)
        assert len(results_24) == 0


class TestSignificanceKey(unittest.TestCase):
    def make_result(self, phenocode, mlogp, pval=None):
        return PhenoResult(phenocode, 'a phenotype', 'a category', 1, pval,
                           None, None, None, None, None, 1, 1, mlogp)

    def test_more_significant_sorts_first(self):
        self.assertLess(self.make_result('STRONG', 10.0, 1e-10).significance_key,
                        self.make_result('WEAK', 1.0, 0.1).significance_key)

    def test_missing_pvalue_sorts_last(self):
        self.assertLess(self.make_result('WEAK', 0.0, 1.0).significance_key,
                        self.make_result('MISSING', None).significance_key)

    def test_equal_mlogp_breaks_tie_on_pval(self):
        self.assertLess(self.make_result('SMALLER_P', 2.0, 0.001).significance_key,
                        self.make_result('LARGER_P', 2.0, 0.05).significance_key)

    def test_equal_mlogp_sorts_absent_pval_after_present_pval(self):
        """The p-value slot needs its own missing-value sentinel: when two
        results tie on mlogp, the one with no p-value at all must not win the
        tiebreak. Without the sentinel this comparison raises TypeError."""
        self.assertLess(self.make_result('HAS_P', 5.0, 1e-05).significance_key,
                        self.make_result('NO_P', 5.0, None).significance_key)

    def test_full_ties_compare_equal(self):
        """Matches the two-pass stable sort this replaced: results tied on both
        mlogp and pval keep the order they were discovered in."""
        self.assertEqual(self.make_result('ZEBRA', 2.0, 0.01).significance_key,
                         self.make_result('ALPHA', 2.0, 0.01).significance_key)


class TestTopPerPhenoOrdering(unittest.TestCase):
    """Issue #656: get_top_per_pheno_variant_results_range must return results
    most significant first, because the gene page takes phenotypes[0] as the
    default LocusZoom phenotype (ui/src/components/Gene/GeneContext.tsx)."""

    def setUp(self):
        with open(test_pheno_list_path, "r") as f:
            self.pheno_map = json.load(f)[0]
        self.tabix_results = TabixResultLongDao(
            lambda x: self.pheno_map, test_data_file_path, test_mocked_columns, mock_sites_file_path
        )

    def make_pheno_result(self, phenocode, mlogp, pval=None):
        pheno = self.pheno_map[phenocode]
        return PhenoResult(phenocode, pheno['phenostring'], pheno['category'],
                           pheno.get('category_index', 0), pval, None, None, None,
                           None, None, pheno['num_cases'], pheno['num_controls'], mlogp)

    def stub_range_results(self, *phenocode_mlogp_pval):
        """Drive the method under test with synthetic per-variant results.

        The tabix fixture only has an mlogp column, so a row with no p-value at
        all cannot be expressed in it -- get_p_and_mlogp raises ValueError on a
        bare 'NA', and derives pval from mlogp whenever mlogp is present. So the
        missing-p-value orderings can only be reached by feeding results in
        directly. One variant per phenotype, in the order given.
        """
        rows = [
            (Variant("1", 13700 + i, "G", "A"), [self.make_pheno_result(*args)])
            for i, args in enumerate(phenocode_mlogp_pval)
        ]
        self.tabix_results.get_variant_results_range = lambda chrom, start, end: rows

    def phenocodes_from_range(self):
        results = self.tabix_results.get_top_per_pheno_variant_results_range("1", 13700, 13800)
        self.assertIsInstance(results, list, "callers index into this, so it must not be a dict view")
        return [res.assoc.phenocode for res in results]

    def test_orders_most_significant_first_regardless_of_input_order(self):
        """The results arrive in chromosomal order, which is unrelated to
        significance. Hand them over least significant first."""
        self.stub_range_results(
            ('AB1_ASPERGILLOSIS', 1.0, 0.1),
            ('CAMPYLOENTERITIS', 2.0, 0.01),
            ('CD2_BENIGN_ANUS_ANAL_CANAL', 3.0, 0.001),
            ('AB1_DIBTHERIA', 8.0, 1e-08),
        )
        self.assertEqual(self.phenocodes_from_range(),
                         ['AB1_DIBTHERIA', 'CD2_BENIGN_ANUS_ANAL_CANAL',
                          'CAMPYLOENTERITIS', 'AB1_ASPERGILLOSIS'])

    def test_orders_result_with_no_pvalue_last(self):
        """A phenotype with neither mlogp nor pval must never be picked as the
        default LocusZoom phenotype, even when it is discovered first."""
        self.stub_range_results(
            ('AB1_ASPERGILLOSIS', None, None),
            ('CAMPYLOENTERITIS', 1.0, 0.1),
            ('AB1_DIBTHERIA', 8.0, 1e-08),
        )
        self.assertEqual(self.phenocodes_from_range(),
                         ['AB1_DIBTHERIA', 'CAMPYLOENTERITIS', 'AB1_ASPERGILLOSIS'])

    def test_breaks_mlogp_ties_on_pvalue(self):
        self.stub_range_results(
            ('CAMPYLOENTERITIS', 2.0, 0.05),
            ('AB1_DIBTHERIA', 2.0, 0.001),
        )
        self.assertEqual(self.phenocodes_from_range(),
                         ['AB1_DIBTHERIA', 'CAMPYLOENTERITIS'])

    def test_breaks_mlogp_ties_after_results_missing_a_pvalue(self):
        """Ties on mlogp where one result has no p-value to break the tie with.
        Not reachable through the tabix reader, which always derives one, but
        the ordering must stay total rather than raising TypeError."""
        self.stub_range_results(
            ('CAMPYLOENTERITIS', 2.0, None),
            ('AB1_DIBTHERIA', 2.0, 0.001),
        )
        self.assertEqual(self.phenocodes_from_range(),
                         ['AB1_DIBTHERIA', 'CAMPYLOENTERITIS'])

    def test_keeps_the_most_significant_variant_of_a_phenotype(self):
        """The top variant per phenotype is independent of the order the
        variants are met in: a later, less significant variant is ignored."""
        self.stub_range_results(
            ('AB1_DIBTHERIA', 8.0, 1e-08),
            ('AB1_DIBTHERIA', 1.0, 0.1),
            ('CAMPYLOENTERITIS', 2.0, 0.01),
        )
        results = self.tabix_results.get_top_per_pheno_variant_results_range("1", 13700, 13800)
        self.assertEqual([res.assoc.phenocode for res in results],
                         ['AB1_DIBTHERIA', 'CAMPYLOENTERITIS'])
        self.assertEqual(results[0].assoc.mlogp, 8.0)
        self.assertEqual(results[0].variant.pos, 13700)

    def test_full_ties_keep_discovery_order(self):
        """Reproduces the stability of the two-pass sort this replaced."""
        self.stub_range_results(
            ('CAMPYLOENTERITIS', 2.0, 0.01),
            ('AB1_DIBTHERIA', 2.0, 0.01),
        )
        self.assertEqual(self.phenocodes_from_range(),
                         ['CAMPYLOENTERITIS', 'AB1_DIBTHERIA'])

    def test_sort_by_significance_orders_a_bare_list(self):
        least, most = (
            PhenoResults(pheno=self.pheno_map['CAMPYLOENTERITIS'],
                         assoc=self.make_pheno_result('CAMPYLOENTERITIS', 1.0, 0.1),
                         variant=[]),
            PhenoResults(pheno=self.pheno_map['AB1_DIBTHERIA'],
                         assoc=self.make_pheno_result('AB1_DIBTHERIA', 8.0, 1e-08),
                         variant=[]),
        )
        self.assertEqual(PhenoResults.sort_by_significance([least, most]), [most, least])
        self.assertEqual(PhenoResults.sort_by_significance([]), [])
