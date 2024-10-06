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
                        // Read the content of the kubeconfig file and write it to a new file in the workspace
                        def kubeConfigContent = readFile(KUBE_CONFIG_FILE)
                        writeFile(file: 'kubeconfig.txt', text: kubeConfigContent)

                        // Verify the kubeconfig file exists
                        sh 'ls -l kubeconfig.txt' // Check if the file exists

                        // Set the KUBECONFIG environment variable
                        env.KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"

                        // Verify Kubernetes access
                        sh 'kubectl get nodes'
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    env.KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"
                    sh 'kubectl apply -f k8s/deployment.yaml'
                }
            }
        }

        stage('Expose via Load Balancer') {
            steps {
                script {
                    env.KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"
                    sh 'kubectl apply -f k8s/service.yaml'
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    env.KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"
                    sh 'python -m unittest discover tests'
                }
            }
        }

        stage('Deploy to Staging Namespace') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    env.KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"
                    sh 'kubectl apply -f k8s/deployment-staging.yaml'
                }
            }
        }
    }
}