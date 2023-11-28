from flask import request, render_template, current_app as app
import requests
import json
from werkzeug.utils import redirect
from db_directory.models import *
from flask.helpers import url_for

@app.route("/", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        r = requests.get(f"http://127.0.0.1:5000/api/login/{username}/{password}")
        if (r.status_code == 200):
            return redirect(url_for("home", user = username))
        else:
            return "Invalid user"    

@app.route("/<user>/home", methods = ["GET"])
def home(user):
    r = requests.get(f"http://127.0.0.1:5000/api/user/{user}")
    if (r.status_code == 200):
        return render_template("home.html", username = user)
    return "NOT FOUND"

@app.route("/<user>/home/dashboard", methods = ["GET"])
def dashboard(user):
    r = requests.get(f"http://127.0.0.1:5000/api/{user}/dashboard")
    decks = json.loads(r.text)
    if (r.status_code == 200):
        return render_template("dashboard.html", decks = decks)    
    return "NOT FOUND"

@app.route("/<user>/home/dashboard/add", methods = ["GET", "POST"])
def ViewNotAddedDashboard(user):
    r = requests.get(f"http://127.0.0.1:5000/api/{user}/dashboard/add")
    decks = json.loads(r.text)
    print(decks)
    if (r.status_code != 200):
        return "NOT FOUND"
    return render_template("DecksNotAdded.html", decks = decks)

@app.route("/<user>/home/dashboard/add/<deck_id>", methods = ["GET"])
def AddDashboard(user, deck_id):
    r = requests.post(f"http://127.0.0.1:5000/api/{user}/dashboard/add/{deck_id}")
    if (r.status_code != 200):
        return "NOT FOUND"
    return redirect(url_for("ViewNotAddedDashboard", user = user))

@app.route("/<user>/home/dashboard/<deck_id>/review/<index>", methods = ["GET", "POST"])
def Review(user, deck_id, index):
    if request.method == "GET":
        r = requests.get(f"http://127.0.0.1:5000/api/review/{user}/{deck_id}/{index}")
        if r.status_code == 211:
            return "No Cards in this deck"
        card = json.loads(r.text)
        next = True
        if r.status_code == 210:
            next = False
        if (not(r.status_code == 200 or r.status_code == 210)):
            return "NOT FOUND"
        return render_template("review.html", card = card, next = next, index = index)
    else:
        score = request.form["score"]
        r = requests.put(f"http://127.0.0.1:5000/api/review/{user}/{deck_id}/{index}/{score}")
        index = int(int(index) + 1)
        if (r.status_code != 200):
            return "NOT FOUND"
        return redirect(url_for("Review", user = user, deck_id = deck_id, index = index))

@app.route("/<user>/home/dashboard/<deck_id>/review/<index>/finish", methods = ["POST"])
def FinishReview(user, deck_id, index):
    score = request.form["score"]
    r = requests.put(f"http://127.0.0.1:5000/api/review/{user}/{deck_id}/{index}/{score}")
    if (r.status_code != 200):
        return "NOT FOUND"
    r = requests.delete(f"http://127.0.0.1:5000/api/review/{user}/{deck_id}/finish")
    if (r.status_code != 200):
        return "NOT FOUND"
    return redirect(url_for("dashboard", user = user))

@app.route("/<user>/home/DeckManagement", methods = ["GET", "POST"])
def DeckManagement(user):
    r = requests.get(f"http://127.0.0.1:5000/api/user/{user}")
    if r.status_code != 200:
        return "NOT FOUND"
    r = requests.get(f"http://127.0.0.1:5000/api/deck")
    decks = json.loads(r.text)
    if (r.status_code == 200):
        return render_template("AllDecks.html", decks = decks, username = user)
    return "NOT FOUND"

@app.route("/<user>/home/DeckManagement/<deck_id>/view", methods = ["GET"])
def viewDeck(user, deck_id):
    r = requests.get(f"http://127.0.0.1:5000/api/user/{user}")
    if r.status_code != 200:
        return "NOT FOUND"
    r = requests.get(f"http://127.0.0.1:5000/api/deck/{deck_id}/cards")
    cards = json.loads(r.text)
    print(cards)
    if (r.status_code == 200):
        return render_template("DeckContents.html", cards = cards, user = user)
    return "NOT FOUND"

@app.route("/<user>/home/DeckManagement/<deck_id>/AddCard", methods = ["GET", "POST"])
def addCards(user, deck_id):
    r = requests.get(f"http://127.0.0.1:5000/api/user/{user}")
    if r.status_code != 200:
        return "NOT FOUND"
    if (request.method == "GET"):
        return render_template("AddCard.html")
    else:
        question = request.form["question"]
        answer = request.form["answer"]
        r = requests.post(f"http://127.0.0.1:5000/api/deck/{deck_id}/AddCard", data = {"question" : question, "answer" : answer})
        if (r.status_code != 200):
            return "Question and Answer should have atleast 1 character"
        return redirect(url_for("viewDeck", user = user, deck_id = deck_id))
        
@app.route("/<user>/home/DeckManagement/<deck_id>/<card_id>/edit", methods = ["GET", "POST"])
def EditCard(user, deck_id, card_id):
    r = requests.get(f"http://127.0.0.1:5000/api/user/{user}")
    if r.status_code != 200:
        return "NOT FOUND"
    if (request.method == "GET"):
        r = requests.get(f"http://127.0.0.1:5000/api/card/{card_id}/GetCard")
        card = json.loads(r.text)
        return render_template("EditCard.html", question = card["question"], answer = card["answer"])
    else:
        question = request.form["question"]
        answer = request.form["answer"]
        r = requests.put(f"http://127.0.0.1:5000/api/card/{card_id}/UpdateCard", data = {"question" : question, "answer" : answer})
        if (r.status_code != 200):
            return "Question and Answer should have atleast 1 character"
        return redirect(url_for("viewDeck", user = user, deck_id = deck_id))
    
@app.route("/<user>/home/DeckManagement/<deck_id>/<card_id>/delete", methods = ["GET"])
def deleteCard(user, deck_id, card_id):
    r = requests.get(f"http://127.0.0.1:5000/api/user/{user}")
    if r.status_code != 200:
        return "NOT FOUND"
    r = requests.delete(f"http://127.0.0.1:5000/api/card/{card_id}/DeleteCard")
    if (r.status_code != 200):
        return "NOT FOUND"
    return redirect(url_for("viewDeck", user = user, deck_id = deck_id))

@app.route("/<user>/home/DeckManagement/<deck_id>/edit", methods = ["GET", "POST"])
def EditDeck(user, deck_id):
    r = requests.get(f"http://127.0.0.1:5000/api/user/{user}")
    if r.status_code != 200:
        return "NOT FOUND"
    if (request.method == "GET"):
        r = requests.get(f"http://127.0.0.1:5000/api/deck/{deck_id}/view")
        deck = json.loads(r.text)
        return render_template("EditDeck.html", deck = deck)
    else:
        deck_name = request.form["deck_name"]
        r = requests.put(f"http://127.0.0.1:5000/api/deck/{deck_id}/edit", data = {"deck_name" : deck_name})
        if (r.status_code != 200):
            return "Name should have atleast 1 character"
        return redirect(url_for("DeckManagement", user = user))

@app.route("/<user>/home/DeckManagement/add", methods = ["GET", "POST"])
def AddDeck(user):
    r = requests.get(f"http://127.0.0.1:5000/api/user/{user}")
    if r.status_code != 200:
        return "NOT FOUND"
    if (request.method == "GET"):
        return render_template("AddDeck.html")
    else:
        deck_name = request.form["deck_name"]
        r = requests.post(f"http://127.0.0.1:5000/api/deck/add", data = {"deck_name" : deck_name})
        if (r.status_code != 200):
            return "Name should have atleast 1 character"
        return redirect(url_for("DeckManagement", user = user))

@app.route("/<user>/home/DeckManagement/<deck_id>/delete", methods = ["GET"])
def DeleteDeck(user, deck_id):
    r = requests.get(f"http://127.0.0.1:5000/api/user/{user}")
    if r.status_code != 200:
        return "NOT FOUND"
    r = requests.delete(f"http://127.0.0.1:5000/api/deck/{deck_id}/delete")
    if (r.status_code != 200):
        return "NOT FOUND"
    return redirect(url_for("DeckManagement", user = user))