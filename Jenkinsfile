pipeline {
    agent none

    stages {
        stage('Checkout Repo') {
            agent {
                docker {
                    image 'python:3.10-slim'
                    args '-u 0:0 -t -v repo:/repo -v /tmp/pip-cache:/root/.cache/pip'
                }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'Github',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASS'
                )]) {
                    sh '''
                        apt-get update -qq && apt-get install -y git make
                        rm -rf repo
                        mkdir repo
                        cd repo
                        git init
                        git remote add origin https://${GIT_USER}:${GIT_PASS}@github.com/norahosny66/Predictive-Maintenance-MLOps.git
                        git fetch --depth=1 origin main
                        git checkout main
                    '''
                }
            }
        }

        stage('Install & Lint') {
            agent {
                docker {
                    image 'python:3.10-slim'
                    args '-u 0:0 -t -v repo:/repo -v /tmp/pip-cache:/root/.cache/pip'
                }
            }
            steps {
                sh '''
                    cd repo
                    pip install --upgrade pip
                    pip install flake8 black mypy pytest
                    make lint || true
                '''
            }
        }

        

        stage('Trigger Training (Prefect)') {
            agent {
                docker {
                    image 'docker:24.0-cli'
                    args """
                        -u 0:0 \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        --group-add 999 \
                        --entrypoint='' -t
                    """
                }
            }
            steps {
                sh '''
                    apk add --no-cache make bash
                    cd repo
                    make train
                '''
            }
        }
    }

    post {
        always {
            echo 'CI pipeline finished.'
        }
    }
}
