pipeline {
  agent any
  stages {
    stage('Build') {
	    steps {
		script {    sh(script:"""printenv""")
		            sh(script:"""sed -i "s/COMMIT_SHA/PHEWEB VERSION : \$(git log -n 1 --format=format:"%H")/" ui/src/common/commonConstants.tsx""")
		            c = docker.build("europe-west1-docker.pkg.dev/phewas-development/fg-phewas-registry/pheweb:ci-${env.GIT_COMMIT}", "-f deploy/Dockerfile ./")
		  	    docker.withRegistry('https://europe-west1-docker.pkg.dev/phewas-development/fg-phewas-registry') { c.push("ci-${env.GIT_COMMIT}") }
			    docker.withRegistry('https://europe-west1-docker.pkg.dev/phewas-development/fg-phewas-registry') { c.push("ci-latest") }
		}

	    }
	}

    stage('Test') {
	    steps {
		script {
		            // Unit tests run against the image that was just built (the
		            // source is baked in at /pheweb); integration tests need
		            // selenium/testcontainers and a running stack, so skip them.
		            sh(script:"""docker run --rm ${c.id} sh -c 'pip install --no-cache-dir pytest && cd /pheweb && pytest --ignore=tests/integration tests'""")
		}
	    }
	}

    stage('Staging') {
            when { expression { env.GIT_BRANCH == 'origin/master'  || env.GIT_BRANCH =~ /.*-test$/ || env.GIT_BRANCH == 'origin/656-gene-page-random-locuszoom' } }
	    steps {
                // No key file: the agent VM's own service account provides the
                // credentials for gcloud, helm-gcs and the GKE cluster.
		    sh '''helm plugin list | grep gcs || helm plugin install https://github.com/hayorov/helm-gcs.git --version 0.4.0'''
		    sh '''helm repo add production_jenkins_storage_green gs://production_jenkins_storage_green/helm/charts'''
		    sh '''helm repo update'''
		    sh '''helm fetch production_jenkins_storage_green/finngen-pheweb'''
                    sh '''/usr/bin/gcloud container clusters get-credentials development-staging-pheweb --zone europe-west1-b'''
                    sh '''if helm ls | grep development-staging > /dev/null  ; then
		          helm get values development-staging-pheweb | grep -v USER-SUPPLIED > ./staging-values.yaml ;
			  helm upgrade development-staging-pheweb production_jenkins_storage_green/finngen-pheweb -f ./staging-values.yaml  --set image.tag=ci-${GIT_COMMIT} ;
			  kubectl delete pods --all --wait=false
			  fi'''

	    }
	}

    }
}
