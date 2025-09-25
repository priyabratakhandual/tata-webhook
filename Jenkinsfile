pipeline {
    agent any

    environment {
        SSH_KEY_CRED = 'ec2-ssh-key'     // Jenkins SSH key credential ID
        HOST_IP_CRED = 'ec2-host-ip'     // Jenkins secret text credential ID
        DEPLOY_DIR   = '/home/ubuntu/tata-webhook'
        GIT_REPO     = 'https://github.com/priyabratakhandual/tata-webhook.git'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: "${GIT_REPO}"
            }
        }

        stage('Deploy to EC2') {
            steps {
                withCredentials([string(credentialsId: "${HOST_IP_CRED}", variable: 'TARGET_HOST')]) {
                    sshagent(credentials: ["${SSH_KEY_CRED}"]) {
                        sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${TARGET_HOST} '
                            set -e
                            sudo mkdir -p ${DEPLOY_DIR}
                            cd ${DEPLOY_DIR}
                            
                            # Pull latest code from GitHub
                            if [ -d .git ]; then
                                git reset --hard
                                git pull origin main
                            else
                                git clone ${GIT_REPO} ${DEPLOY_DIR}
                            fi
                            
                            # Build and run with docker-compose
                            sudo docker-compose down
                            sudo docker-compose up -d --build
                        '
                        """
                    }
                }
            }
        }

        stage('Health Check') {
            steps {
                withCredentials([string(credentialsId: "${HOST_IP_CRED}", variable: 'TARGET_HOST')]) {
                    script {
                        def response = sh (
                            script: "curl -s -o /dev/null -w '%{http_code}' http://${TARGET_HOST}/tata-webhook/ping || true",
                            returnStdout: true
                        ).trim()
                        
                        if (response != "200") {
                            error("Health check failed! Got HTTP ${response}")
                        } else {
                            echo "✅ Health check passed (HTTP 200)"
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "🎉 Deployment successful"
        }
        failure {
            echo "❌ Deployment failed. Check Jenkins logs."
        }
    }
}
