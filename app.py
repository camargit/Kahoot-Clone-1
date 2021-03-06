from flask import Flask, request, json, abort, jsonify, make_response
from src.routes import router
import jwt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 
from random import randint
from src.utils.crypt import forEncrypt, forDecrypt
from src.utils.authorization import generateToken
from src.utils.authorization import verifyLogin


db = SQLAlchemy()
app = Flask(__name__)
CORS(app)
app.register_blueprint(router)
app.config['JSON_SORT_KEYS'] = False

POSTGRES = {
    'user': 'postgres',
    'pw' : 'hawarihaw14',
    'db' : 'kahoot_clone',
    'host' : 'localhost',
    'port': '5432'
}

#real format = postgresql://username:password@localhost:5432/database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

db.init_app(app)
from models import *

# BEGINING OF USER ROUTES

@app.route('/register-user', methods=["POST"])
def registerUser():

    body = request.json
    try:
        user = User(
            username= body["username"],
            full_name= body["full_name"],
            password=forEncrypt(body["password"]),
            email=body["email"]
            )
        
        db.session.add(user)
        db.session.commit()

        body['message'] = "Registration Success, Please Login"
        return jsonify(body), 200
    except Exception as e:
        return(str(e)), 400

@app.route('/login-user', methods=["POST"])
def loginUser():
    body=request.json
    response= {}
    print(body['username'])
    try:
        user = User.query.filter_by(username = body['username']).first()
        if user.username == body['username'] and forDecrypt(user.password) == body['password']:
            body["token"] = generateToken(body["username"])
            body.pop("password")
            body['message'] = "Login Success, welcome {}".format(user.full_name)
            return jsonify(body), 200
        else: 
            # response['message'] = "Login Failed, username or password maybe wrong or not found"
            return "Login Failed, username or password maybe wrong or not found", 404
    except:
        return "Username is not found",404

@app.route('/get-all-users', methods=["GET"])

def getAllUsers():
    try:
        user = User.query.order_by(User.user_id).all()
        
        return jsonify([emstr.serialize()for emstr in user])

    except Exception as e:
        return(str(e))

@app.route('/delete-user-by-id/<id_>', methods=["DELETE"])
def deleteUserById(id_):
    
    try:
        user = User.query.filter_by(user_id = id_).delete()
        db.session.commit()
        
        return "User has deleted"
    except Exception as e:
        return(str(e))

# END OF USER ROUTES



# BEGINING OF QUIZ ROUTES

@app.route('/create-quiz', methods=["POST"])
def createQuiz():
    body = request.json
    
    try:
        quiz = Quiz(
            user_id=body["user_id"],
            quiz_name=body["quiz_name"],
            quiz_category=body['quiz_category'],
            quiz_desc=body["quiz_desc"]
            )
        
        db.session.add(quiz)
        db.session.commit()
        body['message'] = "Quiz name {} has added".format(quiz.quiz_name)   
        return jsonify(body),200
    except Exception as e:
        return(str(e)),400

@app.route('/get-all-quiz', methods=["GET"])
def getAllQuiz():
    try:
        quiz = Quiz.query.order_by(Quiz.quiz_id).all()
        return jsonify([emstr.serialize()for emstr in quiz])

    except Exception as e:
        return(str(e))

@app.route('/get-quiz/<id_>', methods=["GET"])
def getQuizById(id_):
    try:
        quiz = Quiz.query.filter_by(quiz_id = id_).first()
        return jsonify(quiz.serialize()), 200
    except Exception as e:
        return(str(e)), 400

@app.route('/delete-quiz-by-id/<id_>', methods=["DELETE"])
def deleteQuizById(id_):
    try:
        option = Option.query.filter_by(option_id = id_).delete()
        question = Question.query.filter_by(question_id = id_).delete()
        quiz = Quiz.query.filter_by(quiz_id = id_).delete()
        db.session.commit()
        
        return "Quiz data has deleted"
    except Exception as e:
        return(str(e))

@app.route('/update-quiz/<id_>', methods=["PUT"])
def updateQuiz(id_):    
    body = request.json
    try:
        quiz = Quiz.query.filter_by(quiz_id = id_).first()
        for key, value in body.items():
            if key == "quiz_name":
                quiz.quiz_name = value
            elif key == "quiz_category":
                quiz.quiz_category = value
            elif key == "quiz_description":
                quiz.quiz_desc = value

    except Exception as e:
        return (str(e))
    
    db.session.commit()
    return "Quiz data has updated. quiz id={}".format(quiz.quiz_id)

# END OF QUIZ ROUTES



# BEGINING OF QUESTION ROUTES

@app.route('/create-question/<quiz_id_>', methods=["POST"])
def createQuestion(quiz_id_):
    body = request.json

    option = body['answer_option']
    a=option["A"]
    b=option["B"]
    c=option["C"]
    d=option["D"]

    try:
        question = Question(
            quiz_id=quiz_id_,
            the_question=body["the-question"],
            correct_answer=body["correct-answer"]
            )

        question.answer_option = [Option(Question.question_id,a,b,c,d)]
        db.session.add(question)
        db.session.commit()
        body['message'] = "Question data has added. Question id={}".format(question.question_id)
        return jsonify(body), 200

    except Exception as e:
        return (str(e))
    
@app.route('/get-all-question', methods=["GET"])
def getAllQuestion():
    try:
        question = Question.query.order_by(Question.question_id).all()
        return jsonify([emstr.serialize()for emstr in question])

    except Exception as e:
        return(str(e))

@app.route('/get-question/<id_>', methods=["GET"])
def getQuestionById(id_):
    try:
        question = Question.query.filter_by(question_id = id_).first()
        return jsonify(question.serialize())
    except Exception as e:
        return(str(e))

@app.route('/delete-question-by-id/<id_>', methods=["DELETE"])
def deleteQuestionById(id_):
    try:
        option = Option.query.filter_by(option_id = id_).delete()
        question = Question.query.filter_by(question_id = id_).delete()
        db.session.commit()
        
        return "Question has deleted"
    except Exception as e:
        return(str(e))

@app.route('/update-question/<id_>', methods=["PUT"])
def updateQuestionById(id_,):    
    body = request.json
    try:
        question = Question.query.filter_by(question_id = id_).first()

        for key, value in body.items():
            if key == "the-question":
                question.the_question = value
            elif key == "correct-answer":
                question.correct_answer = value
                 
        option = Option.query.filter_by(option_id = id_).first()
        for key, value in body.items():   
            if key == "A":
                option.a = value
            elif key == "B":
                option.b = value
            elif key == "C":
                option.c = value
            elif key == "D":
                option.d = value               
    except Exception as e:
        return (str(e))
    
    db.session.commit()
    return "Question data has updated. question id={}".format(question.question_id)

# END OF QUESTION ROUTES



# ADD OPTION
@app.route('/add-option/<question_id_>', methods=["POST"])
def addOption(question_id_):
    body = request.json

    try:
        answer_option = Option(
            question_id=question_id_,
            a=body["A"],
            b=body["B"],
            c=body["C"],
            d=body["D"]
            )
        db.session.add(answer_option)
        db.session.commit()
        return "Option data has added. Option id={}".format(answer_option.option_id)
    except Exception as e:
        return(str(e))

@app.route('/get-all-option', methods=["GET"])
def getAllOption():
    try:
        option = Option.query.order_by(Option.option_id).all()
        return jsonify([emstr.serialize()for emstr in option])

    except Exception as e:
        return(str(e))


# END OF ADD OPTION


# BEGINING OF GAME ROUTES
@app.route('/create-game', methods=["POST"])
def createGame():
    body = request.json
    
    try:
        game = Game(
            game_pin=randint(100000, 999999),
            quiz_id=body["quiz_id"],
            )

        db.session.add(game)
        db.session.commit()
        return "Game has created. Game pin={}".format(game.game_pin)
    except Exception as e:
        return(str(e))

@app.route('/delete-game-by-id/<pin_>', methods=["DELETE"])
def deleteGame(pin_):
    try:
        game = Game.query.filter_by(game_pin = pin_).delete()
        db.session.commit()
        
        return "Game has deleted"
    except Exception as e:
        return(str(e))     

@app.route('/join-game', methods=["POST"])
def joinGame(): 
    body = request.json
    
    game = Game.query.filter_by(game_pin = body['game_pin']).first()
    try:
        if game.game_pin == body['game_pin']:
            leaderboard = Leaderboard(
                game_pin = body["game_pin"],
                player_id= body['player_id'],
                player_name=body["player_name"],
                score = body["score"]
                )
        else:
            return "game pin is not match"                
        db.session.add(leaderboard)
        db.session.commit()
        return "Player success for join the game"
    except Exception as e:
        return(str(e))                

@app.route('/get-game-info', methods=["GET"])
def getGameInfo():
    try:
        game = Game.query.order_by(Game.game_pin).all()
        return jsonify([emstr.serialize()for emstr in game])

    except Exception as e:
        return(str(e))
# END OF GAME ROUTES


# SUBMIT ANSWER
@app.route('/submit-answer/<game_pin_>', methods=["POST"])
def submitAnswer(game_pin_):
    body = request.json 

    try:

        leaderboard = Leaderboard.query.filter_by(player_id = body['player_id'], player_name=body['player_name'], game_pin=game_pin_).first()
        player_name = leaderboard.player_name
        player_id = leaderboard.player_id
        game_pin = leaderboard.game_pin
        score = leaderboard.score   

    except Exception as e:
        return(str(e))
    
    try:                        
        # game = Game.query.filter_by(game_pin = game_pin_).first()
        question = Question.query.filter_by(question_id = body['question_id']).first()    
        answer = question.correct_answer

        if answer == body['correct_answer']:
            score += 100
        else:
            return"question not found"

        leaderboard = {
            'game_pin': game_pin,
            'player_id': player_id,
            'player_name': player_name,
            'score': score
        }
        db.session.query(Leaderboard).filter(Leaderboard.player_id == player_id).update(leaderboard)
        db.session.commit()
        return "Answer is true you got 100 poin"
    except Exception as e:
        return(str(e))
# END OF SUBMIT ANSWER


# LEADERBOARD
@app.route('/leaderboard/<game_pin>', methods=['GET'])
def get_leaderboard_by_game_pin(game_pin):
    try:
        leaderboard = Leaderboard.query.filter_by(game_pin=game_pin).order_by(Leaderboard.score.desc()).all()
        return jsonify([board.serialize() for board in leaderboard])
    except Exception as e:
        return(str(e))
# END OF LEADERBOARD


if __name__ == '__main__':
    app.run(host = "0.0.0.0", port=5000)        