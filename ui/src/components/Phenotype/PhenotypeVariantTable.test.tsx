import { add_locus_id } from './PhenotypeVariantTable';
import { UnbinnedVariant } from './phenotypeModel';

const testVariant : UnbinnedVariant = {
        af_alt_cases: 0,
        af_alt_controls: 0,
        alt: 'C',
        beta: 0,
        chrom: '3',
        mlogp: 0,
        n_het_cases: 0,
        n_het_controls: 0,
        n_hom_cases: 0,
        n_hom_controls: 0,
        n_hom_ref_cases: 0,
        n_hom_ref_controls: 0,
        nearest_genes: '',
        phenocode: '',
        pos: 101243,
        pval: 0.1,
        ref: 'A',
        rsids: 'r124',
        sebeta: 0
};

test('locus_id', async () => {
        const expected : UnbinnedVariant = { locus_id : "3-101243-A-C", ...testVariant};
        const actual = add_locus_id(testVariant)
        expect(actual).toStrictEqual(expected);
});

test('locus_id undefined', async () => {
        const variant = { ... testVariant, ref : undefined};
        const expected : UnbinnedVariant = { locus_id : "3-101243-undefined-C", ...variant};
        const actual = add_locus_id(variant);
        expect(actual).toStrictEqual(variant);
});