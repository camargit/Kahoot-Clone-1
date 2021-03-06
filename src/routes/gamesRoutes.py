from flask import request, json, jsonify
import os
from random import randint

from . import router, baseLocation, gamesFileLocation, quizzesFileLocation, questionsFileLocation
from .quizzesRoutes import *
from .questionsRoutes import *

from ..utils.file import readFile, writeFile, checkFile
from ..utils.authorization import verifyLogin

@router.route('/game', methods = ['POST'])
@verifyLogin
def createGame():
    quizFound = False
    body = request.json

    quizzesData = readFile(quizzesFileLocation)
    
    for quiz in quizzesData["quizzes"]:
        if quiz["quiz-id"] == int(body["quiz-id"]):
            gameInfo = quiz
            break            
        
    gameInfo["game-pin"] = randint(100000, 999999)
    gameInfo["user-list"] = []
    gameInfo["leaderboard"] = []

    # create skeleton for list of game buat nulis 
    # kalau belum pernah main game sama sekali
    gamesData = {
        "game-list": []
    }
    # if quizFound:    
    if os.path.exists(gamesFileLocation):
        gamesData = readFile(gamesFileLocation)

    gamesData["game-list"].append(gameInfo)
    writeFile(gamesFileLocation, gamesData)

    return jsonify(gameInfo)

@router.route('/game/join', methods=['POST'])
def joinGame():
    body = request.json

    gamesData = readFile(gamesFileLocation)

    position = 0
    for i in range(len(gamesData["game-list"])):
        game = gamesData["game-list"][i]

        if game["game-pin"] == int(body["game-pin"]):
            if body["username"] not in game["user-list"]:               
                game["user-list"].append(body["username"])
                game["leaderboard"].append({
                    "username": body["username"],
                    "score": 0
                    })

                gameInfo = game
                position = i
                break                    
            else:
                response["message"] = "username is used, change username"
                    
    gamesData["game-list"][position] = gameInfo
    writeFile(gamesFileLocation, gamesData)

    return jsonify(gameInfo)

@router.route('/game/answer', methods=['POST'])
def submitAnswer():
    isTrue = False
    body = request.json

    questionData = readFile(questionsFileLocation)

    for question in questionData["question"]:
        if question["quiz-id"] == int(body["quiz-id"]) and question["question-number"] == int(body["question-number"]):
            if question["answer"] == body["answer"]:
                isTrue = True
    
    gamesData = readFile(gamesFileLocation)
            
    gamePosition = 0
    for i in range(len(gamesData["game-list"])):
        game = gamesData["game-list"][i]

        if game["game-pin"] == body["game-pin"]:
            if isTrue:
                userPosition = 0
                for j in range(len(game["leaderboard"])):
                    userData = game["leaderboard"][j]

                    if userData["username"] == body["username"]:
                        userData["score"] += 100

                        userInfo = userData
                        userPosition = j
                        break
                        
                game["leaderboard"][userPosition] = userInfo
                gameInfo = game
                gamePosition = i
                break

    gamesData["game-list"][gamePosition] 
    writeFile(gamesFileLocation, gamesData)

    return jsonify(request.json)

@router.route('/game/leaderboard', methods = ["POST"])
@verifyLogin
def getLeaderboard():
    body = request.json
    
    gamesData = readFile(gamesFileLocation)

    for game in gamesData["game-list"]:
        if game["game-pin"] == body["game-pin"]:
            leaderboard = game["leaderboard"]            

    for _ in range(len(leaderboard)):
        index = 0
        while index < len(leaderboard)-1:
            if leaderboard[index]["score"] < leaderboard[index+1]["score"]:
                leaderboard[index], leaderboard[index+1] = leaderboard[index+1], leaderboard[index]

            index += 1                        
    return jsonify(leaderboard)