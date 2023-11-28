from flask import Flask
from flask_restful import Api
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///flash_card.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
api = Api(app)
app.app_context().push()

from application.api import *
from application.controllers import *

api.add_resource(LoginAPI, "/api/login/<string:username>/<string:password>")
api.add_resource(UserAPI, "/api/user/<string:username>")
api.add_resource(DashBoardAPI, "/api/<string:username>/dashboard")
api.add_resource(AddDashboardAPI, "/api/<string:username>/dashboard/add", "/api/<string:username>/dashboard/add/<int:deck_id>")
api.add_resource(ReviewAPI, "/api/review/<string:username>/<int:deck_id>/<int:index>", "/api/review/<string:username>/<int:deck_id>/<int:index>/<int:score>", "/api/review/<string:username>/<int:deck_id>/finish")
api.add_resource(DeckAPI, "/api/deck/<int:deck_id>/view", "/api/deck/add", "/api/deck/<int:deck_id>/edit", "/api/deck/<int:deck_id>/delete")
api.add_resource(AllDecksAPI, "/api/deck")
api.add_resource(AllCardsAPI, "/api/deck/<int:deck_id>/cards")
api.add_resource(CardAPI, "/api/card/<int:card_id>/GetCard", "/api/deck/<int:deck_id>/AddCard", "/api/card/<int:card_id>/DeleteCard", "/api/card/<int:card_id>/UpdateCard")
if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000, debug = True)