
pipeline {
    agent any

    environment {
        PATH = "/usr/local/bin:/opt/homebrew/bin:/opt/anaconda3/bin:/Users/opium_17/.docker/bin:/Applications/Docker.app/Contents/Resources/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv-ci
                    .venv-ci/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Automated Tests') {
            steps {
                sh '.venv-ci/bin/python -m pytest -v'
            }
        }

        stage('Build and Deploy Docker') {
            steps {
                sh 'docker compose up -d --build'
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    curl --fail --retry 10 --retry-delay 2 --retry-connrefused http://localhost:5001/health
                '''
            }
        }
    }

    post {
        success {
            echo 'Attendify CI/CD Pipeline SUCCESS!'
        }

        failure {
            echo 'Attendify CI/CD Pipeline FAILED!'
        }
    }
}
