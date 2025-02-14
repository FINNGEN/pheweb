import { Locus, locusFromStr } from '../../common/commonModel';
import { VisConfiguration } from '../Configuration/configurationModel';
import { Phenotype } from './../../common/commonModel';
import { ColocalizationConfiguration } from './Colocalization/ColocalizationModel';

export type DataSourceKeys =
	| 'association'
	| 'conditional'
	| 'finemapping'
	| 'colocalization'
	| 'gene'
	| 'constraint'
	| 'gwas_cat'
	| 'clinvar'
	| 'ld'
	| 'recomb';


export interface RegionParams<regionType = string> {
	readonly locus: regionType;
	readonly phenotype: string;
}

export const createParameter = (
	parameter: RegionParams | undefined,
): RegionParams<Locus> | undefined => {
	const locus: Locus | undefined = locusFromStr(parameter?.locus);
	return locus ? { phenotype: parameter?.phenotype, locus } : undefined;
};

export namespace RegionModel {
	export interface LzConfiguration {
		readonly p_threshold: number;
		readonly assoc_fields: {
			readonly quantitative : Array<string>;
			readonly binary : Array<string>;
		};
		readonly ld_ens_pop: string;
		readonly ld_ens_window: number;
		readonly ld_max_window: number;
		readonly ld_service: string;
		readonly prob_threshold: number;
		readonly ld_panel_version: string;
		readonly tooltip_html: string;
		readonly showClinvar: boolean; // clinvar needs to be turned off when developing locally
	}

	export interface Configuration {
		readonly vs_configuration?: VisConfiguration;
		readonly lz_configuration?: LzConfiguration;
		readonly colocalization? : ColocalizationConfiguration | null; // null will hide the colocalization list
	}
}

export namespace Summary {

	export interface SusieCredibleSet {
		id: string
		low_purity: 0 | 1;
		position : number
		prob : number
		ref: string
		alt:        string;
		chr:        number;
		cs:         number;
		rsid:       string;
	}

	export interface FinemapCredibleSet {
		alt:      string;
		chr:      number;
		cs:       number;
		prob:     number;
		ref:      string;
        id:       string;
		position : number;
	}

	export interface ConditionedCredibleSet {
		alt:      string;
		beta:     number;
		chr:      string;
		end:      number;
		id:       string;
		maf:      number;
		position: number;
		pvalue:   number;
		ref:      string;
		sebeta:   number;
		varid:    string;
	}




	export type FinemappingCS = SusieCredibleSet | FinemapCredibleSet | ConditionedCredibleSet;

	export type RegionSummaryType = 'susie' | 'finemap' | 'conditional'

	type RegionTypeToCredibleSet<T extends RegionSummaryType> =
       T extends 'susie' ? SusieCredibleSet :
       T extends 'finemap' ? FinemapCredibleSet :
       T extends 'conditional' ? ConditionedCredibleSet :
       never;

	export type CredibleSetSummaryDetails<R extends FinemappingCS, T extends RegionSummaryType> = {
		lead_variants: R[];
		n_signals: number;
		n_signals_prob: number;
		type: T;
		chr: string;
		start: number;
		end : number;
	}  & (T extends 'conditional' ? { conditioned_on: string[] } : {});


	export type CredibleSetSummary<T extends RegionSummaryType> = CredibleSetSummaryDetails<RegionTypeToCredibleSet<T>, T>;
	export type CredibleSetSummarySusie = CredibleSetSummary<'susie'>;
	export type CredibleSetSummaryFinemap = CredibleSetSummary<'finemap'>;
	export type CredibleSetSummaryConditional = CredibleSetSummary<'conditional'>;

	export type RegionSummary = {
		       location : Locus;
		       region_id : string;
		       credible_sets : CredibleSetSummary<RegionSummaryType>[]
	}

	export interface Region {
		readonly phenotype: Phenotype;
		region:         Locus;
		region_summary: RegionSummary[];
	}
}

export namespace  Locuszoom {

	export type layout_types =
		| 'finemap'
		| 'susie'
		| 'association'
		| 'genes'
		| 'clinvar'
		| 'gwas_cat'
		| 'colocalization'
		| 'conditional';

	export interface Params {
		allData: { type: layout_types; data: unknown; conditioned_on: string; region?: string }[];
		fields: unknown;
		outnames: unknown;
		trans: unknown;
		dataIndex: number;
		lookup: { [key: string]: number };
		handlers: ((position: number | undefined) => void)[] | undefined;
	}
}
