import math

import pytest

from pheweb.serve.data_access.autoreporting import AutoreportingDao

PHENO = "AB1_TEST"

# a group report row in the current release format
CURRENT_ROW = {
    "locus_id": "chr6_115999993_T_C",
    "chrom": "6",
    "pos": "115999993",
    "pval": "5e-07",
    "lead_mlogp": "6.3",
    "lead_beta": "0.799",
    "lead_sebeta": "0.1",
    "lead_enrichment": "0.97",
    "lead_af_alt": "0.396",
    "lead_most_severe_gene": "FRK",
    "good_cs": "TRUE",
    "functional_variants_strict": "chr6_116003979_C_T|missense_variant|0.489",
    "credible_set_variants": "chr6_115999993_T_C|0.0437",
    "cs_size": "12",
    "cs_log_bayes_factor": "5.5",
    "specific_efo_trait_associations_strict": "EFO_A",
    "specific_efo_trait_associations_relaxed": "EFO_B",
    "found_associations_strict": "trait_a|0.99",
    "found_associations_relaxed": "trait_b|0.98",
}

# the same locus in the R5 format: older column names and fewer columns
R5_ROW = {
    "locus_id": "chr6_115999993_T_C",
    "chr": "6",
    "start": "115685530",
    "end": "116490701",
    "enrichment": "0.97",
    "most_severe_gene": "FRK",
    "lead_pval": "5e-07",
    "lead_beta": "0.799",
    "lead_AF": "0.396",
    "found_associations_strict": "trait_a|0.99",
    "found_associations_relaxed": "trait_b|0.98",
    "credible_set_variants": "chr6_115999993_T_C|0.0437",
    "functional_variants_strict": "",
}

R5_COLUMNS = {
    "chrom": "chr",
    "pval": "lead_pval",
    "lead_enrichment": "enrichment",
    "lead_af_alt": "lead_AF",
    "lead_most_severe_gene": "most_severe_gene",
    "pos": None,
    "lead_mlogp": None,
    "lead_sebeta": None,
    "good_cs": None,
    "cs_size": None,
    "cs_log_bayes_factor": None,
}


def write_report(directory, rows, pheno=PHENO):
    header = list(rows[0].keys())
    lines = ["\t".join(header)] + ["\t".join(row[h] for h in header) for row in rows]
    (directory / f"{pheno}.top.out").write_text("\n".join(lines) + "\n")


def make_dao(tmp_path, columns=None):
    auth_file = tmp_path / "mysql.conf"
    auth_file.write_text(
        'mysql = {"user": "user", "password": "password", "host": "localhost", "db": "db", "release": 5}\n'
    )
    report_dir = tmp_path / "group_reports"
    report_dir.mkdir(exist_ok=True)
    return AutoreportingDao(str(auth_file), str(report_dir), columns=columns), report_dir


def test_current_format_without_column_mapping(tmp_path):
    dao, report_dir = make_dao(tmp_path)
    write_report(report_dir, [CURRENT_ROW])
    assert dao.get_group_report(PHENO) == [{
        "chrom": "6",
        "pos": "115999993",
        "pval": 5e-07,
        "locus_id": "chr6_115999993_T_C",
        "phenocode": PHENO,
        "good_cs": True,
        "lead_enrichment": 0.97,
        "lead_af_alt": 0.396,
        "lead_most_severe_gene": "FRK",
        "lead_mlogp": 6.3,
        "lead_beta": 0.799,
        "lead_sebeta": "0.1",
        "functional_variants_strict": "chr6_116003979_C_T|missense_variant|0.489",
        "credible_set_variants": "chr6_115999993_T_C|0.0437",
        "cs_size": 12,
        "cs_log_bayes_factor": 5.5,
        "all_traits_strict": "EFO_A;trait_a|0.99",
        "all_traits_relaxed": "EFO_B;trait_b|0.98",
    }]


def test_missing_report_file_returns_empty_list(tmp_path):
    dao, _ = make_dao(tmp_path)
    assert dao.get_group_report("NOT_A_PHENO") == []


def test_one_record_per_row(tmp_path):
    dao, report_dir = make_dao(tmp_path)
    second = {**CURRENT_ROW, "locus_id": "chr9_79277891_G_C", "chrom": "9"}
    write_report(report_dir, [CURRENT_ROW, second])
    records = dao.get_group_report(PHENO)
    assert [r["locus_id"] for r in records] == ["chr6_115999993_T_C", "chr9_79277891_G_C"]


def test_empty_values_are_reported_as_na(tmp_path):
    dao, report_dir = make_dao(tmp_path)
    write_report(report_dir, [{**CURRENT_ROW, "functional_variants_strict": "", "lead_sebeta": ""}])
    record = dao.get_group_report(PHENO)[0]
    assert record["functional_variants_strict"] == "NA"
    assert record["lead_sebeta"] == "NA"


def test_na_numeric_values_are_nan(tmp_path):
    dao, report_dir = make_dao(tmp_path)
    write_report(report_dir, [{**CURRENT_ROW, "lead_enrichment": "NA", "lead_af_alt": "NA",
                               "cs_log_bayes_factor": "NA", "cs_size": "NA"}])
    record = dao.get_group_report(PHENO)[0]
    for key in ["lead_enrichment", "lead_af_alt", "cs_log_bayes_factor", "cs_size"]:
        assert math.isnan(record[key]), key


def test_trait_merge_skips_missing_entries(tmp_path):
    dao, report_dir = make_dao(tmp_path)
    write_report(report_dir, [{**CURRENT_ROW,
                               "specific_efo_trait_associations_strict": "NA",
                               "found_associations_strict": "trait_a|0.99",
                               "specific_efo_trait_associations_relaxed": "",
                               "found_associations_relaxed": "NA"}])
    record = dao.get_group_report(PHENO)[0]
    assert record["all_traits_strict"] == "trait_a|0.99"
    assert record["all_traits_relaxed"] == "NA"


def test_found_associations_used_without_specific_efo_columns(tmp_path):
    dao, report_dir = make_dao(tmp_path)
    row = {k: v for k, v in CURRENT_ROW.items() if not k.startswith("specific_efo_trait_associations")}
    write_report(report_dir, [row])
    record = dao.get_group_report(PHENO)[0]
    assert record["all_traits_strict"] == "trait_a|0.99"
    assert record["all_traits_relaxed"] == "trait_b|0.98"


def test_renamed_columns_are_read_through_mapping(tmp_path):
    columns = {"chrom": "chr", "pval": "lead_pval"}
    dao, report_dir = make_dao(tmp_path, columns)
    row = {("chr" if k == "chrom" else "lead_pval" if k == "pval" else k): v for k, v in CURRENT_ROW.items()}
    write_report(report_dir, [row])
    record = dao.get_group_report(PHENO)[0]
    assert record["chrom"] == "6"
    assert record["pval"] == 5e-07


def test_r5_format_with_column_mapping(tmp_path):
    dao, report_dir = make_dao(tmp_path, R5_COLUMNS)
    write_report(report_dir, [R5_ROW])
    record = dao.get_group_report(PHENO)[0]
    assert record["chrom"] == "6"
    assert record["pval"] == 5e-07
    assert record["lead_enrichment"] == 0.97
    assert record["lead_af_alt"] == 0.396
    assert record["lead_most_severe_gene"] == "FRK"
    assert record["lead_beta"] == 0.799
    assert record["functional_variants_strict"] == "NA"
    assert record["all_traits_strict"] == "trait_a|0.99"
    assert record["all_traits_relaxed"] == "trait_b|0.98"


def test_columns_mapped_to_none_are_na(tmp_path):
    dao, report_dir = make_dao(tmp_path, R5_COLUMNS)
    write_report(report_dir, [R5_ROW])
    record = dao.get_group_report(PHENO)[0]
    assert record["pos"] == "NA"
    assert record["lead_sebeta"] == "NA"
    assert record["good_cs"] == "NA"
    assert math.isnan(record["cs_size"])
    assert math.isnan(record["cs_log_bayes_factor"])


def test_columns_mapped_to_none_are_na_even_if_present(tmp_path):
    dao, report_dir = make_dao(tmp_path, {"lead_sebeta": None})
    write_report(report_dir, [CURRENT_ROW])
    assert dao.get_group_report(PHENO)[0]["lead_sebeta"] == "NA"


def test_specific_efo_columns_mapped_to_none_use_found_associations(tmp_path):
    columns = {"specific_efo_trait_associations_strict": None,
               "specific_efo_trait_associations_relaxed": None}
    dao, report_dir = make_dao(tmp_path, columns)
    write_report(report_dir, [CURRENT_ROW])
    record = dao.get_group_report(PHENO)[0]
    assert record["all_traits_strict"] == "trait_a|0.99"
    assert record["all_traits_relaxed"] == "trait_b|0.98"


def test_missing_unmapped_column_raises(tmp_path):
    dao, report_dir = make_dao(tmp_path)
    write_report(report_dir, [R5_ROW])
    with pytest.raises(KeyError):
        dao.get_group_report(PHENO)


def test_partial_mapping_raises_for_remaining_missing_column(tmp_path):
    columns = {k: v for k, v in R5_COLUMNS.items() if k != "cs_size"}
    dao, report_dir = make_dao(tmp_path, columns)
    write_report(report_dir, [R5_ROW])
    with pytest.raises(KeyError, match="cs_size"):
        dao.get_group_report(PHENO)


def test_unknown_column_in_mapping_raises(tmp_path):
    with pytest.raises(ValueError, match="pvals"):
        make_dao(tmp_path, {"pvals": "lead_pval"})


def test_lead_mlogp_computed_from_pval_when_not_available(tmp_path):
    dao, report_dir = make_dao(tmp_path, R5_COLUMNS)
    write_report(report_dir, [R5_ROW])
    assert dao.get_group_report(PHENO)[0]["lead_mlogp"] == pytest.approx(-math.log10(5e-07))


def test_lead_mlogp_computed_from_pval_when_na(tmp_path):
    dao, report_dir = make_dao(tmp_path)
    write_report(report_dir, [{**CURRENT_ROW, "lead_mlogp": "NA", "pval": "1e-08"}])
    assert dao.get_group_report(PHENO)[0]["lead_mlogp"] == pytest.approx(8.0)


def test_lead_mlogp_is_inf_for_zero_pval(tmp_path):
    dao, report_dir = make_dao(tmp_path, R5_COLUMNS)
    write_report(report_dir, [{**R5_ROW, "lead_pval": "0"}])
    assert dao.get_group_report(PHENO)[0]["lead_mlogp"] == float("inf")


def test_lead_mlogp_stays_nan_without_pval(tmp_path):
    dao, report_dir = make_dao(tmp_path, R5_COLUMNS)
    write_report(report_dir, [{**R5_ROW, "lead_pval": "NA"}])
    assert math.isnan(dao.get_group_report(PHENO)[0]["lead_mlogp"])


def test_existing_lead_mlogp_is_not_overwritten(tmp_path):
    dao, report_dir = make_dao(tmp_path)
    write_report(report_dir, [{**CURRENT_ROW, "lead_mlogp": "320", "pval": "1e-08"}])
    assert dao.get_group_report(PHENO)[0]["lead_mlogp"] == 320.0
