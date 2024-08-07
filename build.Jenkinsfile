pipeline {
    options {
        buildDiscarder(logRotator(daysToKeepStr: '14'))
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 40, unit: 'MINUTES') // Set a global timeout for the pipeline
    }

    environment {
        PYTHON_REPO = "beny14/python_app"
        NGINX_REPO = "beny14/nginx_static"
    }

    agent {
        docker {
            image 'beny14/dockerfile_agent:latest'
            args '--user root -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/beny1221g/kube_repo.git', branch: 'main'
            }
        }

        stage('Build Python App') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                    script {
                        try {
                            echo "Starting Docker build for Python app"
                            sh """
                                echo ${USERPASS} | docker login -u ${USERNAME} --password-stdin
                                docker build -t ${PYTHON_REPO}:${BUILD_NUMBER} -f app/Dockerfile app
                                docker tag ${PYTHON_REPO}:${BUILD_NUMBER} ${PYTHON_REPO}:latest
                                docker push ${PYTHON_REPO}:${BUILD_NUMBER}
                                docker push ${PYTHON_REPO}:latest
                            """
                            echo "Docker build and push for Python app completed"
                        } catch (Exception e) {
                            error "Build failed: ${e.getMessage()}"
                        }
                    }
                }
            }
        }

        stage('Build Nginx Static Site') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                    script {
                        try {
                            echo "Starting Docker build for Nginx static site"
                            sh """
                                echo ${USERPASS} | docker login -u ${USERNAME} --password-stdin
                                docker build -t ${NGINX_REPO}:${BUILD_NUMBER} -f NGINX/Dockerfile NGINX
                                docker tag ${NGINX_REPO}:${BUILD_NUMBER} ${NGINX_REPO}:latest
                                docker push ${NGINX_REPO}:${BUILD_NUMBER}
                                docker push ${NGINX_REPO}:latest
                            """
                            echo "Docker build and push for Nginx static site completed"
                        } catch (Exception e) {
                            error "Build failed: ${e.getMessage()}"
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                echo "Cleaning up Docker containers and images"
                def pythonContainerId = sh(script: "docker ps -q -f ancestor=${env.PYTHON_REPO}:${BUILD_NUMBER}", returnStdout: true).trim()
                def nginxContainerId = sh(script: "docker ps -q -f ancestor=${env.NGINX_REPO}:${BUILD_NUMBER}", returnStdout: true).trim()

                sh """
                    for id in \$(docker ps -a -q -f ancestor=${env.PYTHON_REPO}:${BUILD_NUMBER}); do
                        if [ "\$id" != "${pythonContainerId}" ]; then
                            docker rm -f \$id || true
                        fi
                    done
                    for id in \$(docker ps -a -q -f ancestor=${env.NGINX_REPO}:${BUILD_NUMBER}); do
                        if [ "\$id" != "${nginxContainerId}" ]; then
                            docker rm -f \$id || true
                        fi
                    done
                """
                sh """
                    docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '${env.PYTHON_REPO}' | grep -v ':latest' | grep -v ':${BUILD_NUMBER}' | awk '{print \$2}' | xargs --no-run-if-empty docker rmi -f || true
                    docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '${env.NGINX_REPO}' | grep -v ':latest' | grep -v ':${BUILD_NUMBER}' | awk '{print \$2}' | xargs --no-run-if-empty docker rmi -f || true
                """
                cleanWs()
                echo "Cleanup completed"
            }
        }

        failure {
            script {
                def errorMessage = currentBuild.result == 'FAILURE' ? currentBuild.description : 'Build failed '
                echo "Error occurred: ${errorMessage}"
            }
        }
    }
}