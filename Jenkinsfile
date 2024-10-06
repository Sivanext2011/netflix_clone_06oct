pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_REPO = 'sivanext/netflix_clone'
        DOCKER_IMAGE_TAG = "sivanext/netflix_clone:${env.BUILD_ID}"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/Sivanext2011/netflix_clone.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build(DOCKER_IMAGE_TAG)
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'DOCKERHUB_CREDENTIALS') {
                        docker.image(DOCKER_IMAGE_TAG).push()
                    }
                }
            }
        }


stage('Prepare Kubeconfig') {
    steps {
        script {
            withCredentials([file(credentialsId: 'kubeconfig-credentials', variable: 'KUBE_CONFIG_FILE')]) {
                echo "Using kubeconfig from: ${KUBE_CONFIG_FILE}"
                env.KUBECONFIG = "${KUBE_CONFIG_FILE}"
		writeFile(file: 'kubeconfig.txt', text: "${KUBE_CONFIG_FILE}")

                // Verify the kubeconfig file exists
                sh 'ls -l ${KUBE_CONFIG_FILE}' // Check if the file exists

                // Verify Kubernetes access
                sh 'kubectl get nodes'
            }
        }
    }
}




        stage('Deploy to Kubernetes') {
            steps {
		env.KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"
 		sh 'kubectl get nodes'
                sh 'kubectl apply -f k8s/deployment.yaml'
            }
        }

        stage('Expose via Load Balancer') {
            steps {
		env.KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"
                sh 'kubectl apply -f k8s/service.yaml'
            }
        }

        stage('Run Unit Tests') {
            steps {
		env.KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"
                sh 'python -m unittest discover tests'
            }
        }

        stage('Deploy to Staging Namespace') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
		env.KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"
                sh 'kubectl apply -f k8s/deployment-staging.yaml'
            }
        }
    }
}