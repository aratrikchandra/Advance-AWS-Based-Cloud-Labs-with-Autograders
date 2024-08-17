from flask import current_app as app, jsonify

@app.route('/')
def home():
    return jsonify(message="Welcome to the Flask Application!")

@app.route('/health')
def health():
    return jsonify(status="Healthy")

@app.route('/scale')
def scale():
    return jsonify(message="Auto-scaling endpoint")

@app.route('/metrics')
def metrics():
    return jsonify(message="Metrics endpoint")
