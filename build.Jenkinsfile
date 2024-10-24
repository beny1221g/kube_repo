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
        label 'ec2-fleet-bz2'  // Adjust this label as needed for EKS
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

        stage('Build and Push') {
            steps {
                script {
                    // Determine if running on EC2 or EKS
                    if (env.NODE_NAME.contains("ec2")) {
                        // EC2-specific build and push steps
                        echo "Running on EC2"
                        buildPythonApp(PYTHON_REPO)
                        buildNginxApp(NGINX_REPO)
                    } else if (env.NODE_NAME.contains("eks")) {
                        // EKS-specific build and push steps
                        echo "Running on EKS"
                        buildPythonAppEKS(PYTHON_REPO)
                        buildNginxAppEKS(NGINX_REPO)
                    } else {
                        error "Unknown environment: ${env.NODE_NAME}"
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

// Function to build and push Python app for EC2
def buildPythonApp(String repo) {
    try {
        echo "Starting Docker build for Python app on EC2"
        sh """
            docker build -t ${repo}:${BUILD_NUMBER} -f app/Dockerfile app
            docker tag ${repo}:${BUILD_NUMBER} ${repo}:latest
            docker push ${repo}:${BUILD_NUMBER}
            docker push ${repo}:latest
        """
        echo "Docker build and push for Python app completed on EC2"
    } catch (Exception e) {
        error "Build failed: ${e.getMessage()}"
    }
}

// Function to build and push Nginx app for EC2
def buildNginxApp(String repo) {
    try {
        echo "Starting Docker build for Nginx static site on EC2"
        sh """
            docker build -t ${repo}:${BUILD_NUMBER} -f NGINX/Dockerfile NGINX
            docker tag ${repo}:${BUILD_NUMBER} ${repo}:latest
            docker push ${repo}:${BUILD_NUMBER}
            docker push ${repo}:latest
        """
        echo "Docker build and push for Nginx static site completed on EC2"
    } catch (Exception e) {
        error "Build failed: ${e.getMessage()}"
    }
}

// Function to build and push Python app for EKS
def buildPythonAppEKS(String repo) {
    try {
        echo "Starting Docker build for Python app on EKS"
        // Add EKS-specific commands here if different from EC2
        sh """
            docker build -t ${repo}:${BUILD_NUMBER} -f app/Dockerfile app
            docker tag ${repo}:${BUILD_NUMBER} ${repo}:latest
            docker push ${repo}:${BUILD_NUMBER}
            docker push ${repo}:latest
        """
        echo "Docker build and push for Python app completed on EKS"
    } catch (Exception e) {
        error "Build failed: ${e.getMessage()}"
    }
}

// Function to build and push Nginx app for EKS
def buildNginxAppEKS(String repo) {
    try {
        echo "Starting Docker build for Nginx static site on EKS"
        // Add EKS-specific commands here if different from EC2
        sh """
            docker build -t ${repo}:${BUILD_NUMBER} -f NGINX/Dockerfile NGINX
            docker tag ${repo}:${BUILD_NUMBER} ${repo}:latest
            docker push ${repo}:${BUILD_NUMBER}
            docker push ${repo}:latest
        """
        echo "Docker build and push for Nginx static site completed on EKS"
    } catch (Exception e) {
        error "Build failed: ${e.getMessage()}"
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

