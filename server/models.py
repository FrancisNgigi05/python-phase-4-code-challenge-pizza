from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    # add serialization rules
 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    pizzas = association_proxy('restaurant_pizzas', 'pizza', creator=lambda pizza_obj: Restaurant(pizza=pizza_obj))


    def __repr__(self):
        return f"<Restaurant {self.name}>"
    
    def to_dictt(self):
        body = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
        }

        return body


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    # add serialization rules
    serialize_rules = ('-restaurant_pizzas.pizza',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')

    restaurants = association_proxy('restaurant_pizzas', 'restaurant', creator=lambda restaurant_obj: Restaurant(restaurant=restaurant_obj))


    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"
    
    def to_dictt(self):
        body = {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }
        return body


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    # add serialization rules
    serialize_rules = ('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas',)

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    # add relationships
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')

    # add validation
    @validates('price')
    def validates_price(self, key, price):
        if not isinstance(price, int) or price < 1 or price > 30:
            raise ValueError('The price should be an integer between 1 and 30')
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
