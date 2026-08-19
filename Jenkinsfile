pipeline {
  agent { label 'docker' }

  options {
    timeout(time: 60, unit: 'MINUTES')
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '30'))
    disableConcurrentBuilds()
  }

  environment {
    REGISTRY = 'europe-west1-docker.pkg.dev/phewas-development/fg-phewas-registry'
    IMAGE    = "${REGISTRY}/pheweb"
    TAG      = "ci-${env.GIT_COMMIT}"
  }

  stages {
    stage('Build') {
      steps {
        sh "sed -i 's|COMMIT_SHA|PHEWEB VERSION : ${env.GIT_COMMIT}|' ui/src/common/commonConstants.tsx"
        script {
          docker.build("${IMAGE}:${TAG}", "--pull -f deploy/Dockerfile ./")
        }
      }
    }

    stage('Test') {
      steps {
        sh """
          mkdir -p test-results && chmod 777 test-results
          docker run --rm -v \$PWD/test-results:/out ${IMAGE}:${TAG} sh -c \\
            'pip install --no-cache-dir "pytest==8.*" && cd /pheweb && pytest --ignore=tests/integration -m "not known_failure" --junitxml=/out/pytest.xml tests'
        """
      }
      post {
        always { junit allowEmptyResults: true, testResults: 'test-results/pytest.xml' }
      }
    }

    stage('Push') {
      steps {
        script {
          docker.withRegistry("https://${REGISTRY}") {
            def image = docker.image("${IMAGE}:${TAG}")
            image.push(env.TAG)
            if (env.GIT_BRANCH == 'origin/master') { image.push('ci-latest') }
          }
        }
      }
    }

    stage('Staging') {
      when {
        expression {
          env.GIT_BRANCH == 'origin/master' || env.GIT_BRANCH =~ /.*-test$/
        }
      }
      steps {
        sh '''set -eu
          helm repo add production_jenkins_storage_green gs://production_jenkins_storage_green/helm/charts
          helm repo update
          gcloud container clusters get-credentials development-staging-pheweb --zone europe-west1-b

          if ! helm status development-staging-pheweb >/dev/null 2>&1; then
            echo "release development-staging-pheweb not found - refusing to deploy" >&2
            exit 1
          fi

          helm upgrade development-staging-pheweb production_jenkins_storage_green/finngen-pheweb \\
            --reuse-values --set image.tag=ci-${GIT_COMMIT} --wait --timeout 10m
        '''
      }
    }
  }

  post {
    always {
      sh "docker rmi ${IMAGE}:${TAG} || true"
      cleanWs()
    }
  }
}
