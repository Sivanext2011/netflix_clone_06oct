pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_REPO = 'sivanext/netflix_clone'
        DOCKER_IMAGE_TAG = "sivanext/netflix_clone:${env.BUILD_ID}"
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

                        // Set the KUBECONFIG environment variable for the shell command
                        sh 'export KUBECONFIG=${WORKSPACE}/kubeconfig.txt'

                        // Verify Kubernetes access
                        sh 'kubectl get nodes'
                    }
                }
            }
        }


		stage('Create Kubernetes Secret') {
			steps {
				script {
					// Set the KUBECONFIG for this stage
					sh 'export KUBECONFIG=${WORKSPACE}/kubeconfig.txt'
					
					// Use the withCredentials block to access the Docker Hub credentials
					withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
						sh '''
							kubectl create secret docker-registry my-registry-secret \
								--docker-server=https://index.docker.io/v1/ \
								--docker-username=${DOCKER_USERNAME} \
								--docker-password=${DOCKER_PASSWORD} \
								--docker-email=sivanext@gmail.com \
								--namespace=staging
						'''
						
												sh '''
							kubectl create secret docker-registry my-registry-secret \
								--docker-server=https://index.docker.io/v1/ \
								--docker-username=${DOCKER_USERNAME} \
								--docker-password=${DOCKER_PASSWORD} \
								--docker-email=sivanext@gmail.com \
								--namespace=prod
						'''
					}
				}
			}
		}


        stage('Deploy to Kubernetes') {
            steps {
                script {
                    sh 'export KUBECONFIG=${WORKSPACE}/kubeconfig.txt'
                    sh 'kubectl apply -f k8s/deployment.yaml'
                }
            }
        }

        stage('Expose via Load Balancer') {
            steps {
                script {
                    sh 'export KUBECONFIG=${WORKSPACE}/kubeconfig.txt'
                    sh 'kubectl apply -f k8s/service.yaml'
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    sh 'export KUBECONFIG=${WORKSPACE}/kubeconfig.txt'
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
                    sh 'export KUBECONFIG=${WORKSPACE}/kubeconfig.txt'
                    sh 'kubectl apply -f k8s/deployment-prod.yaml'
					sh 'kubectl apply -f k8s/service-prod.yaml'
                }
            }
        }
    }
}
