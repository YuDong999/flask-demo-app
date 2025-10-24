pipeline {
    agent any
    
    environment {
        REGISTRY = "192.168.94.198"
        PROJECT = "library"
        APP_NAME = "flask-demo-app"
        DOCKER_CREDENTIALS = "harbor-creds"
        K8S_NAMESPACE = "default"
    }
    
    parameters {
        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Docker镜像标签')
        choice(name: 'DEPLOY_ENV', choices: ['dev', 'prod'], description: '部署环境')
    }
    
    stages {
        stage('代码检出') {
            steps {
                echo "📦 从Git仓库检出代码..."
                git branch: 'main', url: 'https://github.com/你的用户名/你的仓库.git'
            }
        }
        
        stage('代码质量检查') {
            steps {
                echo "🔍 代码质量检查..."
                sh '''
                echo "检查Python文件语法..."
                python -m py_compile app.py
                echo "代码检查完成"
                '''
            }
        }
        
        stage('构建Docker镜像') {
            steps {
                echo "🐳 构建Docker镜像..."
                script {
                    // 设置构建时间
                    def buildTime = sh(script: 'date -u +"%Y-%m-%dT%H:%M:%SZ"', returnStdout: true).trim()
                    
                    sh """
                    docker build \
                      --build-arg BUILD_TIME=${buildTime} \
                      -t ${REGISTRY}/${PROJECT}/${APP_NAME}:${params.IMAGE_TAG} .
                    """
                }
            }
        }
        
        stage('推送镜像到Harbor') {
            steps {
                echo "📤 推送镜像到Harbor仓库..."
                script {
                    withCredentials([usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh """
                        docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} ${REGISTRY}
                        docker push ${REGISTRY}/${PROJECT}/${APP_NAME}:${params.IMAGE_TAG}
                        docker logout ${REGISTRY}
                        """
                    }
                }
            }
        }
        
        stage('部署到Kubernetes') {
            steps {
                echo "🚀 部署应用到Kubernetes..."
                script {
                    // 更新 deployment.yaml 中的镜像标签
                    sh """
                    sed -i 's|image:.*|image: ${REGISTRY}/${PROJECT}/${APP_NAME}:${params.IMAGE_TAG}|' deployment.yaml
                    """
                    
                    // 部署到Kubernetes
                    sh """
                    kubectl apply -f deployment.yaml -n ${K8S_NAMESPACE}
                    """
                }
            }
        }
        
        stage('验证部署') {
            steps {
                echo "✅ 验证部署..."
                script {
                    sleep 30  // 等待应用启动
                    sh """
                    echo "=== 检查Pod状态 ==="
                    kubectl get pods -l app=${APP_NAME} -n ${K8S_NAMESPACE}
                    
                    echo "=== 检查Service状态 ==="
                    kubectl get svc ${APP_NAME}-service -n ${K8S_NAMESPACE}
                    
                    echo "=== 检查应用健康状态 ==="
                    curl -s http://192.168.94.199:30089/health || echo "健康检查失败，应用可能还在启动中"
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "🏁 流水线执行完成"
            cleanWs()  // 清理工作空间
        }
        success {
            echo "🎉 部署成功！"
            echo "🌐 应用访问地址: http://192.168.94.199:30089"
            echo "📊 API信息: http://192.168.94.199:30089/api/info"
        }
        failure {
            echo "❌ 部署失败，请检查日志"
        }
    }
}
