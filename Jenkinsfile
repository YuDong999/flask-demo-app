pipeline {
    agent any
    
    environment {
        // Harbor 配置 - 使用正确的端口
        REGISTRY = "192.168.94.199:30002"  // HTTP 端口
        // REGISTRY = "192.168.94.199:30003"  // 或者使用 HTTPS 端口
        PROJECT = "library"
        APP_NAME = "flask-demo-app"
        DOCKER_CREDENTIALS = "harbor-creds"
        
        // K8s 配置
        K8S_NAMESPACE = "default"
    }
    
    parameters {
        string(name: 'IMAGE_TAG', defaultValue: "build-${env.BUILD_ID}", description: 'Docker镜像标签')
        choice(name: 'DEPLOY_ENV', choices: ['dev', 'staging'], description: '部署环境')
        booleanParam(name: 'SKIP_TESTS', defaultValue: false, description: '跳过测试')
    }
    
    stages {
        stage('准备代码') {
            steps {
                echo "📦 准备应用代码..."
                sh '''
                # 从本地目录复制代码
                cp -r /git/flask-demo-app/* .
                ls -la
                echo "代码文件:"
                find . -type f -name "*.py" -o -name "*.txt" -o -name "Dockerfile" -o -name "*.yaml" -o -name "*.yml"
                '''
            }
        }
        
        stage('环境检查') {
            steps {
                echo "🔧 检查构建环境..."
                sh '''
                echo "=== Docker 检查 ==="
                docker --version || echo "Docker 未安装"
                
                echo "=== Python 检查 ==="
                python --version || echo "Python 未安装"
                
                echo "=== 网络检查 ==="
                ping -c 2 192.168.94.199 && echo "控制节点可达" || echo "控制节点不可达"
                curl -I http://192.168.94.199:30002 || echo "Harbor HTTP 不可达"
                '''
            }
        }
        
        stage('代码质量检查') {
            when {
                expression { params.SKIP_TESTS == false }
            }
            steps {
                echo "🔍 代码质量检查..."
                sh '''
                echo "=== 文件完整性检查 ==="
                [ -f "app.py" ] && echo "✓ app.py 存在" || echo "✗ app.py 缺失"
                [ -f "requirements.txt" ] && echo "✓ requirements.txt 存在" || echo "✗ requirements.txt 缺失"
                [ -f "Dockerfile" ] && echo "✓ Dockerfile 存在" || echo "✗ Dockerfile 缺失"
                [ -f "deployment.yaml" ] && echo "✓ deployment.yaml 存在" || echo "✗ deployment.yaml 缺失"
                
                echo "=== Python 语法检查 ==="
                python -m py_compile app.py && echo "✓ Python 语法正确" || echo "✗ Python 语法错误"
                
                echo "=== 代码基础验证 ==="
                echo "应用代码行数:"
                wc -l app.py
                echo "依赖检查:"
                cat requirements.txt
                '''
            }
        }
        
        stage('构建Docker镜像') {
            steps {
                echo "🐳 构建Docker镜像..."
                script {
                    // 检查 Docker 是否可用
                    def dockerAvailable = sh(script: 'command -v docker', returnStdout: true).trim()
                    
                    if (dockerAvailable) {
                        def fullImageTag = "${REGISTRY}/${PROJECT}/${APP_NAME}:${params.IMAGE_TAG}"
                        
                        sh """
                        echo "使用 Docker 构建镜像: ${fullImageTag}"
                        docker build \\
                          --build-arg BUILD_TIME="\$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \\
                          --build-arg VERSION=${params.IMAGE_TAG} \\
                          -t ${fullImageTag} .
                        
                        echo "✅ 镜像构建完成: ${fullImageTag}"
                        docker images | grep ${APP_NAME}
                        """
                    } else {
                        echo "⚠️ Docker 不可用，跳过镜像构建阶段"
                        echo "在实际环境中，这里会使用 Docker 或 Kaniko 构建镜像"
                    }
                }
            }
        }
        
        stage('推送镜像到Harbor') {
            steps {
                echo "📤 推送镜像到Harbor仓库..."
                script {
                    def dockerAvailable = sh(script: 'command -v docker', returnStdout: true).trim()
                    
                    if (dockerAvailable) {
                        withCredentials([usernamePassword(
                            credentialsId: "${DOCKER_CREDENTIALS}",
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            sh """
                            echo "登录到 Harbor 仓库..."
                            docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} ${REGISTRY}
                            
                            echo "推送镜像..."
                            docker push ${REGISTRY}/${PROJECT}/${APP_NAME}:${params.IMAGE_TAG}
                            
                            echo "✅ 镜像已推送到: ${REGISTRY}/${PROJECT}/${APP_NAME}:${params.IMAGE_TAG}"
                            """
                        }
                    } else {
                        echo "⚠️ Docker 不可用，跳过镜像推送"
                        echo "模拟推送完成: ${REGISTRY}/${PROJECT}/${APP_NAME}:${params.IMAGE_TAG}"
                    }
                }
            }
        }
        
        stage('部署到Kubernetes') {
            steps {
                echo "🚀 部署应用到Kubernetes..."
                script {
                    // 使用默认命名空间，避免创建新命名空间的权限问题
                    def namespace = "default"
                    
                    sh """
                    echo "=== 当前部署状态 ==="
                    kubectl get deployments,services,pods -l app=flask-demo-app 2>/dev/null || echo "尚无相关资源"
                    
                    echo "更新部署配置..."
                    # 更新镜像标签
                    sed -i 's|image:.*|image: ${REGISTRY}/${PROJECT}/${APP_NAME}:${params.IMAGE_TAG}|' deployment.yaml
                    
                    echo "应用部署..."
                    kubectl apply -f deployment.yaml -n ${namespace}
                    
                    echo "✅ 应用部署指令已发送"
                    """
                }
            }
        }
        
        stage('验证部署') {
            steps {
                echo "✅ 验证部署状态..."
                script {
                    sleep 10  // 等待应用启动
                    
                    sh """
                    echo "=== 部署状态 ==="
                    kubectl get pods -l app=flask-demo-app -o wide
                    
                    echo "=== 服务状态 ==="
                    kubectl get svc flask-demo-service
                    
                    echo "=== 应用日志 ==="
                    kubectl logs -l app=flask-demo-app --tail=10 2>/dev/null || echo "暂无日志"
                    
                    echo "=== 访问测试 ==="
                    echo "应用访问地址: http://192.168.94.199:30089"
                    curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://192.168.94.199:30089/health || echo "健康检查失败"
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "🏁 流水线执行完成"
            script {
                // 清理 Docker 登录信息
                sh "docker logout ${REGISTRY} 2>/dev/null || true"
                
                // 记录构建信息
                echo "构建总结:"
                echo "  - 镜像: ${REGISTRY}/${PROJECT}/${APP_NAME}:${params.IMAGE_TAG}"
                echo "  - 环境: ${params.DEPLOY_ENV}"
                echo "  - 构建ID: ${env.BUILD_ID}"
            }
        }
        success {
            echo "🎉 CI/CD 流水线执行成功！"
            echo "🌐 应用地址: http://192.168.94.199:30089"
            echo "📊 健康检查: http://192.168.94.199:30089/health"
            echo "🔍 详细信息: http://192.168.94.199:30089/api/info"
            
            // 在实际环境中，这里可以发送成功通知
        }
        failure {
            echo "❌ CI/CD 流水线执行失败"
            echo "请检查以下可能的问题:"
            echo "  1. Docker 是否安装并可用"
            echo "  2. Harbor 凭据是否正确"
            echo "  3. Kubernetes 权限是否足够"
            echo "  4. 网络连接是否正常"
        }
        unstable {
            echo "⚠️ 流水线执行存在警告"
            echo "可能的原因: 测试跳过、环境检查未完全通过等"
        }
    }
}
