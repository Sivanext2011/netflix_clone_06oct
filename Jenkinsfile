pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_REPO = 'sivanext/netflix_clone'
        DOCKER_IMAGE_TAG = "sivanext/netflix_clone:${env.BUILD_ID}" // Use BUILD_ID for dynamic tagging
        DOCKER_IMAGE_LATEST = "sivanext/netflix_clone:latest"
        KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt"
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
                    // Build the image with the build ID tag
                    def image = docker.build(DOCKER_IMAGE_TAG)

                    // Tag the image as 'latest' for convenience
                    image.tag('latest')
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'DOCKERHUB_CREDENTIALS') {
                        // Push the image with build ID tag
                        docker.image(DOCKER_IMAGE_TAG).push()

                        // Push the 'latest' tag
                        docker.image(DOCKER_IMAGE_LATEST).push()
                    }
                }
            }
        }

        stage('Prepare Kubeconfig') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'kubeconfig-credentials', variable: 'KUBE_CONFIG_FILE')]) {
                        def kubeConfigContent = readFile(KUBE_CONFIG_FILE)
                        writeFile(file: 'kubeconfig.txt', text: kubeConfigContent)
                        sh 'kubectl get nodes' // Verify Kubernetes access
                    }
                }
            }
        }

        stage('Create Kubernetes Secret') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''
                            kubectl create secret docker-registry my-registry-secret \
                                --docker-server=https://index.docker.io/v1/ \
                                --docker-username=${DOCKER_USERNAME} \
                                --docker-password=${DOCKER_PASSWORD} \
                                --docker-email=sivanext@gmail.com \
                                --namespace=staging || true
                                
                            kubectl create secret docker-registry my-registry-secret \
                                --docker-server=https://index.docker.io/v1/ \
                                --docker-username=${DOCKER_USERNAME} \
                                --docker-password=${DOCKER_PASSWORD} \
                                --docker-email=sivanext@gmail.com \
                                --namespace=prod || true
                        '''
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Deploy the specific image version with the BUILD_ID
                    sh 'kubectl set image deployment/netflix-clone netflix-clone=sivanext/netflix_clone:${env.BUILD_ID} --namespace=prod'
                }
            }
        }

        stage('Expose via Load Balancer') {
            steps {
                script {
                    sh 'kubectl apply -f k8s/service.yaml'
                }
            }
        }

        stage('Approval') {
            steps {
                script {
                    input 'Approve Deployment to Production?'
                }
            }
        }

        stage('Deploy to Staging Namespace') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    // Apply staging environment deployment
                    sh 'kubectl apply -f k8s/deployment-prod.yaml'
                    sh 'kubectl apply -f k8s/service-prod.yaml'
                }
            }
        }
    }
}
