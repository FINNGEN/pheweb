task manhattan {
    String docker
    File pheno_file
    File annotation_filepath
    File annotation_tbi_filepath

    String pheno_name = sub(basename(pheno_file), ".gz$", "")
    String manhattan_file = "pheweb/generated-by-pheweb/manhattan/${pheno_name}.json.gz"

    command <<<
        set -euxo pipefail

        mkdir -p pheweb/generated-by-pheweb/parsed
        mkdir -p pheweb/generated-by-pheweb/pheno
        mkdir -p /root/.pheweb/cache

        cat ${pheno_file} | \
        (if [[ "${pheno_file}" == *.gz || "${pheno_file}" == *.bgz ]]; then zcat ; else cat ; fi) | \
        sed '1 s/^#chrom/chrom/ ; ' > pheweb/generated-by-pheweb/parsed/${pheno_name}

        cp pheweb/generated-by-pheweb/parsed/${pheno_name} pheweb/generated-by-pheweb/pheno/${pheno_name}

        cd pheweb

        pheweb phenolist glob generated-by-pheweb/parsed/* --simple-phenocode && \
        pheweb manhattan --annotation_filepath=${annotation_filepath} && \
        gzip generated-by-pheweb/manhattan/${pheno_name}.json
    >>>

    output {
        File out = manhattan_file
    }

    runtime {
        docker: "${docker}"
        cpu: 2
        memory: "4 GB"
        bootDiskSizeGb: 30
        disks: "local-disk 70 HDD"
        zones: "europe-west1-b"
        preemptible: 2
    }
}

workflow generate_manhattan {

    File pheno_file_loc
    File annotation_filepath
    File annotation_tbi_filepath

    Array[String] pheno_files = read_lines(pheno_file_loc)

    scatter (pheno_file in pheno_files) {
        call manhattan {
            input:
                pheno_file = pheno_file,
                annotation_filepath = annotation_filepath,
                annotation_tbi_filepath = annotation_tbi_filepath,
        }
    }

    output {
        Array[File] manhattan = manhattan.out
    }
}
