pipeline {
    agent { label 'ec2-fleet-bz2' }

    environment {
        image_tag_p = "python_app:${BUILD_NUMBER}"
        image_tag_n = "nginx_static:${BUILD_NUMBER}"
        IMG_NAME_P = "beny14/python_app:${BUILD_NUMBER}"
        IMG_NAME_N = "beny14/nginx_static:${BUILD_NUMBER}"
        DOCKER_REGISTRY_N = "beny14/nginx_static"
        DOCKER_REGISTRY_P = "beny14/python_app"
        ecr_registry = "023196572641.dkr.ecr.us-east-2.amazonaws.com"
        ecr_repo_n = "${ecr_registry}/beny14/nginx_static"
        ecr_repo_p = "${ecr_registry}/beny14/python_app"
        aws_region = "us-east-2"
        sns_topic_arn = "arn:aws:sns:us-east-2:023196572641:bz_topic"
    }

    stages {
        stage('Build Docker Images') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                    script {
                        dir('app') {
                            echo "Building Docker images for NGINX and Python App..."
                            sh """
                                docker login -u ${USERNAME} -p ${USERPASS}
                                docker build -t ${IMG_NAME_P} .
                                docker build -t ${IMG_NAME_N} .
                            """
                        }
                    }
                }
            }
        }

        stage('Push NGINX Image to DockerHub') {
            steps {
                script {
                    echo "Pushing NGINX image to DockerHub..."
                    sh """
                        docker tag ${IMG_NAME_N} ${DOCKER_REGISTRY_N}:${BUILD_NUMBER}
                        docker push ${DOCKER_REGISTRY_N}:${BUILD_NUMBER}
                    """
                }
            }
        }

        stage('Push Python App Image to DockerHub') {
            steps {
                script {
                    echo "Pushing Python App image to DockerHub..."
                    sh """
                        docker tag ${IMG_NAME_P} ${DOCKER_REGISTRY_P}:${BUILD_NUMBER}
                        docker push ${DOCKER_REGISTRY_P}:${BUILD_NUMBER}
                    """
                }
            }
        }

        stage('Push Images to Amazon ECR') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                    credentialsId: 'aws'
                ]]) {
                    script {
                        echo "Pushing images to Amazon ECR..."
                        sh """
                            aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_registry}
                            docker tag ${IMG_NAME_N} ${ecr_repo_n}:${BUILD_NUMBER}
                            docker tag ${IMG_NAME_P} ${ecr_repo_p}:${BUILD_NUMBER}
                            docker push ${ecr_repo_n}:${BUILD_NUMBER}
                            docker push ${ecr_repo_p}:${BUILD_NUMBER}
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded, sending success notification..."
            withCredentials([[
                $class: 'AmazonWebServicesCredentialsBinding',
                accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                credentialsId: 'aws'
            ]]) {
                sh """
                    aws sns publish --region ${aws_region} --topic-arn ${sns_topic_arn} \
                        --message "Pipeline succeeded for build #${BUILD_NUMBER} on ${JOB_NAME}" \
                        --subject "Jenkins Pipeline Success Notification"
                """
            }
        }
        failure {
            echo "Pipeline failed, sending failure notification..."
            withCredentials([[
                $class: 'AmazonWebServicesCredentialsBinding',
                accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                credentialsId: 'aws'
            ]]) {
                sh """
                    aws sns publish --region ${aws_region} --topic-arn ${sns_topic_arn} \
                        --message "Pipeline failed for build #${BUILD_NUMBER} on ${JOB_NAME}" \
                        --subject "Jenkins Pipeline Failure Notification"
                """
            }
        }
        always {
            script {
                echo "Performing cleanup tasks..."
                sh """
                    # Stop and remove containers for NGINX
                    docker ps -q -f ancestor=${DOCKER_REGISTRY_N}:${BUILD_NUMBER} | xargs -r docker stop
                    docker ps -a -q -f ancestor=${DOCKER_REGISTRY_N}:${BUILD_NUMBER} | xargs -r docker rm -f

                    # Stop and remove containers for Python App
                    docker ps -q -f ancestor=${DOCKER_REGISTRY_P}:${BUILD_NUMBER} | xargs -r docker stop
                    docker ps -a -q -f ancestor=${DOCKER_REGISTRY_P}:${BUILD_NUMBER} | xargs -r docker rm -f

                    # Remove old images for both applications
                    docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '${DOCKER_REGISTRY_N}' | grep -v ':latest' | grep -v ':${BUILD_NUMBER}' | awk '{print \$2}' | xargs -r docker rmi -f
                    docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '${DOCKER_REGISTRY_P}' | grep -v ':latest' | grep -v ':${BUILD_NUMBER}' | awk '{print \$2}' | xargs -r docker rmi -f
                """
                cleanWs()
            }
        }
    }
}
