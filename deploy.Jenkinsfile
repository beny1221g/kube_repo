pipeline {
    agent any

    parameters {
        string(name: 'IMAGE_NAME', defaultValue: 'beny14/polybot', description: 'Name of the Docker image')
        string(name: 'BUILD_NUMBER', defaultValue: '', description: 'Build number of the Docker image to deploy')
    }

    stages {
        stage('Push Docker Image to Nexus') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker_nexus', usernameVariable: 'USERNAME', passwordVariable: 'USERPASS')]) {
                    script {
                        def dockerImage = "${params.IMAGE_NAME}:${params.BUILD_NUMBER}"
                        echo "Starting push of Docker image ${dockerImage} to Nexus"
                        sh """
                            echo ${USERPASS} | docker login localhost:8083 -u ${USERNAME} --password-stdin
                            docker tag ${dockerImage} localhost:8083/${dockerImage}
                            docker push localhost:8083/${dockerImage}
                        """
                        echo "Docker push to Nexus completed "
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline completed"
        }
        failure {
            echo "Pipeline failed"
        }
    }
}