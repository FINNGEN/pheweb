// text
const aboutBanner = `
     <h1>About this site</h1><br>
     <p>
     The genetic association results on this website are from the FinnGen 
     study. These results are from 2,466 binary endpoints and 3 quantitative 
     endpoints (HEIGHT_IRN, WEIGHT_IRN, BMI_IRN) from data freeze 12 (October 2023), 
     consisting of 500,348 individuals.
     </p>
     <p>
     This site was built with PheWeb
     (<a href="https://github.com/statgen/pheweb/">original repository</a>,
      <a href="https://github.com/FINNGEN/pheweb/">Finngen repository</a>).
      All positions are on GRCh38.
     </p>
     <p>
     Questions? Drop us a line humgen-servicedesk@helsinki.fi
     </p>
`
const notFoundEntityMessage = `
    <p>The endpoint <i>'{{query}}'</i> does not exist.</p>

    <p>
    Please check the spelling first. Note that redundant
    and non-meaningful endpoints have been omitted from analyses.
    </p>

    <p>
    Check the omitted endpoints in
    <a href="https://www.finngen.fi/en/researchers/clinical-endpoints">https://www.finngen.fi/en/researchers/clinical-endpoints</a>
    </p>
  </div>
    `
const notFoundPageMessage = `
    <p>The page <i>'{{query}}'</i> could not be found.</p>

`
// const variantTableColumns = [
//     { type : 'category' },
//     { type : 'phenotype' },
//     { type : 'mlogp' },
//     { type : 'pValue' , attributes : { show : false } },
//     { type : 'risteysLink' , attributes : { show : false } },
//     { type : 'af' , attributes : { show : false } },
//     { type : 'beta' , attributes : { title : 'beta' } },
//     { type : 'chipAFCase' , attributes : { accessor: 'maf_case' } },
//     { type : 'chipAFControl' , attributes : { accessor: 'maf_control' } },
//     { type : 'numCases' , attributes : { accessor: 'n_case' } },
//     { type : 'numControls', attributes : { accessor: 'n_control' } },
//     { type : 'pip' }
// ]

const variantTableColumns = [
  { type : 'category' },
  { type : 'phenotype' },
  { type : 'betaVariant' , attributes : { title : 'beta' }, sortMethod: "nullToBottomSorter"},
  { type : 'pValue' , attributes : { show : true }, sortMethod: "nullToBottomSorter" },
  { type : 'mlogp', sortMethod: "nullToBottomSorter" },
  { type : 'risteysLink' , attributes : { show : false } },
  { type : 'af' , attributes : { show : false } },
  { type : 'chipAFCase' , attributes : { accessor: 'maf_case' }, sortMethod: "nullToBottomSorter" },
  { type : 'chipAFControl' , attributes : { accessor: 'maf_control' }, sortMethod: "nullToBottomSorter" },
  { type : 'numCases' , attributes : { accessor: 'n_case' } },
  { type : 'numControls', attributes : { accessor: 'n_control' } },
  { title : "pip" , label : "pip" , accessor : "pip" , formatter : "optionalDecimal" }  
]


const maxTableWidth = 1600;
const columnWith = (size) => Math.min(size, size / maxTableWidth * window.innerWidth);

const genePqtlTableColumns = [
  { title : "trait" , label: "trait",accessor : "trait" , formatter : "text",  minWidth: columnWith(120) },
  { title : "source" , label: "source", accessor : "source_displayname" , formatter : "text",  minWidth: columnWith(200) },
  { title : "region" , label : "region" , accessor : "region" , formatter : "text",  minWidth: columnWith(200) },
  { title : "CS" , label : "CS" , accessor : "cs" , formatter : "number",  minWidth: columnWith(80) },
  { title : "variant" , label: "variant",accessor: "v",sortMethod: "variantSorter",minWidth: columnWith(200) },
  { title : "CS prob" , label : "cs specific prob" , accessor : "cs_specific_prob" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { title : "CS bayes factor (log10)" , title : "CS bayes factor (log10)" , accessor : "cs_log10bf" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { title : "CS min r2" , accessor : "cs_min_r2" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { title : "beta" , accessor : "beta" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { title : "p-value" , accessor : "p" , formatter : "pValue",  minWidth: columnWith(100) },
  { title : "CS PIP" , accessor : "prob" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { type : 'codingMostServe' },
  { title : "gene" , label : "gene most severe" ,   accessor : "gene_most_severe" , formatter : "text",  minWidth: columnWith(100) }
]
const coding = { "config" : {
    "title": "FinnGen freeze 12 coding variant results",
    "help" : "FinnGen freeze 12 coding variant results<br/><br/>By default you will see top coding variant association results (all results with a p-value < 1e-5).<br/><br/>Search by gene name to get all results of coding variants in that gene for all analyzed binary phenotypes<br/>(more precisely variants whose most severe consequence from VEP annotation is for that gene).<br/>If you can't find your gene, try with another name.<br/><br/>The result table contains association statistics from additive and recessive analysis<br/>of imputed data (500,348 samples from the FinnGen chip and legacy data)<br/>and from additive analysis of chip genotyped data (416,860 samples from the FinnGen chip).<br/><br/>You can hover over the column names to see their explanations and sort the table by the different p-values and other columns.<br/>Hover over a variant id to see the cluster plot for that variant.<br/>Click on \"only top phenotype per variant\" to see only the top association for each variant.<br/>Click on \"only chip\" to see variants that are on the chip and not in the imputation panel.<br/><br/>Not all variants have results for all three analyses:<br/><br/><div style=\"padding-left: 20px\">Additive analysis results of imputed data are available for all variants in the SiSu4.2<br/>imputation panel with imputation INFO score &gt; 0.6 except for variants with a very low MAC<br/>among the cases and controls of each phenotype.<br/><br/>Recessive analysis results of imputed data are available for all variants with at least two<br/>hard-called minor allele homozygotes and imputation INFO score &gt; 0.6.<br/><br/>Additive analysis results of chip genotyped data are available for all variants that passed QC<br/>except for variants with a very low MAC among the cases and controls of each phenotype.</div>",
      "tip": {
    "variant": "chrom-pos-ref-alt (alt is effect allele) - hover over a variant to see its cluster plot",
    "consequence": "most severe consequence from Variant Effect Predictor",
    "resources": "links to FinnGen browser, gnomAD and Open Targets",
    "INFO": "imputation INFO score<br/>NA if the variant is not in the imputation panel",
    "MAF": "minor allele frequency<br/>from imputed data if the variant is in the imputation panel<br/>from chip data otherwise",
    "FIN enr.": "Finnish enrichment: AF_FIN / AF_NFSEE from gnomAD exomes 2.1.1<br/>(NFSEE=non-Finnish-Swedish-Estonian European)<br/>NA if there are neither FIN nor NFSEE alleles in gnomAD or the variant is not in gnomAD",
    "p-val": "additive model p-value from imputed data",
    "p-val rec": "recessive model p-value from imputed data",
    "p-val chip": "additive model p-value from chip genotype data",
    "beta": "additive model effect size beta from imputed data",
    "beta rec": "recessive model effect size beta from imputed data",
    "beta chip": "additive model effect size beta from chip genotype data",
    "rec-add": "recessive -log10(p) minus additive -log10(p)<br/>positive values mean recessive signal is more significant",
    "leads": "data on possible more significant non-coding lead variants in the region<br/>if the lead variant is more than two orders of magnitude stronger than the coding variant, the column is yellow"
  }
} };
// configuration
const userInterface = {
	/*
    lof : {
	table : { columns : [
	    { type : 'lofPhenotype' },
	    { type : 'lofGene' },	    
	    { type : 'pValue' , attributes : { accessor: 'p_value' } },
	    { type : 'variantList' },
	    { type : 'beta' },
	] }

    },  
  notFound: {
    entity: { message: notFoundEntityMessage },
    page: { message: notFoundPageMessage }
  }, */
  coding: coding,
  about: { banner: aboutBanner },
    variant : { table : { columns : variantTableColumns , defaultSorted : [{
  id: 'mlogp',
  desc: true
}] } }, 
	gene: { 
            geneColocalizations: {},
            tableOfContentsTitles: {
	        "associationResults": "Disease associations within gene region",
	        "geneFunctionalVariants": "Coding variant associations",
	        "lossOfFunction": "Protein truncating variant burden associations",
	        "pqtlColocalizations": "pQTL and colocalizations",
	        "geneDrugs": "Drugs targeting the gene"
            },
	    lossOfFunction: { tableColumns :  [{ type : "phenotype" },
					       { type : "variants" , attributes : { minWidth : 400 } },
					       { type : "pValue" },
					       { type : "or" } ] },
	    lz_config : { ld_panel_version : "sisu42" } ,
	     pqtlColocalizations : {}  },
  phenotype: {
      variant : { table : { columns : [ { type : "chrom" },
                                        { type : "pos" },
					{ type : "ref" },
					{ type : "alt" },
					{ type : "locus" },
					{ type : "rsid" },
					{ type : "nearestGene" },
					{ type : "consequence" },
					{ type : "infoScore" },
					{ type : "finEnrichment" },
                                        { type : "af" },
                                        { type : "afCases" },
                                        { type : "afControls" },
                                        { type : "or" },
					{ type : "pValue" },
                                        { type : "mlogp" }
				      ] },
                    r2_to_lead_threshold: 0.6
		},
    banner: `
    <h2 style="margin-top: 0;">
        {{phenostring}}
        </h2>
        <p>{{category}}</p>
        <p style="margin-bottom: 10px;">
        <a style="
        font-size: 1.25rem;
        padding: .25rem .5rem;
        background-color: #2779bd;
        color: #fff;
        border-radius: .25rem;
        font-weight: 700;
    box-shadow: 0 0 5px rgba(0,0,0,.5);"
           rel="noopener noreferrer"
           href="https://risteys.finngen.fi/phenocode/{{risteys}}"
           target="_blank">RISTEYS
        </a>
        <table class="column_spacing">
            <tbody>
                {{#num_cases}}
                <tr><td><b>{{.}}</b> cases</td></tr>
                {{/num_cases}}

                {{#num_controls}}
                <tr><td><b>{{.}}</b> controls</td></tr>
                {{/num_controls}}
            </tbody>
        </table>
      </p>
    `
  },
  index: {
    table: {
      columns: [
        { type: 'phenotype' },
        { type: 'risteysLink' },
        { type: 'category' },
        { type: 'numCases' },
        {
          title: 'number of cases r10',
          label: 'number of cases r10',
          accessor: 'num_cases_prev',
          formatter: 'textCellFormatter',
          filter: 'number'
        },
        { type: 'numControls' },
        { type: 'numGwSignificant' },
        {
          title: 'genome-wide sig loci r10',
          label: 'genome-wide sig loci r10',
          accessor: 'num_gw_significant_prev',
          formatter: 'textCellFormatter',
          filter: 'number'
        },
        { type: 'controlLambda' }
      ]
    }
  }
}
const metaData = {}
const application = {
  browser : 'FINNGEN' ,
  logo: '<img src="/images/finngen_loop1.gif" style="float: left; width: 60px; height: 60px; margin: -10px; margin-top: 8px">',
  title: 'BETA 12',
  ld_service : "https://api.finngen.fi/api/ld",
  ld_panel_version : "sisu42",  
  vis_conf: {
    info_tooltip_threshold: 0.8,
    loglog_threshold: 10,
    manhattan_colors: [
      'rgb(53,0,212)',
      'rgb(40, 40, 40)'
    ]
  },
  model: {
    tooltip_underscoretemplate: '<% if(_.has(d, \'chrom\')) { %><b><%= d.chrom %>:<%= d.pos.toLocaleString() %> <%= d.ref %> / <%= d.alt %></b><br><% } %>\n<% if(_.has(d, \'rsids\')) { %><% _.each(_.filter((d.rsids||"").split(",")), function(rsid) { %>rsid: <%= rsid %><br><% }) %><% } %>\n<% if(_.has(d, \'nearest_genes\')) { %>nearest gene<%= _.contains(d.nearest_genes, ",")? "s":"" %>: <%= d.nearest_genes %><br><% } %>\n<% if(_.has(d, \'pheno\')) { %>pheno: <%= d[\'pheno\'] %><br><% } %>\n<% if(_.has(d, \'pval\')) { %>p-value: <%= pValueToReadable(d.pval) %><br><% } %>\n<% if(_.has(d, \'mlogp\')) { %>mlog10p-value: <%= d.mlogp %><br><% } %>\n<% if(_.has(d, \'beta\')) { %>beta: <%= d.beta.toFixed(2) %><% if(_.has(d, "sebeta")){ %> (<%= d.sebeta.toFixed(2) %>)<% } %><br><% } %>\n<% if(_.has(d, \'or\')) { %>Odds Ratio: <%= d[\'or\'] %><br><% } %>\n<% if(_.has(d, \'af_alt\')) { %>AF: <%= d.af_alt.toFixed(4) %><br><% } %>\n<% if(_.has(d, \'af_alt_cases\')) { %>AF cases: <%= d.af_alt_cases.toFixed(4) %><br><% } %>\n<% if(_.has(d, \'af_alt_controls\')) { %>AF controls: <%= d.af_alt_controls.toFixed(4) %><br><% } %>\n<% if(_.has(d, \'maf\')) { %>AF: <%= d.maf.toFixed(4) %><br><% } %>\n<% if(_.has(d, \'maf_cases\')) { %>AF cases: <%= d.maf_cases.toFixed(4) %><br><% } %>\n<% if(_.has(d, \'maf_controls\')) { %>AF controls: <%= d.maf_controls.toFixed(4) %><br><% } %>\n<% if(_.has(d, \'af\')) { %>AF: <%= d[\'af\'] %><br><% } %>\n<% if(_.has(d, \'ac\')) { %>AC: <%= d.ac.toFixed(1) %> <br><% } %>\n<% if(_.has(d, \'r2\')) { %>R2: <%= d[\'r2\'] %><br><% } %>\n<% if(_.has(d, \'tstat\')) { %>Tstat: <%= d[\'tstat\'] %><br><% } %>\n<% if(_.has(d, \'n_cohorts\')) { %>n_cohorts: <%= d[\'n_cohorts\'] %><br><% } %>\n<% if(_.has(d, \'n_hom_cases\')) { %>n_hom_cases: <%= d[\'n_hom_cases\'] %><br><% } %>\n<% if(_.has(d, \'n_hom_ref_cases\')) { %>n_hom_ref_cases: <%= d[\'n_hom_ref_cases\'] %><br><% } %>\n<% if(_.has(d, \'n_het_cases\')) { %>n_het_cases: <%= d[\'n_het_cases\'] %><br><% } %>\n<% if(_.has(d, \'n_hom_controls\')) { %>n_hom_controls: <%= d[\'n_hom_controls\'] %><br><% } %>\n<% if(_.has(d, \'n_hom_ref_controls\')) { %>n_hom_ref_controls: <%= d[\'n_hom_ref_controls\'] %><br><% } %>\n<% if(_.has(d, \'n_het_controls\')) { %>n_het_controls: <%= d[\'n_het_controls\'] %><br><% } %>\n<% if(_.has(d, \'n_case\')) { %>#cases: <%= d[\'n_case\'] %><br><% } %>\n<% if(_.has(d, \'n_control\')) { %>#controls: <%= d[\'n_control\'] %><br><% } %>\n<% if(_.has(d, \'num_samples\')) { %>#samples: <%= d[\'num_samples\'] %><br><% } %>\n'
  }
}

const config = { application , metaData , userInterface , }
