from flask import current_app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(current_app)
class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String, primary_key = True)
    password = db.Column(db.String, nullable = False)
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Card(db.Model):
    __tablename__ = 'card'
    card_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    question = db.Column(db.String, nullable = False)
    answer = db.Column(db.String, nullable = False)
    def __init__(self,  question, answer):
        self.question = question
        self.answer = answer

class Deck(db.Model):
    __tablename__ = 'deck'
    deck_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    deck_name = db.Column(db.String, nullable = False)
    cards = db.relationship("Card", secondary = "deck_content")
    def __init__(self,  deck_name):
        self.deck_name = deck_name

class DeckContent(db.Model):
    __tablename__ = 'deck_content'
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.deck_id"), primary_key = True)
    card_id = db.Column(db.Integer, db.ForeignKey("card.card_id"), primary_key = True)
    def __init__(self,  deck_id, card_id):
        self.deck_id = deck_id
        self.card_id = card_id

class CardProgress(db.Model):
    __tablename__ = 'card_progress'
    username = db.Column(db.String, db.ForeignKey("user.username"), primary_key = True)
    card_id = db.Column(db.Integer, db.ForeignKey("card.card_id"), primary_key = True)
    card_score = db.Column(db.Integer, nullable = False)
    def __init__(self,  username, card_id, card_score):
        self.username = username
        self.card_id = card_id
        self.card_score = card_score

class DeckProgress(db.Model):
    __tablename__ = 'deck_progress'
    username = db.Column(db.String, db.ForeignKey("user.username"), primary_key = True)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.deck_id"), primary_key = True)
    deck_score = db.Column(db.Float, nullable = False)
    last_reviewed = db.Column(db.String, nullable = False)
    def __init__(self,  username, deck_id, deck_score, last_reviewed):
        self.username = username
        self.deck_id = deck_id
        self.deck_score = deck_score
        self.last_reviewed = last_reviewed





      

