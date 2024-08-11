pipeline {
    agent any

    parameters {
        string(name: 'IMAGE_NAME', defaultValue: 'beny14/python_app', description: 'Name of the Docker image')
        string(name: 'BUILD_NUMBER', defaultValue: '', description: 'Build number of the Docker image to deploy')
    }

    stages {
        stage('Download Artifacts') {
            steps {
                copyArtifacts(projectName: 'app_build', filter: 'k8s/*.yaml', target: 'rmp')
                  }
                                    }


        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "Applying Kubernetes configurations"

                    // Apply deployments
                    sh 'kubectl apply -f rmp/nginx-deployment.yaml -n demo-app'
                    sh 'kubectl apply -f rmp/app-deployment.yaml -n demo-app'

                    // Apply services and ingress
                    sh 'kubectl apply -f rmp/nginx-service.yaml -n demo-app'
                    sh 'kubectl apply -f rmp/nginx-ingress.yaml -n demo-app'

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