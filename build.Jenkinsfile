pipeline {
    options {
        buildDiscarder(logRotator(daysToKeepStr: '14'))
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 50, unit: 'MINUTES')
    }

    environment {
        IMG_NAME = "kube:${BUILD_NUMBER}"
        DOCKER_REPO = "beny14/kube_repo"
    }

    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    docker.image('beny14/dockerfile_agent:latest').inside('--user root -v /var/run/docker.sock:/var/run/docker.sock') {
                        withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                            try {
                                echo "Starting Docker build"
                                sh """
                                    echo ${USERPASS} | docker login -u ${USERNAME} --password-stdin
                                    docker build -t ${DOCKER_REPO}:${BUILD_NUMBER} .
                                    docker tag ${DOCKER_REPO}:${BUILD_NUMBER} ${DOCKER_REPO}:latest
                                    docker push ${DOCKER_REPO}:${BUILD_NUMBER}
                                    docker push ${DOCKER_REPO}:latest
                                """
                                echo "Docker build and push completed"
                            } catch (Exception e) {
                                error "Build failed: ${e.getMessage()}"
                            }
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
                def containerId = sh(script: "docker ps -q -f ancestor=${DOCKER_REPO}:${BUILD_NUMBER}", returnStdout: true).trim()

                sh """
                    for id in \$(docker ps -a -q -f ancestor=${DOCKER_REPO}:${BUILD_NUMBER}); do
                        if [ "\$id" != "${containerId}" ]; then
                            docker rm -f \$id || true
                        fi
                    done
                """
                sh """
                    docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '${DOCKER_REPO}' | grep -v ':latest' | grep -v ':${BUILD_NUMBER}' | awk '{print \$2}' | xargs --no-run-if-empty docker rmi -f || true
                """
                cleanWs()
                echo "Cleanup completed"
            }
        }

        failure {
            script {
                def errorMessage = currentBuild.result == 'FAILURE' ? currentBuild.description : 'Build failed'
                echo "Error occurred: ${errorMessage}"
            }
        }
    }
}
