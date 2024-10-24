pipeline {
    options {
        buildDiscarder(logRotator(daysToKeepStr: '14'))
        disableConcurrentBuilds()
        timeout(time: 40, unit: 'MINUTES')
    }

    environment {
        PYTHON_REPO = "beny14/python_app"
        NGINX_REPO = "beny14/nginx_static"
    }

    agent {
        label 'jenkins-agent'  // Adjust this label as needed for EKS
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    // Ensure the checkout happens in the node context
                    checkout scm
                }
            }
        }

        stage('Docker Login') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                        sh """
                            echo ${USERPASS} | docker login -u ${USERNAME} --password-stdin
                        """
                    }
                }
            }
        }

        stage('Build and Push Applications') {
            parallel {
                stage('Build and Push Python App') {
                    steps {
                        script {
                            buildAndPushApp(PYTHON_REPO, 'app/Dockerfile', 'app')
                        }
                    }
                }

                stage('Build and Push Nginx App') {
                    steps {
                        script {
                            buildAndPushApp(NGINX_REPO, 'NGINX/Dockerfile', 'NGINX')
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
        }
    }
}

// Centralized Function to build and push Docker images
def buildAndPushApp(String repo, String dockerfile, String contextDir) {
    // Wrap the Docker commands in a script block to ensure proper context
    script {
        try {
            def isEC2 = sh(script: 'curl -s http://169.254.169.254/latest/meta-data/instance-id || true', returnStdout: true).trim()
            if (!isEC2) {
                echo "Running on EC2"
            } else {
                echo "Running on EKS or unknown environment"
                kubernetes {
                   label 'jenkins-agent'
                    // Other configurations...
                    }
                podTemplate(yaml: '''
                            apiVersion: v1
                            kind: Pod
                            labels:
                              jenkins-agent: true
                            spec:
                              serviceAccountName: jenkins
                              containers:
                              - name: jnlp
                                image: jenkins/inbound-agent
                                args: ['--user', 'root', '-v', '/var/run/docker.sock:/var/run/docker.sock']
                              - name: build
                                image: beny14/dockerfile_agent:latest
                                tty: true
                                volumeMounts:
                                - name: docker-sock
                                  mountPath: /var/run/docker.sock
                              volumes:
                              - name: docker-sock
                                hostPath:
                                  path: /var/run/docker.sock
                        ''')
            }

            echo "Starting Docker build for ${repo}"
            sh """
                docker build -t ${repo}:${BUILD_NUMBER} -f ${dockerfile} ${contextDir}
                docker tag ${repo}:${BUILD_NUMBER} ${repo}:latest
                docker push ${repo}:${BUILD_NUMBER}
                docker push ${repo}:latest
            """
            echo "Docker build and push completed for ${repo}"
        } catch (Exception e) {
            error "Build failed: ${e.getMessage()}"
        }
    }
}

// pipeline {
//     agent { label 'ec2-fleet-bz2' }
//
//     options {
//         buildDiscarder(logRotator(daysToKeepStr: '14'))
//         disableConcurrentBuilds()
//         timeout(time: 40, unit: 'MINUTES')
//     }
//
//     environment {
//         PYTHON_REPO = "beny14/python_app"
//         NGINX_REPO = "beny14/nginx_static"
//     }
//
//     stages {
//         stage('Detect Environment and Choose Agent') {
//             steps {
//                 script {
//                     echo "Checking environment..."
//                     if (env.KUBERNETES_SERVICE_HOST) {
//                         echo "Running in EKS. Setting up pod template..."
//                         podTemplate(yaml: '''
//                             apiVersion: v1
//                             kind: Pod
//                             spec:
//                               serviceAccountName: jenkins  # Ensure this is your Jenkins Service Account
//                               containers:
//                               - name: jnlp
//                                 image: jenkins/inbound-agent
//                                 args: ['--user', 'root', '-v', '/var/run/docker.sock:/var/run/docker.sock']
//                               - name: build
//                                 image: beny14/dockerfile_agent:latest
//                                 tty: true
//                                 volumeMounts:
//                                 - name: docker-sock
//                                   mountPath: /var/run/docker.sock
//                               volumes:
//                               - name: docker-sock
//                                 hostPath:
//                                   path: /var/run/docker.sock
//                         ''') {
//                             runPipeline()
//                         }
//                     } else {
//                         echo "Running in EC2. Using EC2 fleet agent..."
//                         label('ec2-fleet-bz2') {
//                             runPipeline()
//                         }
//                     }
//                 }
//             }
//         }
//     }
//
//     post {
//         always {
//             script {
//                 echo "Cleaning up Docker containers and images"
//                 sh "docker system prune -f --volumes || true"
//                 cleanWs()
//                 echo "Cleanup completed"
//             }
//         }
//
//         failure {
//             script {
//                 def errorMessage = currentBuild.result == 'FAILURE' ? currentBuild.description : 'Build failed'
//                 echo "Error occurred: ${errorMessage}"
//             }
//         }
//     }
// }
//
// def runPipeline() {
//     stage('Checkout') {
//         git url: 'https://github.com/beny1221g/kube_repo.git', branch: 'main'
//     }
//
//     stage('Docker Login') {
//         withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
//             script {
//                 sh "echo ${USERPASS} | docker login -u ${USERNAME} --password-stdin"
//             }
//         }
//     }
//
//     buildDockerImage('Build Python App', PYTHON_REPO, 'app/Dockerfile', 'app')
//     buildDockerImage('Build Nginx Static Site', NGINX_REPO, 'NGINX/Dockerfile', 'NGINX')
// }
//
// def buildDockerImage(String stageName, String repo, String dockerfile, String context) {
//     stage(stageName) {
//         script {
//             try {
//                 echo "Starting Docker build for ${stageName}"
//                 sh """
//                     docker build -t ${repo}:${BUILD_NUMBER} -f ${dockerfile} ${context}
//                     docker tag ${repo}:${BUILD_NUMBER} ${repo}:latest
//                     docker push ${repo}:${BUILD_NUMBER}
//                     docker push ${repo}:latest
//                 """
//                 echo "Docker build and push for ${stageName} completed"
//             } catch (Exception e) {
//                 error "Build failed for ${stageName}: ${e.getMessage()}"
//             }
//         }
//     }
// }

