# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```
for whom using windows :-

```
cmd.exe /c " psql -U USERNAME trivia < trivia.psql"
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

# API Reference
## Getting started
- BaseURLs :- this app working locally now, so you can test run it on you local machine <br>
1- Frontend-url :- this url to test the react app view http://127.0.0.1:3000 <br>
2- Backend-url : this url to test the flask app http://127.0.0.1:5000

## Error Handling
- Errors returned as a json object contains the error code and the message as the following:
```
{
  "error": 404,
  "message": "not found",
  "success": false
}
```
the types of errors handled by API: <br> 
400: Bad Request<br>
404 : Not Found<br>
405: Method Not Allowed<br>
422: Unproccessable<br>
500: Internal Server Error<br>

## End points

### Categories :

GET  '/categories'

- General : <br>
1- Fetch all distinct categories that related to qusetions <br>
2- Request Arguments: None <br>
3- Returns: An object that contains the type and the id in key:value pairs format. 
- sample ```curl http://127.0.0.1:5000/categories```
```
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
```

GET '/categories/<int:category_id>/questions'
- General : <br>
1- Fetch all questions related to specified category <br>
2- Request Arguments: category id <br>
3- Returns: An object that contains list of questions in key:value pairs format. 
- sample ```curl http://127.0.0.1:5000/categories/1/questions```

```
"questions": [
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Alexander Fleming",
      "category": 1,
      "difficulty": 3,
      "id": 21,
      "question": "Who discovered penicillin?"
    }],
  "success": true
```

### Questions :
 all the end points related to questions :

GET '/questions'
- General : <br>
1- Fetch all questions<br>
2- Request Arguments: (optional) page id <br>
3- Returns: An object that contains list of the questions,total_questions,categories in key:value format. 
- sample ```curl http://127.0.0.1:5000/questions```
```
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "questions": [
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }],
    "total_questions": 38 
}
```
POST '/questions'
- General : <br>
1- the end point used for Add new question<br>
2- Request Arguments: question, answer, category, difficulty <br>
3- Returns: An object that contain a success message 
- sample ```curl -X POST http://127.0.0.1:5000/questions -H 'Content-type:application/json' -d '{"question": "Is a test questions?","answer": "yes, it is ","difficulty": "3","category": "2"}' ```

```
{
    "message": "Question added Successfully",
    "success": true
}
```

POST '/questions/search'
- General : <br>
1- the end point used for search for a specified questions by search_term<br>
2- Request Arguments: searchTerm <br>
3- Returns: An object that contain list of questions, categories that related to the search term 
- sample ```curl -X POST http://127.0.0.1:5000/questions/search -H 'Content-type:application/json' -d '{"searchTerm": "world cup"}' ```

```
{
    "categories": {
        "6": "Sports"
    },
    "questions": [
        {
            "answer": "Brazil",
            "category": 6,
            "difficulty": 3,
            "id": 10,
            "question": "Which is the only team to play in every soccer World Cup tournament?"
        },
        {
            "answer": "Uruguay",
            "category": 6,
            "difficulty": 4,
            "id": 11,
            "question": "Which country won the first ever soccer World Cup in 1930?"
        }
    ],
    "totalQuestions": 2
}
```
DELETE '/questions/<int:question_id>'
- General : <br>
1- the end point used for Delete a question with a given id<br>
2- Request Arguments: quesion id <br>
3- Returns: An object that contain success message for deleteing
- sample ```curl -X DELETE http://127.0.0.1:5000/questions/1 ```

```
{
  "message": "Order Deleted Successfully",
  "succes": true
}
```
### Quizzes :
- General : <br>
1- the end point used for get a random questions in the selected category and keep track with the asked question to ignore it in the next questions<br>
2- Request Arguments: category_id, category type, list of the previous asked questions to keep track with<br>
3- Returns: An object that contain a new questions in the given category and the list of the previous asked questions
- sample ```curl -X POST http://127.0.0.1:5000/quizzes -H 'Content-type:application/json' -d '{"previous_questions":[],"quiz_category":{"type":"Geography","id":"3"}}' ```
```
{
    "question": {
        "answer": "Lake Victoria",
        "category": 3,
        "difficulty": 2,
        "id": 13,
        "question": "What is the largest lake in Africa?"
    },
    "success": true
}
```


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```