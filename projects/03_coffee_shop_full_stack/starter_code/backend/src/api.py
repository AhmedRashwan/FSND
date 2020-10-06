import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ------------------------
# Get All Drinks
# ------------------------
@app.route("/drinks")
def get_drinks():
    try:
        drinks = db.session.query(Drink).all()
        if drinks is not None:
            return jsonify({
                'success': True,
                'drinks': [drink.short() for drink in drinks]
            })
        else:
            abort(404)
    except Exception:
        abort(422)


# ------------------------
# Get Drinks Details
# ------------------------
@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_details():
    try:
        drinks = db.session.query(Drink).all()
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except Exception as ex:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()


# ------------------------
# Add New Drink
# ------------------------
@app.route("/drinks", methods=['POST'])
@requires_auth("post:drinks")
def create_drink():
    try:
        # Read Drink Data
        request_data = request.get_json()
        drink_title = request_data.get('title', 'title')
        drink_recipe = json.dumps(request_data.get('recipe', []))

        # Check if the data is exist or return error message
        if drink_title or drink_recipe is not None:
            drink = Drink(title=drink_title, recipe=drink_recipe)
            drink.insert()
            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        else:
            abort(422)

    except Exception as ex:
        print(ex)
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()


# -----------------------------
# Edit Drink Details
# -----------------------------
@app.route("/drinks/<int:id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(id):
    try:
        # Get the drink by id
        drink = db.session.query(Drink).filter(Drink.id == id).one_or_none()
        # Check if the drink is exist
        if drink is None:
            return abort(404)

        # Edit Drink object data then update
        drink.title = request.args.get("title", drink.title)
        drink.recipe = json.dumps(request.args.get('recipe', json.dumps(drink.recipe)))
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception as ex:
        print(ex)
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()


# ------------------------
# Delete Drink by given id
# ------------------------
@app.route("/drinks/<int:id>", methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(id):
    try:
        # Get the drink by id
        drink = db.session.query(Drink).filter(Drink.id == id).one_or_none()

        # Check if the drink is exist or retun error message
        if drink is None:
            abort(404)

        # delete drink
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })
    except Exception:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()


# ---------------------------
# ERROR HANDLING
# ---------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "not found",
        "error": 404
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "message": "method not allowed",
        "error": 405
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "message": "unprocessable",
        "error": 422
    }), 422


@app.errorhandler(500)
def internalError(error):
    return jsonify({
        "success": False,
        "message": "internal server error",
        "error": 500
    }), 500
