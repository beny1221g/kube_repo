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
        ecr_repo = "${ecr_registry}/beny14/aws_repo"
        aws_region = "us-east-2"
        sns_topic_arn = "arn:aws:sns:us-east-2:023196572641:bz_topic"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                    script {
                        try {
                            dir('app') {
                                sh "docker login -u ${USERNAME} -p ${USERPASS}"
                                sh "docker build -t ${IMG_NAME_P} ."
                                sh "docker build -t ${IMG_NAME_N} ."
                            }
                        } catch (Exception e) {
                            echo "Docker build failed: ${e.message}"
                            error "Build failed: ${e.message}"
                        }
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    sh "docker tag ${IMG_NAME} ${DOCKER_REGISTRY_N}:${BUILD_NUMBER}"
                    sh "docker tag ${IMG_NAME} ${DOCKER_REGISTRY_P}:${BUILD_NUMBER}"

                    sh "docker push ${DOCKER_REGISTRY_N}:${BUILD_NUMBER}"
                    sh "docker push ${DOCKER_REGISTRY_P}:${BUILD_NUMBER}"
                }
            }
        }

        stage('Verify Docker Image') {
            steps {
                script {
                    sh "docker images ${IMG_NAME_P}"
                    sh "docker images ${IMG_NAME_N}"
                }
            }
        }

        stage('Push to Amazon ECR') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY',
                    credentialsId: 'aws_cred'
                ]]) {
                    script {
                        sh """
                            aws ecr get-login-password --region ${env.aws_region} | docker login --username AWS --password-stdin ${env.ecr_registry}


                            docker tag ${env.image_tag} ${env.ecr_repo}:${BUILD_NUMBER}


                            docker push ${env.ecr_repo}:${BUILD_NUMBER}
                        """
                    }
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
                credentialsId: 'aws_cred'
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
                credentialsId: 'aws_cred'
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
                    docker ps -q -f ancestor=${DOCKER_REGISTRY}:${BUILD_NUMBER} | xargs -r docker stop
                    docker ps -a -q -f ancestor=${DOCKER_REGISTRY}:${BUILD_NUMBER} | xargs -r docker rm -f
                """

                // Remove images related to this build except the latest
                sh """
                    docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '${DOCKER_REGISTRY}' | grep -v ':latest' | grep -v ':${BUILD_NUMBER}' | awk '{print \$2}' | xargs -r docker rmi -f
                """

                // Clean workspace
                cleanWs()
            }
        }
    }


}


