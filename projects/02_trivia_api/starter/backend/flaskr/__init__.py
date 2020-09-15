import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db
QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Header', 'Content-type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
        return response

    # ------------------------------
    # Get all Categories
    # -------------------------------
    @app.route('/categories')
    def getCategories():
        try:
            categories = {}
            query = db.session.query(Category).all()
            for category in query:
                categories[category.id] = category.type

            return jsonify({
              "categories": categories
            }), 200
        except Exception:
            db.session.close()
            abort(422)

    # ---------------------------------
    # handle GET request for questions
    # ---------------------------------
    @app.route('/questions')
    def getQuestions():
        try:
            categories = {}
            # Pagination
            page_num = request.args.get('page', 1, type=int)
            start = (page_num - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            # Questions
            questions = db.session.query(Question).all()
            questions = [question.format() for question in questions]

            # Categories relates to returned questions
            category_ids = db.session.query(Question).distinct(Question.category).all()
            for category in category_ids:
                category_data = db.session.query(Category).get(category.category)
                categories[category_data.id] = category_data.type

            if not questions[start:end]:
                abort(404)
            else:
                return jsonify({
                  'questions': questions[start:end],
                  'total_questions': len(questions),
                  'categories': categories,
                })
        except Exception:
            abort(404)

    # -----------------------------------
    # DELETE question using a question ID
    # -----------------------------------
    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        question = db.session.query(Question).filter(Question.id == question_id).one_or_none()
        if question is None:
            abort(404)
        else:
            question.delete()
            return jsonify({
                    "succes": True,
                    'message': 'Order Deleted Successfully'
                    }), 200

    # --------------------------------------
    # POST a new question
    # --------------------------------------
    @app.route("/questions", methods=["POST"])
    def create_question():
        request_data = request.get_json()
        question = request_data.get('question')
        answer = request_data.get('answer')
        category = request_data.get('category')
        difficulty = request_data.get('difficulty')
        if question and answer and category and difficulty is not None:
            question = Question(question=question,
                                answer=answer,
                                category=category,
                                difficulty=difficulty)
            question.insert()
            return jsonify(
                         {"success": True,
                          'message': 'Question added Successfully'
                          }), 201
        else:
            abort(405)

    # ---------------------------------------------
    # Search for a question
    # ---------------------------------------------
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        categories = {}
        request_data = request.get_json()
        search_term = request_data.get('searchTerm')
        questions = db.session.query(Question).filter(Question.question.ilike('%' + search_term + '%')).all()

        # Categories relates to returned questions
        for category in questions:
            category_data = db.session.query(Category).get(category.category)
            if category_data.type not in categories:
                categories[category_data.id] = category_data.type

        return jsonify({
                      'questions': [question.format() for question in questions],
                      'totalQuestions': len(questions),
                      'categories': categories
                      })

    # ---------------------------------------------------
    # Get questions of category
    # ---------------------------------------------------
    @app.route("/categories/<int:category_id>/questions")
    def get_category_questions(category_id):
        questions = db.session.query(Question).filter(Question.category == category_id).all()
        if len(questions) == 0:
            abort(404)
        else:
            return jsonify({
                          'success': True,
                          'questions': [question.format() for question in questions]
                    }), 200

    # -------------------------------------
    # Handle quizzes
    # -------------------------------------
    @app.route("/quizzes", methods=['POST'])
    def letus_play():
        request_data = request.get_json()
        quiz_category = request_data.get('quiz_category')
        previous_questions = request_data.get('previous_questions')
        if quiz_category and previous_questions is not None:
            if quiz_category['id'] == 0:
                question = db.session.query(Question).filter(~Question.id.in_(previous_questions)).first()
            else:
                question = db.session.query(Question).filter(and_(Question.category == quiz_category['id'], ~Question.id.in_(previous_questions))).first()

            if question is None:
                question = False
            else:
                question = question.format()

            return jsonify({
                          'success': True,
                          'question': question
                  }), 200
        else:
            abort(422)

    # ---------------------------
    # ERROR HANDLING
    # ---------------------------
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
          "success": False,
          "message": "bad request",
          "error": 400
        }), 400

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
          "message": "unproccessable",
          "error": 422
        }), 422

    @app.errorhandler(500)
    def internalError(error):
        return jsonify({
          "success": False,
          "message": "internal server error",
          "error": 500
        }), 500

    return app
