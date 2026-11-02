from flask import jsonify


def ok(payload, status=200):
    return jsonify(payload), status


def not_found(message):
    return jsonify({"error": message}), 404


def server_error(message):
    return jsonify({"error": message}), 500
