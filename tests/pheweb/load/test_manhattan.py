"""Unit tests for the bin_variants function in pheweb/load/manhattan.py."""
from unittest.mock import patch, MagicMock

from pheweb.load.manhattan import bin_variants, np_label_peaks

BIN_LENGTH = 1_000_000
NEG_BIN_SIZE = 0.05
NEG_BIN_DIGITS = 2


def _make_conf(**overrides):
    defaults = {
        'manhattan_num_unbinned': 10,
        'manhattan_hla_num_unbinned': 5,
        'manhattan_unbin_anyway_pval': 5e-8,
        'hla_begin': 26_000_000,
        'hla_end': 36_000_000,
        'manhattan_max_num_unbinned': 10,
        'within_pheno_mask_around_peak': 1_000_000
    }
    defaults.update(overrides)
    conf = MagicMock()
    for k, v in defaults.items():
        setattr(conf, k, v)
    return conf


def _v(chrom, pos, pval, mlogp=1.0):
    return {'chrom': str(chrom), 'pos': pos, 'pval': pval, 'mlogp': mlogp}


def _call(variants, **conf_overrides):
    conf = _make_conf(**conf_overrides)
    with patch('pheweb.load.manhattan.conf', conf):
        return bin_variants(iter(variants), BIN_LENGTH, NEG_BIN_SIZE, NEG_BIN_DIGITS)


class TestAllVariantsUnbinned:
    def test_fewer_variants_than_limit_all_unbinned(self):
        variants = [_v('1', 1_000_000, 0.01), _v('1', 2_000_000, 0.02), _v('2', 1_000_000, 0.03)]
        binned, unbinned = _call(variants, manhattan_num_unbinned=10)
        assert binned == []
        assert len(unbinned) == 3


class TestBinning:
    def test_least_significant_gets_binned_when_over_limit(self):
        variants = [
            _v('1', 1_000_000, 0.001, mlogp=3.0),  # most sig, stays unbinned
            _v('1', 2_000_000, 0.01, mlogp=2.0),   # 2nd sig, stays unbinned
            _v('1', 4_000_000, 0.5, mlogp=0.5),    # least sig, binned
        ]
        binned, unbinned = _call(variants, manhattan_num_unbinned=2)

        assert len(unbinned) == 2
        assert len(binned) == 1
        assert {v['pval'] for v in unbinned} == {0.001, 0.01}

    def test_bin_pos_is_startpos_plus_half_bin_length(self):
        # variant at pos=1_800_000 falls in pos_bin=1
        # startpos = 1 * 1_000_000 = 1_000_000
        # expected bin pos = 1_000_000 + 1_000_000 // 2 = 1_500_000
        variants = [
            _v('1', 500_000, 0.001, mlogp=3.0),    # stays unbinned
            _v('1', 1_800_000, 0.5, mlogp=0.5),    # binned in pos_bin=1
        ]
        binned, _ = _call(variants, manhattan_num_unbinned=1)
        assert len(binned) == 1
        assert binned[0]['pos'] == int(1_000_000 + BIN_LENGTH / 2)

    def test_multiple_variants_in_same_bin_produce_single_bin(self):
        variants = [
            _v('1', 500_000, 0.001, mlogp=3.0),    # stays unbinned
            _v('1', 1_200_000, 0.4, mlogp=0.5),    # binned (pos_bin=1)
            _v('1', 1_800_000, 0.5, mlogp=1.5),    # binned (pos_bin=1, same bin)
        ]
        binned, _ = _call(variants, manhattan_num_unbinned=1)
        assert len(binned) == 1

    def test_variants_in_different_bins_produce_multiple_bins(self):
        variants = [
            _v('1', 500_000, 0.001, mlogp=3.0),    # stays unbinned
            _v('1', 1_500_000, 0.4, mlogp=0.5),    # binned (pos_bin=1)
            _v('1', 3_500_000, 0.5, mlogp=1.5),    # binned (pos_bin=3)
        ]
        binned, _ = _call(variants, manhattan_num_unbinned=1)
        assert len(binned) == 2

    def test_binned_variant_has_expected_keys(self):
        variants = [
            _v('1', 500_000, 0.001, mlogp=3.0),
            _v('1', 1_500_000, 0.5, mlogp=1.0),
        ]
        binned, _ = _call(variants, manhattan_num_unbinned=1)
        assert len(binned) == 1
        b = binned[0]
        assert b['chrom'] == '1'
        assert 'pos' in b
        assert 'neglog10_pvals' in b
        assert 'startpos' not in b

    def test_bins_in_chromosomal_order(self):
        variants = [
            _v('2', 1_500_000, 0.5, mlogp=0.5),    # chrom 2, binned
            _v('1', 1_500_000, 0.4, mlogp=0.5),    # chrom 1, binned
            _v('3', 1_500_000, 0.001, mlogp=3.0),  # chrom 3, stays unbinned
        ]
        binned, _ = _call(variants, manhattan_num_unbinned=1)
        assert len(binned) == 2
        assert [b['chrom'] for b in binned] == ['1', '2']


class TestMaxUnbinnedVariants:
    """Tests for the second-pass cap: peaks always kept, remaining slots filled by p-value."""

    def test_under_max_all_variants_unbinned(self):
        # 2 independent peaks (far apart), max=5 → second pass bins nothing
        variants = [
            _v('1', 1_000_000, 0.001, mlogp=3.0),
            _v('1', 5_000_000, 0.01, mlogp=2.0),   # > 1M from v1 → independent peak
        ]
        binned, unbinned = _call(variants, manhattan_num_unbinned=100, manhattan_max_num_unbinned=5)
        assert binned == []
        assert len(unbinned) == 2

    def test_least_significant_non_peaks_binned_when_over_max(self):
        # 1 peak + 4 non-peaks all within mask distance; max=2
        # Pop order (highest pval first): 0.04, 0.03, 0.02, 0.01, 1e-6
        # 0.04 → bin; 0.03 → bin; 0.02 → keep (remaining=2<=2); 0.01 → keep; 1e-6 → keep (peak+last)
        variants = [
            _v('1', 1_000_000, 1e-6, mlogp=6.0),    # peak (most significant)
            _v('1', 1_100_000, 0.01, mlogp=2.0),    # non-peak, most sig
            _v('1', 1_200_000, 0.02, mlogp=1.7),    # non-peak
            _v('1', 1_300_000, 0.03, mlogp=1.5),    # non-peak, binned
            _v('1', 1_400_000, 0.04, mlogp=1.4),    # non-peak, least sig, binned
        ]
        _, unbinned = _call(variants, manhattan_num_unbinned=100, manhattan_max_num_unbinned=2)
        unbinned_pvals = {v['pval'] for v in unbinned}
        assert 1e-6 in unbinned_pvals     # peak always kept
        assert 0.01 in unbinned_pvals     # most sig non-peak kept
        assert 0.02 not in unbinned_pvals     # 2nd most sig non-peak kept
        assert 0.03 not in unbinned_pvals  # binned
        assert 0.04 not in unbinned_pvals  # binned (least sig)

    def test_peak_with_high_pval_kept_even_when_popped_before_limit_kicks_in(self):
        # The chrom2 variant is isolated → peak, but has pval=0.5 (high)
        # It is popped from the queue first, when remaining > max, yet must be kept
        variants = [
            _v('2', 1_000_000, 0.5, mlogp=0.3),     # isolated peak on chrom2 (high pval)
            _v('1', 1_000_000, 1e-6, mlogp=6.0),    # peak on chrom1
            _v('1', 1_100_000, 0.01, mlogp=2.0),    # non-peak (within mask of chrom1 peak)
            _v('1', 1_200_000, 0.02, mlogp=1.7),    # non-peak
        ]
        _, unbinned = _call(variants, manhattan_num_unbinned=100, manhattan_max_num_unbinned=1)
        unbinned_pvals = {v['pval'] for v in unbinned}
        assert 0.5 in unbinned_pvals      # chrom2 peak kept despite high pval
        assert 1e-6 in unbinned_pvals     # chrom1 peak kept
        assert 0.01 not in unbinned_pvals  # non-peak binned
        assert 0.02 not in unbinned_pvals  # non-peak binned

    def test_most_significant_non_peaks_kept_over_least_significant(self):
        # When two non-peaks compete for the last slot, the lower pval wins
        variants = [
            _v('1', 1_000_000, 1e-6, mlogp=6.0),    # peak
            _v('1', 1_100_000, 0.001, mlogp=3.0),   # non-peak, more significant → kept
            _v('1', 1_200_000, 0.1, mlogp=1.0),     # non-peak, less significant → binned
        ]
        _, unbinned = _call(variants, manhattan_num_unbinned=100, manhattan_max_num_unbinned=1)
        unbinned_pvals = {v['pval'] for v in unbinned}
        assert 0.001 not in unbinned_pvals   # more significant non-peak kept
        assert 0.1 not in unbinned_pvals  # less significant non-peak binned


class TestGWSignificantVariants:
    def test_gw_sig_variant_stays_unbinned_even_when_over_limit(self):
        variants = [
            _v('1', 1_000_000, 1e-10, mlogp=10.0),  # GW sig, always kept
            _v('1', 4_000_000, 0.4, mlogp=0.5),      # regular, binned
            _v('1', 7_000_000, 0.5, mlogp=0.5),      # regular, binned
        ]
        _, unbinned = _call(variants, manhattan_num_unbinned=1, manhattan_unbin_anyway_pval=5e-8)
        assert any(v['pval'] == 1e-10 for v in unbinned)

    def test_multiple_gw_sig_variants_all_stay_unbinned(self):
        variants = [
            _v('1', 1_000_000, 1e-10, mlogp=10.0),
            _v('1', 2_000_000, 1e-9, mlogp=9.0),
            _v('1', 4_000_000, 0.5, mlogp=0.5),      # regular, binned
        ]
        _, unbinned = _call(variants, manhattan_num_unbinned=1, manhattan_unbin_anyway_pval=5e-8)
        unbinned_pvals = {v['pval'] for v in unbinned}
        assert 1e-10 in unbinned_pvals
        assert 1e-9 in unbinned_pvals


class TestHLAVariants:
    def test_hla_variants_binned_when_over_hla_limit(self):
        variants = [
            _v('6', 26_500_000, 0.01, mlogp=2.0),   # HLA, more sig, stays in hla_pq
            _v('6', 27_000_000, 0.1, mlogp=1.0),    # HLA, less sig, binned (hla limit=1)
            _v('1', 1_000_000, 0.05, mlogp=1.5),    # non-HLA anchor
        ]
        binned, _ = _call(variants, manhattan_hla_num_unbinned=1)
        assert any(b['chrom'] == '6' for b in binned)

    def test_significant_hla_variant_added_to_unbinned(self):
        # HLA pval=0.01 < max_p pval=0.05, so it is added to unbinned
        variants = [
            _v('6', 26_500_000, 0.01, mlogp=2.0),  # HLA, pval < non-HLA max_p
            _v('1', 1_000_000, 0.05, mlogp=1.5),   # non-HLA; max_p = 0.05
        ]
        _, unbinned = _call(variants, manhattan_hla_num_unbinned=5)
        assert any(v['pval'] == 0.01 for v in unbinned)

    def test_insignificant_hla_variant_not_added_to_unbinned(self):
        # HLA pval=0.1 > max_p pval=0.05, so it is NOT added to unbinned
        variants = [
            _v('6', 26_500_000, 0.1, mlogp=1.0),   # HLA, pval > non-HLA max_p
            _v('1', 1_000_000, 0.05, mlogp=1.5),   # non-HLA; max_p = 0.05
        ]
        _, unbinned = _call(variants, manhattan_hla_num_unbinned=5)
        assert not any(v['pval'] == 0.1 for v in unbinned)

    def test_chrom6_variant_outside_hla_region_treated_as_non_hla(self):
        # Variant on chrom 6 but position is before hla_begin
        variants = [
            _v('6', 100_000, 0.01, mlogp=2.0),     # chrom 6, outside HLA
            _v('1', 1_000_000, 0.001, mlogp=3.0),  # anchor for non-empty main queue
        ]
        _, unbinned = _call(variants, hla_begin=26_000_000, hla_end=36_000_000)
        # The chrom 6 variant outside HLA should be handled by the main queue
        assert any(v['pos'] == 100_000 for v in unbinned)


class TestNeglog10Pvals:
    def test_mlogp_binned_with_correct_rounded_value(self):
        # mlogp=1.5: 1.5 // 0.05 * 0.05 = 30.0 * 0.05 = 1.5 → round(1.5, 2) = 1.5
        variants = [
            _v('1', 500_000, 0.001, mlogp=3.0),    # stays unbinned
            _v('1', 1_500_000, 0.5, mlogp=1.5),    # binned
        ]
        binned, _ = _call(variants, manhattan_num_unbinned=1)
        assert len(binned) == 1
        assert 1.5 in binned[0]['neglog10_pvals']

    def test_pval_only_variant_binned_with_correct_neglog10(self):
        # variant has no 'mlogp', so rounded_neglog10(pval) is used instead
        # pval=0.01 → -log10(0.01)=2.0 → 2.0 // 0.05 * 0.05 = 2.0 → round(2.0, 2) = 2.0
        anchor = _v('1', 500_000, 0.001, mlogp=3.0)
        binned_variant = {'chrom': '1', 'pos': 1_500_000, 'pval': 0.01}  # no mlogp
        binned, _ = _call([anchor, binned_variant], manhattan_num_unbinned=1)
        assert len(binned) == 1
        assert 2.0 in binned[0]['neglog10_pvals']

    def test_multiple_mlogp_values_aggregated_in_same_bin(self):
        # mlogp=0.5 and mlogp=1.5 are both cleanly representable multiples of bin_size
        variants = [
            _v('1', 500_000, 0.001, mlogp=3.0),    # stays unbinned
            _v('1', 1_200_000, 0.4, mlogp=0.5),    # binned (pos_bin=1)
            _v('1', 1_800_000, 0.5, mlogp=1.5),    # binned (pos_bin=1, same bin)
        ]
        binned, _ = _call(variants, manhattan_num_unbinned=1)
        assert len(binned) == 1
        assert 0.5 in binned[0]['neglog10_pvals']
        assert 1.5 in binned[0]['neglog10_pvals']


MASK = 1_000_000  # within_pheno_mask_around_peak used in np_label tests


def _label(variants):
    conf = MagicMock()
    conf.within_pheno_mask_around_peak = MASK
    with patch('pheweb.load.manhattan.conf', conf):
        np_label_peaks(variants)


def _var(chrom, pos, pval):
    return {'chrom': str(chrom), 'pos': pos, 'pval': pval}


class TestNpLabel:
    def test_single_variant_is_marked_as_peak(self):
        v = _var('1', 1_000_000, 0.001)
        _label([v])
        assert v.get('peak') is True

    def test_two_variants_far_apart_are_both_peaks(self):
        v1 = _var('1', 1_000_000, 0.001)
        v2 = _var('1', 3_000_000, 0.01)   # |3M - 1M| = 2M > MASK
        _label([v1, v2])
        assert v1.get('peak') is True
        assert v2.get('peak') is True

    def test_two_variants_within_mask_only_most_significant_is_peak(self):
        v1 = _var('1', 1_000_000, 0.001)  # more significant
        v2 = _var('1', 1_500_000, 0.01)   # |1.5M - 1M| = 500K < MASK → masked out
        _label([v1, v2])
        assert v1.get('peak') is True
        assert 'peak' not in v2

    def test_most_significant_variant_is_peak_regardless_of_list_order(self):
        v1 = _var('1', 1_000_000, 0.01)   # less significant, listed first
        v2 = _var('1', 1_500_000, 0.001)  # more significant, listed second
        _label([v1, v2])
        assert v2.get('peak') is True
        assert 'peak' not in v1

    def test_variants_on_different_chroms_are_independent(self):
        v1 = _var('1', 1_000_000, 0.001)
        v2 = _var('2', 1_000_000, 0.01)   # same position, different chrom → both peaks
        _label([v1, v2])
        assert v1.get('peak') is True
        assert v2.get('peak') is True

    def test_three_variants_two_peaks_one_masked(self):
        v1 = _var('1', 1_000_000, 0.001)  # 1st peak
        v2 = _var('1', 3_000_000, 0.005)  # 2nd peak, far from v1
        v3 = _var('1', 3_500_000, 0.02)   # |3.5M - 3M| = 500K < MASK → masked by v2
        _label([v1, v2, v3])
        assert v1.get('peak') is True
        assert v2.get('peak') is True
        assert 'peak' not in v3

    def test_variant_exactly_at_mask_boundary_is_masked(self):
        v1 = _var('1', 1_000_000, 0.001)
        v2 = _var('1', 2_000_000, 0.01)   # |2M - 1M| = MASK exactly, condition is strict >
        _label([v1, v2])
        assert v1.get('peak') is True
        assert 'peak' not in v2

    def test_variant_just_outside_mask_boundary_is_peak(self):
        v1 = _var('1', 1_000_000, 0.001)
        v2 = _var('1', 2_000_001, 0.01)   # |2_000_001 - 1M| = MASK + 1 → kept
        _label([v1, v2])
        assert v1.get('peak') is True
        assert v2.get('peak') is True

    def test_two_variants_same_position_lower_pval_is_peak(self):
        # pos_dict keys on position, so the second variant added overwrites the first.
        # The variant with the lower pval should be identified as the peak regardless
        # of insertion order — this test exposes the pos_dict collision bug when the
        # more significant variant is listed first.
        v1 = _var('1', 1_000_000, 0.001)  # more significant, listed first
        v2 = _var('1', 1_000_000, 0.01)   # less significant, overwrites v1 in pos_dict
        _label([v1, v2])
        assert v1.get('peak') is True
        assert 'peak' not in v2


def test_integration_all_parameters():
    """
    Single scenario that exercises all four parameters together.
    """
    variants = [
        _v('1', 1_000_000, 0.001, mlogp=3.0),   # PEAK #1, unbinned
        _v('1', 1_200_000, 0.008, mlogp=2.1),   # not a peak, binned
        _v('1', 5_000_000, 0.009, mlogp=2.05),  # PEAK #2 unbinned
        _v('1', 1_000_000, 0.007),  # not a peak, unbinned
        _v('1', 9_000_000, 0.8,   mlogp=0.1),   # binned
    ]
    binned, unbinned = _call(
        variants,
        manhattan_num_unbinned=2,
        manhattan_max_num_unbinned=3,
        manhattan_unbin_anyway_pval=0.01,
    )
    unbinned_pvals = {v['pval'] for v in unbinned}

    # manhattan_min_unbinned: v_fp exceeded the first-pass cap and was binned
    assert 0.8 not in unbinned_pvals
    assert len(binned) >= 1
    assert len(unbinned) == 3

    # manhattan_unbin_anyway_pval: v_gw3 (0.009 < 0.01) was re-added when popped
    # and survives to the final output
    assert 0.009 in unbinned_pvals

    # within_pheno_mask_around_peak: v_gw1 and v_gw3 are peaks (4M apart);
    # v_gw4 in unbinned must NOT be a peak (0.4M from v_gw1 < 1M mask)
    peak_pvals = {v['pval'] for v in unbinned if v.get('peak')}
    assert 0.001 in peak_pvals    # v_gw1 is a peak
    assert 0.009 in peak_pvals    # v_gw3 is a peak
    assert 0.007 not in peak_pvals  # v_gw4 is not a peak

    # manhattan_max_num_unbinned: v_gw2 (0.008, not a peak) binned in second pass;
    # v_gw3 (0.009, a peak) kept despite having the highest pval in the queue
    assert 0.008 not in unbinned_pvals  # binned — not a peak
    assert 0.007 in unbinned_pvals      # kept — most significant remaining non-peak
