from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health_check():
    return 'Health', 200

@app.route('/readiness')
def readiness_check():  # Renamed to `readiness_check` to avoid conflict
    return 'Ready', 200

@app.route('/')
def hello_world():
    return 'Hello, World!', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
