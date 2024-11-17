pipeline {
    agent { label 'ec2-fleet-bz2' }

    environment {
        image_tag_p = "python_app:${BUILD_NUMBER}"
        image_tag_p_latest = "python_app:latest"
        image_tag_n = "nginx_static:${BUILD_NUMBER}"
        image_tag_n_latest = "nginx_static:latest"
        IMG_NAME_P = "beny14/python_app:${BUILD_NUMBER}"
        IMG_NAME_N = "beny14/nginx_static:${BUILD_NUMBER}"
        DOCKER_REGISTRY_N = "beny14/nginx_static"
        DOCKER_REGISTRY_P = "beny14/python_app"
        ecr_registry = "023196572641.dkr.ecr.us-east-2.amazonaws.com"
        ecr_repo_p = "${ecr_registry}/beny14/python_app"
        ecr_repo_n = "${ecr_registry}/beny14/nginx_static"
        aws_region = "us-east-2"
        sns_topic_arn = "arn:aws:sns:us-east-2:023196572641:bz_topic"
    }

    stages {
        stage('Build Docker Images') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                    script {
                        try {
                            dir('app') {
                                sh "docker login -u ${USERNAME} -p ${USERPASS}"
                                // Build Python app image
                                sh "docker build -t ${IMG_NAME_P} -t ${DOCKER_REGISTRY_P}:latest ."
                                // Build NGINX image
                                sh "docker build -t ${IMG_NAME_N} -t ${DOCKER_REGISTRY_N}:latest ."
                            }
                        } catch (Exception e) {
                            echo "Docker build failed: ${e.message}"
                            error "Build failed: ${e.message}"
                        }
                    }
                }
            }
        }

        stage('Push Docker Images to DockerHub') {
            steps {
                script {
                    // Push Python app image
                    sh """
                        docker push ${IMG_NAME_P}
                        docker push ${DOCKER_REGISTRY_P}:latest
                    """
                    // Push NGINX image
                    sh """
                        docker push ${IMG_NAME_N}
                        docker push ${DOCKER_REGISTRY_N}:latest
                    """
                }
            }
        }

        stage('Push Docker Images to Amazon ECR') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                    credentialsId: 'aws'
                ]]) {
                    script {
                        sh """
                            aws ecr get-login-password --region ${env.aws_region} | docker login --username AWS --password-stdin ${env.ecr_registry}
                            # Tag and push Python app image
                            docker tag ${IMG_NAME_P} ${ecr_repo_p}:${BUILD_NUMBER}
                            docker tag ${DOCKER_REGISTRY_P}:latest ${ecr_repo_p}:latest
                            docker push ${ecr_repo_p}:${BUILD_NUMBER}
                            docker push ${ecr_repo_p}:latest
                            # Tag and push NGINX image
                            docker tag ${IMG_NAME_N} ${ecr_repo_n}:${BUILD_NUMBER}
                            docker tag ${DOCKER_REGISTRY_N}:latest ${ecr_repo_n}:latest
                            docker push ${ecr_repo_n}:${BUILD_NUMBER}
                            docker push ${ecr_repo_n}:latest
                        """
                    }
                }
            }
        }

        stage('Verify Docker Images') {
            steps {
                script {
                    // Verify Python app image
                    sh "docker images ${IMG_NAME_P}"
                    sh "docker images ${DOCKER_REGISTRY_P}:latest"
                    // Verify NGINX image
                    sh "docker images ${IMG_NAME_N}"
                    sh "docker images ${DOCKER_REGISTRY_N}:latest"
                }
            }
        }
    }

    post {
        success {
            withCredentials([[
                $class: 'AmazonWebServicesCredentialsBinding',
                accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                credentialsId: 'aws'
            ]]) {
                sh """
                    aws sns publish --region ${env.aws_region} --topic-arn ${env.sns_topic_arn} \\
                        --message "Pipeline succeeded for build #${env.BUILD_NUMBER} on ${env.JOB_NAME}" \\
                        --subject "Jenkins Pipeline Success Notification"
                """
            }
        }
        failure {
            withCredentials([[
                $class: 'AmazonWebServicesCredentialsBinding',
                accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                credentialsId: 'aws'
            ]]) {
                sh """
                    aws sns publish --region ${env.aws_region} --topic-arn ${env.sns_topic_arn} \\
                        --message "Pipeline failed for build #${env.BUILD_NUMBER} on ${env.JOB_NAME}" \\
                        --subject "Jenkins Pipeline Failure Notification"
                """
            }
        }
        always {
            script {
                sh """
                    # Stop and remove containers related to the current build
                    docker ps -q -f ancestor=${DOCKER_REGISTRY_N}:${BUILD_NUMBER} | xargs -r docker stop
                    docker ps -a -q -f ancestor=${DOCKER_REGISTRY_N}:${BUILD_NUMBER} | xargs -r docker rm -f

                    docker ps -q -f ancestor=${DOCKER_REGISTRY_P}:${BUILD_NUMBER} | xargs -r docker stop
                    docker ps -a -q -f ancestor=${DOCKER_REGISTRY_P}:${BUILD_NUMBER} | xargs -r docker rm -f

                    # Remove unused images except latest and current BUILD_NUMBER
                    docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '${DOCKER_REGISTRY_N}' | grep -v ':latest' | grep -v ':${BUILD_NUMBER}' | awk '{print \$2}' | xargs -r docker rmi -f
                    docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '${DOCKER_REGISTRY_P}' | grep -v ':latest' | grep -v ':${BUILD_NUMBER}' | awk '{print \$2}' | xargs -r docker rmi -f
                """
                cleanWs()
            }
        }
    }
}
