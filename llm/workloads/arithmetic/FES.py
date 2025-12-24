#!/usr/bin/env python3

from flask import Flask, request, jsonify

app = Flask(__name__)

# Define a route to add two numbers
@app.route('/add', methods=['GET'])
def add_numbers():
    # Get 'a' and 'b' from query parameters
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    
    if a is None or b is None:
        return jsonify({"error": "Both 'a' and 'b' are required as query parameters."}), 400
    
    result = a + b
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
