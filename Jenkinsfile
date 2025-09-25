pipeline {
    agent any

    environment {
        registry           = "priyabratakhandual/tata-webhook"   // Docker Hub repo
        registryCredential = "dockerhub-credentials"             // Jenkins credential ID for Docker Hub
        ec2SshCredential   = "ec2-ssh-key"                       // Jenkins credential ID for EC2 SSH key
        ec2HostCred        = "ec2-host-ip"                       // Jenkins Secret Text credential for EC2 public IP
    }

    stages {
        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Build Docker Image") {
            steps {
                script {
                    dockerImage = docker.build("${registry}:prod-${BUILD_NUMBER}")
                }
            }
        }

        stage("Push Docker Image") {
            steps {
                script {
                    docker.withRegistry('', registryCredential) {
                        dockerImage.push("prod-${BUILD_NUMBER}")
                        dockerImage.push("latest")
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
                                    cd /home/ubuntu/deploy &&
                                    export IMAGE_TAG=prod-${BUILD_NUMBER} &&
                                    docker-compose pull &&
                                    docker-compose up -d
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
                        def response = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://${EC2_IP}/tata-webhook/ping",
                            returnStdout: true
                        ).trim()

                        if (response != '200') {
                            error("❌ Health check failed! Expected 200, got ${response}")
                        } else {
                            echo "✅ Health check passed with status 200"
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Deployment successful!"
        }
        failure {
            echo "❌ Deployment failed. Check logs and container status."
        }
    }
}
