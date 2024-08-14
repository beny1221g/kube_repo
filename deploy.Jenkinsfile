pipeline {
    agent any

    parameters {
        string(name: 'IMAGE_NAME', defaultValue: 'beny14/python_app', description: 'Name of the Docker image')
        string(name: 'BUILD_NUMBER', defaultValue: '', description: 'Build number of the Docker image to deploy')
    }

    stages {
        stage('Download Artifacts') {
            steps {
                copyArtifacts(projectName: 'app_build', filter: 'k8s/*.yaml', target: 'k8s')
                  }
                                    }


        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "Applying Kubernetes configurations"

                    // Apply deployments
                    sh 'kubectl apply -f k8s/nginx-deployment.yaml -n benyz'
                    sh 'kubectl apply -f k8s/app-deployment.yaml -n benyz'

                    // Apply services and ingress
                    sh 'kubectl apply -f k8s/nginx-service.yaml -n benyz'
                    sh 'kubectl apply -f k8s/nginx-ingress.yaml -n benyz'

                    echo "Kubernetes configurations applied"

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