from flask import Flask


app = Flask(__name__)
@app.route('/health')
def health_check():
    return 'Health',200
@app.route('/readiness')
def health_check():
    return 'Ready',200

@app.route('/')
def hello_world():
    return 'Hso, World!'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)