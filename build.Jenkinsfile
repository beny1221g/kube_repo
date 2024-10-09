pipeline {
    options {
        buildDiscarder(logRotator(daysToKeepStr: '14'))
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 40, unit: 'MINUTES')
    }

    environment {
        PYTHON_REPO = "beny14/python_app"
        NGINX_REPO = "beny14/nginx_static"
    }

    agent {
           lable 'ec2-fleet-bz'
//         docker {
//             image 'beny14/dockerfile_agent:latest'
//             args '--user root -v /var/run/docker.sock:/var/run/docker.sock'
//         }
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/beny1221g/kube_repo.git', branch: 'main'
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                    script {
                        sh """
                            echo ${USERPASS} | docker login -u ${USERNAME} --password-stdin
                        """
                    }
                }
            }
        }

        stage('Build Python App') {
            steps {
                script {
                    try {
                        echo "Starting Docker build for Python app"
                        sh """
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

        stage('Build Nginx Static Site') {
            steps {
                script {
                    try {
                        echo "Starting Docker build for Nginx static site"
                        sh """
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

        // Uncomment if needed
        // stage('Archive Artifacts') {
        //     steps {
        //         archiveArtifacts artifacts: 'k8s/*.yaml', allowEmptyArchive: true
        //     }
        // }
    }

    post {
        always {
            script {
                echo "Cleaning up Docker containers and images"
                sh "docker system prune -f --volumes || true"
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
