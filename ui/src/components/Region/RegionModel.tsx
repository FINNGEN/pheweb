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

export interface Params {
	allData: { type: layout_types; data: unknown; conditioned_on: string }[];
	fields: unknown;
	outnames: unknown;
	trans: unknown;
	dataIndex: number;
	lookup: { [key: string]: number };
	handlers: ((position: number | undefined) => void)[] | undefined;
}

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
	}

	export interface Configuration {
		readonly vs_configuration?: VisConfiguration;
		readonly lz_configuration?: LzConfiguration;
		readonly colocalization? : ColocalizationConfiguration | null; // null will hide the colocalization list
	}
}
export type layout_types =
	| 'finemap'
	| 'susie'
	| 'association'
	| 'genes'
	| 'clinvar'
	| 'gwas_cat'
	| 'colocalization'
	| 'conditional';

export interface CondFMRegions {
	chr: number;
	end: number;
	n_signals: number;
	n_signals_prob: number;
	path: string;
	start: number;
	type: layout_types;
	variants: string;
}

export type regions_summaries = RegionSummary[] | undefined | null;

export interface SusieRegion {
	alt:        string;
	chr:        number;
	cs:         number;
	id:         string;
	low_purity: number;
	maf:        number | null;
	position:   number;
	prob:       number;
	ref:        string;
	rsid:       string;
}

export interface FinemapRegion {
	alt:      string;
	chr:      number;
	cs:       number;
	id:       string;
	position: number;
	prob:     number;
	ref:      string;
}
export interface ConditionedRegion {
	alt:      string;
	beta:     number;
	chr:      number;
	end:      number;
	id:       string;
	maf:      number;
	position: number;
	pvalue:   number;
	ref:      string;
	sebeta:   number;
	varid:    string;
}

export type FinemappingRegion = SusieRegion | FinemapRegion | ConditionedRegion;

export type RegionSummaryType = 'susie' | 'finemap' | 'conditional'

export interface RegionSummaryFunctor<R extends FinemappingRegion, T extends RegionSummaryType> {
	chr: number;
	end: number;
	lead_variants: R[];
	n_signals: number;
	n_signals_prob: number;
	start: number;
	type: T;
}

export type RegionSummarySusie = RegionSummaryFunctor<SusieRegion,'susie'>;
export type RegionSummaryFinemap = RegionSummaryFunctor<FinemapRegion,'finemap'>;
export type RegionSummaryConditional = RegionSummaryFunctor<ConditionedRegion,'conditional'>;

export type RegionSummary = RegionSummarySusie | RegionSummaryFinemap | RegionSummaryConditional;

export  interface RegionDescription {
	chromosome: number;
	start:      number;
	stop:       number;
}

export interface Region {
	phenotype:      Phenotype;
	region:         RegionDescription;
	region_summary: RegionSummary[];
}