authentication=True
cors_origins="*"
authentication_file = "/etc/gcp/oauth.conf"
noindex=True

data_dir="/mnt/nfs/pheweb/r11/release/"
resource_dir="/mnt/nfs/pheweb/r11/release/resources"
cache="/mnt/nfs/pheweb/r11/release/cache/"

logging_level="WARNING"

database_conf = (
    { "annotation": { "TabixAnnotationDao": { "matrix_path": "/mnt/nfs/pheweb/r11/dev/annotation/variants/R11_annotated_variants_v2.gz" ,
                                              "gene_column" : "gene_most_severe" } } },
    { "result": { 
        "TabixResultFiltDao": { 'const_arguments': [ ("phenos","PHEWEB_PHENOS"), ("matrix_path","MATRIX_PATH") ], 
        "columns" : {"pheno": "#pheno", "mlogp": "mlogp", "beta": "beta", "sebeta": "sebeta", "maf": "af_alt", "maf_cases": "af_alt_cases", "maf_controls": "af_alt_controls"}  } 
    } },
    { "gnomad": { "TabixGnomadDao": { "matrix_path": "/mnt/nfs/pheweb/r11/release/annotation/gnomad21/gnomad.genomes.r2.1.sites.liftover.b38.finngen.r2pos.af.ac.an.tsv.gz" } } },
    { "finemapping" : { "FineMappingMySQLDao": { "authentication_file": "/etc/gcp/mysql.conf",
                                                 "base_paths": { "susie": "/mnt/nfs/pheweb/r11/release/finemap/snp",
                                                                 "conditional": "/mnt/nfs/pheweb/r11/release/finemap/conditional",
                                                                 "finemap": "/mnt/nfs/pheweb/r11/release/finemap/cred" } } } } ,
    { "lof": { "LofMySQLDao": { "authentication_file": "/etc/gcp/mysql.conf" } } },
    { "colocalization": { "ColocalizationDAO": { "db_url": "/etc/gcp/mysql.conf" ,
                                                 "echo" : False  } } },
    { "autoreporting": {"AutoreportingDao": { "authentication_file": "/etc/gcp/mysql.conf",
                                              "group_report_path": "/mnt/nfs/pheweb/r11/release/autoreport/group_reports"} } } ,
    { "variant_phenotype" :
          { "VariantPhenotypeDao" :
            { "authentication_file": "/etc/gcp/mysql.conf" ,
              "fields" : [ { "table" : "variant_phenotype_pip" ,
                             "columns" : [ "pip" ] },
    #                       #{ "table" : "dev_analysis_r10.sex_diff" ,
    #                       #  "columns" : [ "diff_beta", "p_diff" ] }
              ]
            }
          }
    } ,
    { "autocompleter" : { "AutocompleterMYSQLDAO" : { "const_arguments" : [ ("phenos" , "PHEWEB_USE_PHENOS") ],
                                                      "authentication_file" : "/etc/gcp/mysql.conf" } } },
    { "coding":
      {"FileCodingDAO":
       { "phenos" : "/mnt/nfs/pheweb/r11/release/chip/analyzed_phenos.json" ,
         "variant_annotation" : "/mnt/nfs/pheweb/r11/release/chip/R11_annotated_coding_variants_chip_imputed_merged.gz" ,
         "gwas_tiledb" : "/mnt/nfs/pheweb/r11/release/chip/r11_coding_tiledb" ,
         "top_table" : "/mnt/nfs/pheweb/r11/release/chip/R11_coding_variant_results_1e-5_signals.tsv" ,
         "plot_root" : "gs://finngen-production-library-green/finngen_R11/cluster_plots/raw/" ,
       }
      }
    },
    { "pqtl_colocalization": 
      { "PqtlColocalisationDao": 
        { "authentication_file": "/etc/gcp/mysql.conf",
          "pqtl": {
            "table": "pqtl_finemap",
            "columns": [ "trait","region","cs","v","cs_specific_prob",
                         "cs_log10bf", "cs_min_r2", "beta", "p", "prob", 
                         "most_severe", "gene_name", "gene_most_severe", 
                         "source", "source_displayname"] 
          },
          "colocalization": {
              "table": "colocalization",
              "columns": ["source2", "phenotype1", "phenotype1_description",
                          "clpp", "clpa", "len_inter", "len_cs1", 
                          "len_cs2", "source2_displayname", "beta1", "beta2", "pval1", "pval2"]
          } 
      } } 
    }
    )

n_query_threads=4
report_conf = {"func_var_assoc_threshold":0.0001,
               "gene_top_assoc_threshold":0.0001}
