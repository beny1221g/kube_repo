pipeline {
    agent { label 'ec2-fleet-bz2' }

    options {
        buildDiscarder(logRotator(daysToKeepStr: '14'))
        disableConcurrentBuilds()
        timeout(time: 40, unit: 'MINUTES')
    }

    environment {
        PYTHON_REPO = "beny14/python_app"
        NGINX_REPO = "beny14/nginx_static"
        AGENT_REPO = "beny14/dockerfile_agent" // Define agent repo
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "Checking out code from Git..."
                    git url: 'https://github.com/beny1221g/kube_repo.git', branch: 'main'
                }
            }
        }

        stage('Docker Login') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                        echo "Logging in to Docker Hub..."
                        sh "echo ${USERPASS} | docker login -u ${USERNAME} --password-stdin"
                    }
                }
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Build Python App') {
                    steps {
                        buildDockerImage('Build Python App', PYTHON_REPO, 'app/Dockerfile', 'app')
                    }
                }
                stage('Build Nginx Static Site') {
                    steps {
                        buildDockerImage('Build Nginx Static Site', NGINX_REPO, 'NGINX/Dockerfile', 'NGINX')
                    }
                }
                stage('Build Agent Image') {  // New stage to build and push agent image
                    steps {
                        script {
                            echo "Building and pushing Docker agent image..."
                            sh """
                                docker build -t ${AGENT_REPO}:${BUILD_NUMBER} -f Dockerfile_agent .
                                docker tag ${AGENT_REPO}:${BUILD_NUMBER} ${AGENT_REPO}:latest
                                docker push ${AGENT_REPO}:${BUILD_NUMBER}
                                docker push ${AGENT_REPO}:latest
                            """
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
                sh "docker system prune -f --volumes || true"
                cleanWs()
                echo "Cleanup completed"
            }
        }
        failure {
            echo "Build failed: ${currentBuild.description}"
        }
    }
}

def buildDockerImage(String stageName, String repo, String dockerfile, String context) {
    stage(stageName) {
        try {
            echo "Starting Docker build for ${stageName}"
            sh """
                docker build -t ${repo}:${BUILD_NUMBER} -f ${dockerfile} ${context}
                docker tag ${repo}:${BUILD_NUMBER} ${repo}:latest
                docker push ${repo}:${BUILD_NUMBER}
                docker push ${repo}:latest
            """
            echo "Docker build and push for ${stageName} completed"
        } catch (Exception e) {
            error "Build failed for ${stageName}: ${e.getMessage()}"
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

