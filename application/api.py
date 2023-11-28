from flask_restful import Resource, fields, marshal_with, reqparse
import requests
import json
from application.controllers import dashboard
from db_directory.models import *
from application.validation import *
from sqlalchemy import and_
from datetime import datetime

dashboard_fields = {
    "deck_id": fields.Integer,
    "deck_name": fields.String,
    "last_reviewed": fields.String,
    "deck_score" : fields.Float
}
deck_fields = {
    "deck_id" : fields.Integer,
    "deck_name" : fields.String,
}
card_fields = {
    "card_id" : fields.Integer,
    "question" : fields.String,
    "answer" : fields.String
}
parser = reqparse.RequestParser()
parser.add_argument("question")
parser.add_argument("answer")
parser.add_argument("deck_name")
class LoginAPI(Resource):
    def get(self, username, password):
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            raise BusinessValidationError(status_code = 404, error_code = "USER002", error_message = "User does not exist")
        ValidCredentials = db.session.query(User).filter(and_(User.username == username, User.password == password)).first()
        if not ValidCredentials:
            raise BusinessValidationError(status_code = 400, error_code = "USER001", error_message = "Wrong credentials")
        return "", 200

class UserAPI(Resource):
    def get(self, username):
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            raise BusinessValidationError(status_code = 404, error_code = "USER002", error_message = "User does not exist")
        return "", 200

class DashBoardAPI(Resource):
    @marshal_with(dashboard_fields)
    def get(self, username):
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            raise BusinessValidationError(status_code = 404, error_code = "USER002", error_message = "User does not exist")
        decks = db.session.query(DeckProgress).filter(DeckProgress.username == username).all()
        dashboard = []
        for deck in decks:
            deck_name = db.session.query(Deck).filter(Deck.deck_id == deck.deck_id).first().deck_name
            dashboard.append({"deck_id": deck.deck_id, "deck_name" : deck_name, "deck_score" : deck.deck_score, "last_reviewed" : deck.last_reviewed})
        return dashboard, 200   

class AddDashboardAPI(Resource):
    @marshal_with(deck_fields)
    def get(self, username):
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            raise BusinessValidationError(status_code = 404, error_code = "USER002", error_message = "User does not exist")
        decks = db.session.query(Deck).all()
        not_added = []
        for deck in decks:
            not_added.append(deck.deck_id)
        decks = db.session.query(DeckProgress).filter(DeckProgress.username == username).all()
        for deck in decks:
            not_added.remove(deck.deck_id)
        decks = []
        for deck_id in not_added:
            deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
            decks.append(deck)
        return decks

    def post(self, username, deck_id):
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            raise BusinessValidationError(status_code = 404, error_code = "USER002", error_message = "User does not exist")
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            raise BusinessValidationError(status_code = 404, error_code = "DECK001", error_message = "Deck does not exist")
        
        deck_progress = DeckProgress(username, deck_id, 0, "Never")
        for card in deck.cards:
            card_id = card.card_id
            card_progress = CardProgress(username, card_id, 0)
            db.session.add(card_progress)
        db.session.add(deck_progress)
        db.session.commit()
        
class ReviewAPI(Resource):
    @marshal_with(card_fields)
    def get(self, username, deck_id, index):
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            raise BusinessValidationError(status_code = 404, error_code = "USER002", error_message = "User does not exist")
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            raise BusinessValidationError(status_code = 404, error_code = "DECK001", error_message = "Deck does not exist")
        if len(deck.cards) == 0:
            raise BusinessValidationError(status_code = 211, error_code = "Review001", error_message = "Deck has no cards")
        if index >= len(deck.cards):
             raise BusinessValidationError(status_code = 400, error_code = "Review002", error_message = "Index surpassed the number of cards")
        if index == len(deck.cards) - 1:
            return deck.cards[index], 210
        return deck.cards[index]

    def put(self, username, deck_id, index, score):
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            raise BusinessValidationError(status_code = 404, error_code = "USER002", error_message = "User does not exist")
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            raise BusinessValidationError(status_code = 404, error_code = "DECK001", error_message = "Deck does not exist")
        r = requests.get(f"http://127.0.0.1:5000/api/review/{username}/{deck_id}/{index}")
        card = json.loads(r.text)
        card_progress = db.session.query(CardProgress).filter(and_(CardProgress.username == username, CardProgress.card_id == card["card_id"])).first()
        if not card_progress:
            raise BusinessValidationError(status_code = 400, error_code = "CardProgress001", error_message = "User does not have this card in any of the decks")
        if score < 1 or score > 10:
            raise BusinessValidationError(status_code = 400, error_code = "Score001", error_message = "Score must be in range 1-10")
        card_progress.card_score = score
        db.session.commit()

    def delete(self, username, deck_id):
        score = 0
        count = 0
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            raise BusinessValidationError(status_code = 404, error_code = "USER002", error_message = "User does not exist")
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            raise BusinessValidationError(status_code = 404, error_code = "DECK001", error_message = "Deck does not exist")
        r = requests.get(f"http://127.0.0.1:5000/api/deck/{deck_id}/cards")
        cards = json.loads(r.text)
        for card in cards:
            card_id = card["card_id"]
            score += db.session.query(CardProgress).filter(and_(CardProgress.card_id == card_id, CardProgress.username == username)).first().card_score
            count += 1
        print(score, count)     
        score /= count
        score = round(score, 2)
        score *= 10
        deck_progress = db.session.query(DeckProgress).filter(and_(DeckProgress.username == username, DeckProgress.deck_id == deck_id)).first()
        if not deck_progress:
            raise BusinessValidationError(status_code = 400, error_code = "Review003", error_message = "User does not have this deck added")
        deck_progress.deck_score = score
        deck_progress.last_reviewed = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        db.session.commit()       

class DeckAPI(Resource):
    @marshal_with(deck_fields)
    def get(self, deck_id):
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            raise BusinessValidationError(status_code = 404, error_code = "DECK001", error_message = "Deck does not exist")
        return deck    

    def put(self, deck_id):
        args = parser.parse_args()
        deck_name = args["deck_name"]
        if deck_name.strip() == "":
            raise BusinessValidationError(status_code = 400, error_code = "DECK002", error_message = "Deck's name should have atleast 1 character")
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            raise BusinessValidationError(status_code = 404, error_code = "DECK001", error_message = "Deck does not exist")
        deck.deck_name = deck_name
        db.session.commit()

    def post(self):
        args = parser.parse_args()
        deck_name = args["deck_name"]
        if deck_name.strip() == "":
            raise BusinessValidationError(status_code = 400, error_code = "DECK002", error_message = "Deck's name should have atleast 1 character")
        deck = Deck(deck_name)
        db.session.add(deck)
        db.session.commit()

    def delete(self, deck_id):
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            raise BusinessValidationError(status_code = 404, error_code = "DECK001", error_message = "Deck does not exist")
        cards = deck.cards
        deck_contents = db.session.query(DeckContent).filter(DeckContent.deck_id == deck_id).all()
        deck_progresses = db.session.query(DeckProgress).filter(DeckProgress.deck_id == deck_id).all()
        db.session.delete(deck)
        for deck_content in deck_contents:
            db.session.delete(deck_content)
        for deck_progress in deck_progresses:
            db.session.delete(deck_progress)
        for card in cards:
            card_id = card.card_id
            card = db.session.query(Card).filter(Card.card_id == card_id).first()
            card_progresses = db.session.query(CardProgress).filter(CardProgress.card_id == card_id).all()
            for card_progress in card_progresses:
                db.session.delete(card_progress)
            db.session.delete(card)
        db.session.commit()        


class AllDecksAPI(Resource):
    @marshal_with(deck_fields)
    def get(self):
        decks = db.session.query(Deck).all()
        return decks

class AllCardsAPI(Resource):
    @marshal_with(card_fields)
    def get(self, deck_id):
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            raise BusinessValidationError(status_code = 404, error_code = "DECK001", error_message = "Deck does not exist")
        return deck.cards

class CardAPI(Resource):
    @marshal_with(card_fields)
    def get(self, card_id):
        card = db.session.query(Card).filter(Card.card_id == card_id).first()
        if not card:
            raise BusinessValidationError(status_code = 404, error_code = "CARD001", error_message = "Card does not exist")
        return card

    def put(self, card_id):
        args = parser.parse_args()
        question = args["question"]
        answer = args["answer"]
        if question.strip() == "":
            raise BusinessValidationError(status_code = 400, error_code = "CARD002", error_message = "Question should have atleast 1 character")
        if answer.strip() == "":
            raise BusinessValidationError(status_code = 400, error_code = "CARD003", error_message = "Answer should have atleast 1 character")
        card = db.session.query(Card).filter(Card.card_id == card_id).first()
        if not card:
            raise BusinessValidationError(status_code = 404, error_code = "CARD001", error_message = "Card does not exist")
        card.question = question
        card.answer = answer
        db.session.commit()

    def post(self, deck_id):
        args = parser.parse_args()
        question = args["question"]
        answer = args["answer"]
        if question.strip() == "":
            raise BusinessValidationError(status_code = 400, error_code = "CARD002", error_message = "Question should have atleast 1 character")
        if answer.strip() == "":
            raise BusinessValidationError(status_code = 400, error_code = "CARD003", error_message = "Answer should have atleast 1 character")
        card = Card(question, answer)
        db.session.add(card)
        card = db.session.query(Card).filter(and_(Card.question == question, Card.answer == answer)).all()[-1]
        deck_content = DeckContent(deck_id, card.card_id)
        deck_progresses = db.session.query(DeckProgress).filter(DeckProgress.deck_id == deck_id).all()
        for deck_progress in deck_progresses:
            username = deck_progress.username
            card_progress = CardProgress(username, card.card_id, 0)
            db.session.add(card_progress)
        db.session.add(deck_content)
        db.session.commit()
        return "", 200

    def delete(self, card_id):
        card = db.session.query(Card).filter(Card.card_id == card_id).first()
        if not card:
            raise BusinessValidationError(status_code = 404, error_code = "CARD001", error_message = "Card does not exist")
        deck_contents = db.session.query(DeckContent).filter(DeckContent.card_id == card_id).all()
        card_progresses = db.session.query(CardProgress).filter(CardProgress.card_id == card_id).all()
        for card_progress in card_progresses:
            db.session.delete(card_progress)
        db.session.delete(card)
        for deck_content in deck_contents:
            db.session.delete(deck_content)
        db.session.commit()

