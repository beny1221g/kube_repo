pipeline {
    options {
        buildDiscarder(logRotator(daysToKeepStr: '14'))
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 40, unit: 'MINUTES')
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
                    // Ensure Docker socket is mounted properly
                    docker.image('beny14/dockerfile_agent:latest').inside('--user root -v /var/run/docker.sock:/var/run/docker.sock:rw') {
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
                def containerIds = sh(script: "docker ps -q -f ancestor=${DOCKER_REPO}:${BUILD_NUMBER}", returnStdout: true).trim()
                if (containerIds) {
                    sh "docker rm -f ${containerIds} || true"
                }
                def imageIds = sh(script: "docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '${DOCKER_REPO}' | grep -v ':latest' | grep -v ':${BUILD_NUMBER}' | awk '{print \$2}'", returnStdout: true).trim()
                if (imageIds) {
                    sh "docker rmi -f ${imageIds} || true"
                }
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
