import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "password"
        self.database_path = "postgres://{}:{}@{}/{}".format(self.database_user, self.database_password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.question = {
                'question': 'is a test Question ?!',
                'answer': 'yes',
                'category': '2',
                'difficulty': '1'
        }
        self.quiz = {
                'quiz_category': {
                    'type': 'Art',
                    'id': '2'
                },
                'previous_questions': [1, 2, 16]
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertTrue(data['categories'])

    def test_405_get_categories(self):
        res = self.client().post("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_404_get_paginated_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "not found")
        self.assertEqual(data['error'], 404)

    def test_delete_question(self):
        question = db.session.query(Question).first()
        question_id = question.format()['id']

        res = self.client().delete('/questions/' + str(question_id) + '')
        data = json.loads(res.data)

        question = db.session.query(Question).filter(Question.id == question_id).first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['succes'], True)
        self.assertEqual(data['message'], "Order Deleted Successfully")
        self.assertEqual(question, None)

    def test_404_delete_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        question = db.session.query(Question).filter(Question.id == 100).first()
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "not found")
        self.assertEqual(question, None)

    def test_post_new_question(self):
        res = self.client().post('/questions', json=self.question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question added Successfully')

    def test_405_if_new_question_not_allowed(self):
        fakeQuestion = self.question
        fakeQuestion['question'] = None
        res = self.client().post('/questions', json=fakeQuestion)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_category_questions(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_404_if_category_questions_not_found(self):
        res = self.client().get('/categories/2000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')

    def test_get_quiz_questions(self):
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(len(data['question']))

    def test_422_if_quiz_questions_unproccessable(self):
        fakeQuiz = self.quiz
        fakeQuiz['quiz_category'] = None
        res = self.client().post('/quizzes', json=fakeQuiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unproccessable')

    def test_search_for_questions(self):
        res = self.client().post('/questions/search', json={"searchTerm":"Cup"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])

    def test_404_search_for_questions(self):
        res = self.client().post('/questions/search', json={"searchTerm":"NO_TERM_FOUND"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
