all:list

list:
	echo "finngen-refinery-dev"
	gcloud deployment-manager deployments list --project finngen-refinery-dev
	echo "phewas-development"
	gcloud deployment-manager deployments list --project phewas-development

create-red-development-pipeline-pheweb:
	gcloud deployment-manager deployments create red-development-pipeline-pheweb   --config red-development-pipeline-pheweb-values.yaml   --project finngen-refinery-dev -q --automatic-rollback-on-error

delete-red-development-pipeline-pheweb:
	gsutil -m rm -r gs://red-development-userresults-cromwell-storage ;\
	gcloud deployment-manager deployments delete red-development-pipeline-pheweb --project finngen-refinery-dev -q

create-green-development-pipeline-pheweb:
	gcloud deployment-manager deployments create green-development-pipeline-pheweb --config green-development-pipeline-pheweb-values.yaml --project phewas-development -q --automatic-rollback-on-error


delete-green-development-pipeline-pheweb:
	gsutil -m rm -r gs://green-development-userresults-cromwell-storage ;\
	gcloud deployment-manager deployments delete green-development-pipeline-pheweb --project phewas-development -q
