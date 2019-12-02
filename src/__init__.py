from flask import Flask, jsonify


@app.route('/')
def root():
    return jsonify(['Hello', 'World'])