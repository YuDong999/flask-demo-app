from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    version = os.getenv('VERSION', '1.0.0')
    return f"""
    <html>
        <head><title>CI/CD Demo</title></head>
        <body>
            <h1>🚀 CI/CD 流水线演示应用</h1>
            <p>版本: {version}</p>
            <p>构建时间: {os.getenv('BUILD_TIME', '未知')}</p>
            <p>环境: {os.getenv('ENVIRONMENT', 'development')}</p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "service": "flask-demo"}

@app.route('/api/info')
def info():
    return {
        "name": "flask-demo-app",
        "version": os.getenv('VERSION', '1.0.0'),
        "environment": os.getenv('ENVIRONMENT', 'development')
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
