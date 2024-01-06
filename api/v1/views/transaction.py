#!/usr/bin/env python3
"""Transaction view"""
from api.v1.views import app_views
from api.v1.auth.middleware import token_required
from api.models.user import User
from api.models.transaction import Transaction
from flask import abort, jsonify, request, Response
import json


@app_views.route("/transactions", methods=["POST"])
@token_required
def create_transaction(current_user: User) -> Response:
    """POST /api/v1/transactions

    Form body:
      - category_id
      - budget_id
      - goal_id
      - type
      - amount
      - date
      - description
    """
    payload = request.form
    if "category_id" not in payload:
        abort(400, "category_id is missing")
    if "budget_id" not in payload:
        abort(400, "budget_id is missing")
    if "goal_id" not in payload:
        abort(400, "goal_id is missing")
    if "type" not in payload:
        abort(400, "type is missing")
    if "amount" not in payload:
        abort(400, "amount is missing")
    if "date" not in payload:
        abort(400, "date is missing")
    if "description" not in payload:
        abort(400, "description is missing")
    try:
        transaction = Transaction(**payload)
        transaction.user_id = current_user.id
        transaction.save()
        return jsonify(json.loads(transaction.to_json())), 201
    except Exception as e:
        abort(400, e)


@app_views.route("/transactions", methods=["GET"])
@token_required
def get_transactions(current_user: User) -> Response:
    """GET /api/v1/transactions
    Retrieve all transactions for the current user
    """
    transactions = Transaction.objects(user_id=current_user.id)
    return jsonify(json.loads(transactions.to_json()))


@app_views.route("/transactions/<transaction_id>", methods=["GET"])
@token_required
def get_transaction(current_user: User, transaction_id: str) -> Response:
    """GET /api/v1/transactions/<transaction_id>
    Retrieve a single transaction
    """
    transaction = Transaction.objects(id=transaction_id).first()
    if transaction is None:
        abort(404)
    if transaction.user_id != current_user.id:
        abort(403)
    return jsonify(json.loads(transaction.to_json()))


@app_views.route("/transactions/<transaction_id>", methods=["PUT"])
@token_required
def update_transaction(current_user: User, transaction_id: str) -> Response:
    """PUT /api/v1/transactions/<transaction_id>
    Update a single transaction

    Form body:
      - category_id (optional)
      - budget_id (optional)
      - goal_id (optional)
      - type (optional)
      - amount (optional)
      - date (optional)
      - description (optional)

    Return:
      - Updated transaction in JSON
      - 404 if transaction_id is not found
      - 403 if transaction does not belong to current user
      - 400 if transaction update fails
    """
    transaction = Transaction.objects(id=transaction_id).first()
    if transaction is None:
        abort(404)
    if transaction.user_id != current_user.id:
        abort(403)
    payload = request.form

    try:
        if "category_id" in payload:
            transaction.category_id = payload["category_id"]
        if "budget_id" in payload:
            transaction.budget_id = payload["budget_id"]
        if "goal_id" in payload:
            transaction.goal_id = payload["goal_id"]
        if "type" in payload:
            transaction.type = payload["type"]
        if "amount" in payload:
            transaction.amount = payload["amount"]
        if "date" in payload:
            transaction.date = payload["date"]
        if "description" in payload:
            transaction.description = payload["description"]
        transaction.save()
        return jsonify(json.loads(transaction.to_json()))
    except Exception as e:
        abort(400, e)


@app_views.route("/transactions/<transaction_id>", methods=["DELETE"])
@token_required
def delete_transaction(current_user: User, transaction_id: str) -> Response:
    """DELETE /api/v1/transactions/<transaction_id>
    Delete a single transaction

    Return:
      - 200 on successful delete
      - 404 if transaction_id is not found
      - 403 if transaction does not belong to current user
      - 400 if transaction delete fails
    """
    transaction = Transaction.objects(id=transaction_id).first()
    if transaction is None:
        abort(404)
    if transaction.user_id != current_user.id:
        abort(403)
    try:
        transaction.delete()
        return jsonify({}), 200
    except Exception as e:
        abort(400, e)
