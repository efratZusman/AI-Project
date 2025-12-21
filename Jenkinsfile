pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Backend Image') {
            steps {
                sh 'docker compose build backend'
            }
        }

        stage('Run Backend Tests (in container)') {
            steps {
                sh '''
                  docker compose run --rm backend \
                  pytest --cov=app --cov-report=xml
                '''
            }
        }

        stage('Build Frontend Extension Image') {
            steps {
                sh 'docker compose build frontend-extension'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'backend/coverage.xml', fingerprint: true
        }
    }
}
