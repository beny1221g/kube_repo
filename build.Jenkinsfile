pipeline {
    agent none
    options {
        buildDiscarder(logRotator(daysToKeepStr: '14'))
        disableConcurrentBuilds()
        timeout(time: 40, unit: 'MINUTES')
    }
    parameters {
        choice(
            name: 'AGENT_TYPE',
            choices: ['k8s', 'ec2'],
            description: 'Choose the agent to use: Kubernetes (k8s) or EC2'
        )
    }
    environment {
        PYTHON_REPO = "beny14/python_app"
        NGINX_REPO = "beny14/nginx_static"
        POD_LABEL = "my-k8s-agent" // Define the POD_LABEL here
        POD_NAME = "my-k8s-agent" // Define the POD_NAME here
    }

    stages {
        stage('Detect Environment and Choose Agent') {
            steps {
                script {
                    echo "Checking environment and selecting agent..."
                    if (params.AGENT_TYPE == 'k8s') {
                        echo "Using Kubernetes agent..."

                        // Check if the pod already exists
                        def podExists = sh(script: "kubectl get pods -n bz-jenkins | grep ${POD_NAME} || true", returnStatus: true) == 0

                        // Create the pod only if it doesn't exist
                        if (!podExists) {
                            echo "Pod ${POD_NAME} does not exist. Creating it..."
                            sh """
                                kubectl run ${POD_NAME} --image=beny14/dockerfile_agent:latest --restart=Never --labels=${POD_LABEL}=true --namespace=bz-jenkins
                            """
                        } else {
                            echo "Pod ${POD_NAME} already exists. Using it..."
                        }

                        // Now run the pipeline using the created pod
                        podTemplate(label: POD_LABEL, yaml: '''
                            apiVersion: v1
                            kind: Pod
                            spec:
                              serviceAccountName: jenkins
                              containers:
                              - name: jnlp
                                image: jenkins/inbound-agent
                                args: ['-url', 'http://k8s-bzjenkin-releasej-c663409355-6f66daf7dc73980b.elb.us-east-2.amazonaws.com:8080', 'JenkinsAgent']
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
                        ''') {
                            node(POD_LABEL) {
                                runPipeline() // Call the function without additional node context
                            }
                        }
                    } else {
                        echo "Using EC2 fleet agent..."
                        node('ec2-fleet-bz2') {
                            runPipeline() // Call the function without additional node context
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
                def cleanupNode = params.AGENT_TYPE == 'ec2' ? 'ec2-fleet-bz2' : POD_LABEL
                node(cleanupNode) {
                    sh "docker system prune -f --volumes || true"
                    cleanWs()
                }
                echo "Cleanup completed"
            }
        }
        failure {
            echo "Build failed: ${currentBuild.description}"
        }
    }
}

def runPipeline() {
    stage('Checkout') {
        git url: 'https://github.com/beny1221g/kube_repo.git', branch: 'main'
    }

    stage('Docker Login') {
        withCredentials([usernamePassword(credentialsId: 'dockerhub_key', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
            sh "echo ${USERPASS} | docker login -u ${USERNAME} --password-stdin"
        }
    }

    buildDockerImage('Build Python App', PYTHON_REPO, 'app/Docke


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

