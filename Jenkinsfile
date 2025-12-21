pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Tests + Coverage') {
            steps {
                dir('backend') {
                    sh 'pip install -r requirements.txt'
                    sh 'pytest --cov=app --cov-report=term-missing --cov-report=xml'
                }
            }
        }

        stage('Build Backend Docker') {
            steps {
                sh 'docker compose build backend'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'backend/coverage.xml', fingerprint: true
        }
    }
}
