pipeline {
    agent any

    environment {
        registryApp        = "priyabratakhandual/tata-webhook"        // App repo
        registryNginx      = "priyabratakhandual/tata-webhook-nginx"  // Nginx repo
        registryCredential = "dockerhub-credentials"                  // Jenkins DockerHub credentials
        ec2SshCredential   = "ec2-ssh-key"                            // Jenkins EC2 SSH key
        ec2HostCred        = "ec2-host-ip"                            // Jenkins Secret Text for EC2 IP
    }

    stages {
        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Build & Push Docker Images") {
            steps {
                script {
                    docker.withRegistry('', registryCredential) {
                        retry(3) {
                            // Build & push tata-webhook image
                            def appImage = docker.build("${registryApp}:prod-${BUILD_NUMBER}", "-f Dockerfile .")
                            appImage.push("prod-${BUILD_NUMBER}")
                            appImage.push("latest")

                            // Build & push nginx image
                            def nginxImage = docker.build("${registryNginx}:prod-${BUILD_NUMBER}", "-f Dockerfile-nginx .")
                            nginxImage.push("prod-${BUILD_NUMBER}")
                            nginxImage.push("latest")
                        }
                    }
                }
            }
        }

        stage("Deploy to EC2") {
            steps {
                script {
                    withCredentials([string(credentialsId: ec2HostCred, variable: 'EC2_IP')]) {
                        sshagent([ec2SshCredential]) {
                            sh """
                                ssh -o StrictHostKeyChecking=no ubuntu@${EC2_IP} '
                                    mkdir -p /home/ubuntu/deploy &&
                                    cd /home/ubuntu/deploy &&
                                    export IMAGE_TAG=prod-${BUILD_NUMBER} &&
                                    docker-compose pull &&
                                    docker-compose up -d &&
                                    docker image prune -af
                                '
                            """
                        }
                    }
                }
            }
        }

        stage("Health Check") {
            steps {
                script {
                    withCredentials([string(credentialsId: ec2HostCred, variable: 'EC2_IP')]) {
                        retry(5) {
                            sleep 5
                            def response = sh(
                                script: "curl -s -o /dev/null -w '%{http_code}' http://${EC2_IP}/tata-webhook/ping",
                                returnStdout: true
                            ).trim()
                            if (response != '200') {
                                error("❌ Health check failed! Expected 200, got ${response}")
                            }
                        }
                        echo "✅ Health check passed with status 200"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Deployment successful! Image tags: prod-${BUILD_NUMBER}"
        }
        failure {
            echo "❌ Deployment failed. Check logs and container status."
        }
    }
}
