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
                sh 'docker build -t ai-guard-backend ./backend'
            }
        }

        stage('Run Backend Tests (in container)') {
            steps {
                sh '''
                  docker run --rm \
                  ai-guard-backend \
                  pytest --cov=app --cov-report=xml
                '''
            }
        }

        stage('Build Frontend Extension Image') {
            steps {
                sh 'docker build -t ai-guard-extension ./extension'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'backend/coverage.xml', fingerprint: true
        }
    }
}
