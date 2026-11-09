// Builds a release image only when pheweb/version.py on master has a version
// that is not in the registry yet, i.e. after `pheweb version patch|minor|major`.
// Other commits finish early as NOT_BUILT.
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
  }

  stages {
    stage('Version') {
      steps {
        script {
          env.VERSION = sh(returnStdout: true,
                           script: "sed -nE \"s/^version = '(.*)'\$/\\1/p\" pheweb/version.py").trim()
          if (!(env.VERSION ==~ /\d+\.\d+\.\d+/)) {
            error "could not read a semantic version from pheweb/version.py: '${env.VERSION}'"
          }
          // fails the build if the registry can not be read, so a version is never rebuilt by accident
          sh "gcloud artifacts docker tags list ${IMAGE} --format='value(tag.basename())' > registry-tags.txt"
          def built = sh(returnStatus: true, script: "grep -qxF '${env.VERSION}' registry-tags.txt") == 0
          if (env.GIT_BRANCH != 'origin/master') {
            env.RELEASE = 'false'
            currentBuild.description = "not master"
          } else if (built) {
            env.RELEASE = 'false'
            currentBuild.description = "v${env.VERSION} already built"
          } else {
            env.RELEASE = 'true'
            currentBuild.description = "v${env.VERSION}"
          }
          if (env.RELEASE == 'false') {
            // this should make Jenkins show this build as grey (NOT_BUILT)
            currentBuild.result = 'NOT_BUILT'
          }
        }
      }
    }

    stage('Build') {
      when { environment name: 'RELEASE', value: 'true' }
      steps {
        sh "sed -i 's|COMMIT_SHA|PHEWEB VERSION : ${VERSION}|' ui/src/common/commonConstants.tsx"
        script {
          docker.build("${IMAGE}:${VERSION}", "--pull -f deploy/Dockerfile ./")
        }
      }
    }

    stage('Test') {
      when { environment name: 'RELEASE', value: 'true' }
      steps {
        sh """
          mkdir -p test-results && chmod 777 test-results
          docker run --rm -v \$PWD/test-results:/out ${IMAGE}:${VERSION} sh -c \\
            'pip install --no-cache-dir "pytest==8.*" && cd /pheweb && pytest --ignore=tests/integration -m "not known_failure" --junitxml=/out/pytest.xml tests'
        """
      }
      post {
        always { junit allowEmptyResults: true, testResults: 'test-results/pytest.xml' }
      }
    }

    stage('Push') {
      when { environment name: 'RELEASE', value: 'true' }
      steps {
        script {
          docker.withRegistry("https://${REGISTRY}") {
            def image = docker.image("${IMAGE}:${VERSION}")
            image.push(env.VERSION)
            image.push('latest')
          }
        }
      }
    }

    stage('Staging') {
      when { environment name: 'RELEASE', value: 'true' }
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
            --reuse-values --set image.tag=${VERSION} --wait --timeout 10m
        '''
      }
    }
  }

  post {
    always {
      script {
        if (env.RELEASE == 'true') {
          sh "docker rmi ${IMAGE}:${VERSION} || true"
        }
      }
      cleanWs()
    }
  }
}
