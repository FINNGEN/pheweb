data_dir="/mnt/data-disk/pheweb"

database_conf = ({ "annotation":
                    {"elastic": { "host":"35.187.119.225","port":9200, "variant_index":"finngen_r1_variant_annotation"}  }
                 },
                 { "result": { "tabix": { 'const_arguments': [("phenos","PHEWEB_PHENOS"), ("matrix_path","MATRIX_PATH")] } } }
                )