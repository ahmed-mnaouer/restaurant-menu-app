from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class FoodItem(db.Model):
    __tablename__ = 'food_items'

    # Ensure the primary key uses the database/autoincrement sequence
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    variant = db.Column(db.String(100), nullable=True)
    course = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.Text)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    country_origin = db.Column(db.String(50))
    availability = db.Column(db.String(50))
    calories = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "variant": self.variant,
            "course": self.course,
            "ingredients": self.ingredients,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "country_origin": self.country_origin,
            "availability": self.availability,
            "calories": self.calories
        }
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="customer")  # 'manager' or 'customer'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "role": self.role}
