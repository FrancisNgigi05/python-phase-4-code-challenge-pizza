#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dictt() for restaurant in Restaurant.query.all()]
        response = make_response(restaurants, 200)
        return response

class RestaurantByIndex(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()

        if restaurant:
            response = make_response(restaurant.to_dict(), 200)

        else:
            body = {"error": "Restaurant not found"}
            response = make_response(body, 404)

        return response

class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dictt() for pizza in Pizza.query.all()]
        response = make_response(pizzas, 200)
        return response

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        if not all(key in data for key in ['price', 'pizza_id', 'restaurant_id']):
            body = {'error': ['Missing required fields: price, pizza_id, restaurant_id']}
            return make_response(body, 400)

        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data.get('price'),
                pizza_id=data.get('pizza_id'),
                restaurant_id=data.get('restaurant_id')
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            new_restaurant_pizza_dict = new_restaurant_pizza.to_dict()
            response = make_response(new_restaurant_pizza_dict, 201)
        except Exception as e:
            db.session.rollback()
            body = {"error": ['Validation error']}
            response = make_response(body, 400)
        
        return response

api.add_resource(RestaurantPizzas, '/restaurant_pizzas')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantByIndex, '/restaurants/<int:id>')
api.add_resource(Restaurants, '/restaurants')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
