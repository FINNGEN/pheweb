// text

const aboutBanner = `
     <h1>About this site</h1><br>
     <p>
     The genetic association results on this website are from the
     FinnGen study. These results are from 2,269 binary endpoints
     and 3 quantitative endpoints (HEIGHT_IRN, WEIGHT_IRN, BMI_IRN)
     from freeze 9 (April 2021), consisting of 377,277 individuals.
     </p>
     <p>
     This site was built with PheWeb
     (<a href="https://github.com/statgen/pheweb/">original repository</a>,
      <a href="https://github.com/FINNGEN/pheweb/">Finngen repository</a>).
      All positions are on GRCh38.
     </p>
     <p>
     PheWAS contact:
        Samuli Ripatti (samuli.ripatti@helsinki.fi)<br/>
        FinnGen contact: Aarno Palotie (aarno.palotie@helsinki.fi)
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
const maxTableWidth = 1600;
const columnWith = (size) => Math.min(size, size / maxTableWidth * window.innerWidth);
// configuration
/** @type {ConfigurationUserInterface} */
const userInterface = {
  notFound: {
    entity: { message: notFoundEntityMessage },
    page: { message: notFoundPageMessage }
  },
  about: { banner: aboutBanner },
  phenotype: {
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
           href="https://risteys.finregistry.fi/phenocode/{{risteys}}"
           target="_blank">RISTEYS
        </a>
      </p>
    `,
    r2_to_lead_threshold: 0.6,
  },
  index: {
    table: {
      columns: [
        { type: 'phenotype' },
        { type: 'risteysLink' },
	{ type: 'hasRisteys',
	  accessor: 'hasRisteys',
	  show: false
	},
        { type: 'category' },
        { type: 'numCases' },
        {
          title: 'number of cases r8',
          label: 'number of cases r8',
          accessor: 'num_cases_prev',
          formatter: 'textCellFormatter',
          filter: 'number'
        },
        { type: 'numControls' },
        { type: 'numGwSignificant' },
        {
          title: 'genome-wide sig loci r8',
          label: 'genome-wide sig loci r8',
          accessor: 'num_gw_significant_prev',
          formatter: 'textCellFormatter',
          filter: 'number'
        },
        { type: 'controlLambda' }
      ]
    }
  },
  gene: { lossOfFunction: null , lz_config : { ld_panel_version : "sisu42" },
          pqtlColocalizations: {
	      tableColumns : [
  { title : "trait" , label: "trait",accessor : "trait" , formatter : "text",  minWidth: columnWith(120) },
  { title : "source" , label: "source", accessor : "source_displayname" , formatter : "text",  minWidth: columnWith(200) },
  { title : "region" , label : "region" , accessor : "region" , formatter : "text",  minWidth: columnWith(200) },
  { title : "CS" , label : "CS" , accessor : "cs" , formatter : "number",  minWidth: columnWith(80) },
  { title : "variant" , label: "variant",accessor: "v",sortMethod: "variantSorter",minWidth: columnWith(200) },

  { type : "distance" },
  { type : "cisttrans"},

  { title : "CS prob" , label : "cs specific prob" , accessor : "cs_specific_prob" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { title : "CS bayes factor (log10)" , title : "CS bayes factor (log10)" , accessor : "cs_log10bf" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { title : "CS min r2" , accessor : "cs_min_r2" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { title : "beta" , accessor : "beta" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { title : "p-value" , accessor : "p" , formatter : "pValue",  minWidth: columnWith(100) },
  { title : "CS PIP" , accessor : "prob" , formatter : "optionalDecimal",  minWidth: columnWith(100) },
  { type : 'codingMostServe' },
  { title : "gene" , label : "gene most severe" ,   accessor : "gene_most_severe" , formatter : "text",  minWidth: columnWith(100) }

	      ] },
          geneColocalizations: { subTableColumns : [

                { type : "colocSource" },
                { type : "colocPhenotype2" },
                { type : "colocClpp" },
                { type : "colocClpa" },
                { type : "colocLenInter" },
                { type : "colocLenCS1" },
                { type : "colocLenCS2" },
                { type : "colocLeadingVariantCS1" , attributes : { minWidth : 200 } },

                { type : "distance" , attributes : { accessor: "locus_id1_relative_position" , title : "distance lead cs1 TSS" } },
                { type : "cisttrans" , attributes : { accessor: "locus_id1_distance" , title : "cs1 csi/trans" } },

                { type : "colocLeadingVariantCS1" , attributes : { minWidth : 200 } },

                { type : "distance" , attributes : { accessor: "locus_id2_relative_position" , title : "distance lead cs2 TSS" } },
                { type : "cisttrans" , attributes : { accessor: "locus_id2_distance" , title : "cs2 csi/trans" } },

                { type : "colocBeta1" },
                { type : "colocBeta2" },
                { type : "colocPval1" },
                { type : "colocPval2" }


	  ] },
          tableOfContentsTitles: {
            "associationResults": "Disease associations within gene region",
            "geneFunctionalVariants": "Coding variant associations",
            "lossOfFunction": "Protein truncating variant burden associations",
            "pqtlColocalizations": "pQTL and colocalizations",
            "geneDrugs": "Drugs targeting the gene"
          }
  },
  region: {
    colocalization: {
      tableColumns : [
        {
          title: 'source',
          label: 'source',
          accessor: 'dataset1',
          formatter: 'textCellFormatter'
        },
        {
          title: 'locus id 1',
          label: 'locus id 1',
          accessor: 'hit1',
          formatter: 'textCellFormatter'
        },
        {
          title: 'locus id 2',
          label: 'locus id 2',
          accessor: 'hit2',
          formatter: 'textCellFormatter'
        },
        {
          title: 'Code',
          label: 'Code',
          accessor: 'trait2',
          formatter: 'textCellFormatter'
        },
        {
          title: 'clpp',
          label: 'clpp',
          accessor: 'clpp',
          formatter: 'textCellFormatter'
        },
        {
          title: 'clpa',
          label: 'clpa',
          accessor: 'clpa',
          formatter: 'textCellFormatter'
        },
        {
          title: 'cs1 size',
          label: 'cs1 size',
          accessor: 'cs1_size',
          formatter: 'textCellFormatter'
        },
        {
          title: 'cs2 size',
          label: 'cs2 size',
          accessor: 'cs2_size',
          formatter: 'textCellFormatter'
        },

        {
          title: 'cs1 log10 bf',
          label: 'cs1 log10 bf',
          accessor: 'cs1_log10bf',
          formatter: 'textCellFormatter'
        },
        {
          title: 'cs2 log10 bf',
          label: 'cs2 log10 bf',
          accessor: 'cs1_log10bf',
          formatter: 'textCellFormatter'
        }
      ],
      subtableColumns : [
        {
          title: 'Variant',
          label: 'Variant',
          accessor: 'rsid',
          formatter: 'textCellFormatter'
        },
        {
          title: 'p-value 1',
          label: 'p-value 1',
          accessor: 'p1',
          formatter: 'textCellFormatter'
        },
        {
          title: 'beta 1',
          label: 'beta 1',
          accessor: 'beta1',
          formatter: 'textCellFormatter'
        },
        {
          title: 'se 1',
          label: 'se 1',
          accessor: 'se1',
          formatter: 'textCellFormatter'
        },
        {
          title: 'cs specific prob 1',
          label: 'cs specific prob 1',
          accessor: 'cs_specific_prob1',
          formatter: 'textCellFormatter'
        },

        {
          title: 'p-value 2',
          label: 'p-value 2',
          accessor: 'p2',
          formatter: 'textCellFormatter'
        },
        {
          title: 'beta 2',
          label: 'beta 2',
          accessor: 'beta2',
          formatter: 'textCellFormatter'
        },
        {
          title: 'se 2',
          label: 'se 2',
          accessor: 'se2',
          formatter: 'textCellFormatter'
        },
        {
          title: 'cs specific prob 2',
          label: 'cs specific prob 2',
          accessor: 'cs_specific_prob1',
          formatter: 'textCellFormatter'
        }
      ],
      colocalizationSourceTypes: [
        {type: "Endpoints/Biomarkers", sources: ["FinnGen", "UKBB"]},
        {type: "pQTL", sources: ["Somascan", "Olink", "UKBB-PPP"]},
        {type: "mQTL", sources: ["geneRISK"]},
        {type: "INTERVAL", sources: ["INTERVAL"]},
        {type: "eQTL", sources: ["Alasoo_2018","BLUEPRINT",
                   "Bossini-Castillo_2019",
                   "BrainSeq","Braineac2","CAP",
                   "CEDAR","CommonMind","FUSION",
                   "Fairfax_2012","Fairfax_2014","GENCORD",
                   "GEUVADIS","GTEx","Gilchrist_2021",
                   "HipSci","Kasela_2017","Lepik_2017",
                   "Naranbhai_2015","Nedelec_2016",
                   "Peng_2018","PhLiPS","Quach_2016","ROSMAP",
                   "Schmiedel_2018","Schwartzentruber_2018",
                   "Steinberg_2020","TwinsUK","Young_2019",
                   "iPSCORE","van_de_Bunt_2015", "Sun_2018"]}

      ]
    }
  }

}

/** @type {ConfigurationMetaData} */
const metaData = {}

/** @type {ApplicationConfiguration} */
const application = {
    ld_service : "http://api.finngen.fi/api/ld",
    genome_build : 37,
    browser: "pheweb-dev" ,
    ld_panel_version : "sisu42",
    logo: '<img src="/images/finngen_loop1.gif" style="float: left; width: 60px; height: 60px; margin: -10px; margin-top: 8px">',
    title: 'FREEZE 9 BETA',
    root: 'http://localhost:8081',
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

// @ts-check
/** @type {ConfigurationApplication} */
const config = { application , metaData , userInterface , }
