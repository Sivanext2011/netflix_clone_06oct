pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_REPO = 'sivanext/netflix_clone'
        DOCKER_IMAGE_TAG = "sivanext/netflix_clone:${env.BUILD_ID}"
        DOCKER_IMAGE_LATEST = "sivanext/netflix_clone:latest" // Define the latest tag
        KUBECONFIG = "${env.WORKSPACE}/kubeconfig.txt" // Define KUBECONFIG in environment block
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

					// Tag the image as latest
					docker.image(DOCKER_IMAGE_TAG).tag('latest') // Change this line to avoid the error
				}
			}
		}

        stage('Push to DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'DOCKERHUB_CREDENTIALS') {
                        // Push the image with build ID tag
                        docker.image(DOCKER_IMAGE_TAG).push()
                        // Push the latest tag
                        docker.image(DOCKER_IMAGE_LATEST).push()
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

                        // Verify Kubernetes access
                        sh 'kubectl get nodes'
                    }
                }
            }
        }

        stage('Create Kubernetes Secret') {
            steps {
                script {
                    // Use the withCredentials block to access the Docker Hub credentials
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        // Create the Kubernetes secret in both staging and prod namespaces
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
                    sh 'kubectl apply -f k8s/deployment.yaml'
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
                    sh 'kubectl apply -f k8s/deployment-prod.yaml'
                    sh 'kubectl apply -f k8s/service-prod.yaml'
                }
            }
        }
    }
}
