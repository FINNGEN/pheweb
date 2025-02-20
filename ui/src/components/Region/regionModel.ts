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

	export interface VariantPopup {
		finemap_popup? : string
		susie_popup? : string
		conditional_popup? : string
	}
	export interface Configuration {
		readonly vs_configuration?: VisConfiguration;
		readonly lz_configuration?: LzConfiguration;
		readonly colocalization? : ColocalizationConfiguration | null; // null will hide the colocalization list
		readonly variant_popup? : VariantPopup | null;
	}
}

export namespace Summary {

	export interface CPRA {
		chr:        number;
		position : number;
		ref: string;
		alt:        string;
	}

	export interface SusieCredibleSet extends  CPRA{
		id: string
		low_purity: 0 | 1;
		maf?: number;
		prob : number;
		cs:         number;
		rsid:       string;
	}

	export interface FinemapCredibleSet extends  CPRA {
		cs:       number;
		prob:     number;
        id:       string;
	}

	export interface ConditionedCredibleSet extends  CPRA  {
		beta:     number;
		end:      number;
		id:       string;
		maf:      number;
		pvalue:   number;
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


	export const isCredibleSetSummaryConditional = (cs: CredibleSetSummary<RegionSummaryType>): cs is CredibleSetSummaryConditional =>
		cs.type === 'conditional';
	export const isCredibleSetSummarySusie = (cs: CredibleSetSummary<RegionSummaryType>): cs is CredibleSetSummarySusie =>
		cs.type === 'susie';


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
