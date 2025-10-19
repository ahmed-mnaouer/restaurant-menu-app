from flask import Flask, jsonify, request
## from flask_sqlalchemy import SQLAlchemy
from models import User, db, FoodItem
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os



app = Flask(__name__)

CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Mokhtar1.@localhost:5432/restaurantdb'
## db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
## app.config['JSON_SORT_KEYS'] = False
## app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
## app.config['JSON_AS_ASCII'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fallback.db')

app.config["JWT_SECRET_KEY"] = "super-secret-key"  # change this in production
jwt = JWTManager(app)

db.init_app(app)
with app.app_context():
    db.create_all()

## starters=[{"name": "Salade César", "price" : 20, "type" : "Entrée"}, {"name": "Soupe à l'oignon", "price" : 15, "type" : "Entrée"}]
## main_courses=[{"name": "Steak frites", "price" : 40, "type" : "Plat"}, {"name": "Poulet rôti", "price" : 35, "type" : "Plat"}]
## desserts=[{"name": "Tarte Tatin", "price" : 10, "type" : "Dessert"}, {"name": "Crème brûlée", "price" : 12, "type" : "Dessert"}]

@app.get("/starters")
def get_starters():
    items = FoodItem.query.filter_by(course="Entrée").all()
    return jsonify([item.to_dict() for item in items])

@app.get("/main_courses")
def get_main_courses():
    items = FoodItem.query.filter_by(course="Plat").all()
    return jsonify([item.to_dict() for item in items])

@app.get("/desserts")
def get_desserts():
    items = FoodItem.query.filter_by(course="Dessert").all()
    return jsonify([item.to_dict() for item in items])

@app.post("/add_dish")
@jwt_required()
def add_dish():
    
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user or user.role != "manager":
        return jsonify({"msg": "Unauthorized"}), 403
    
    new_dish = request.get_json()
    if new_dish["course"] == "Entrée":
        FoodItem.query.filter_by(course="Entrée").all().append(new_dish)
        return jsonify(new_dish), 201
    elif new_dish["course"] == "Plat":
        FoodItem.query.filter_by(course="Plat").all().append(new_dish)
        return jsonify(new_dish), 201
    elif new_dish["course"] == "Dessert":
        FoodItem.query.filter_by(course="Dessert").all().append(new_dish)
        return jsonify(new_dish), 201
    else:
        return jsonify({"error": "Type de plat invalide"}), 400
    
@app.put("/update_dish/<int:dish_id>")
@jwt_required()
def update_dish(dish_id):
    
    print("HEADERS:", request.headers)
    print("TOKEN IDENTITY:", get_jwt_identity())
    print("JSON:", request.get_json())

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400   
    
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user or user.role != "manager":
        return jsonify({"msg": "Unauthorized"}), 403
    
    dish = FoodItem.query.get(dish_id)
    if not dish:
        return jsonify({"error": "Plat non trouvé"}), 404

    updated_data = request.get_json()
    dish.name = updated_data.get("name", dish.name)
    dish.price = updated_data.get("price", dish.price)
    dish.course = updated_data.get("course", dish.course)
    dish.availability = updated_data.get("availability", dish.availability)

    db.session.commit()
    return jsonify(dish.to_dict()), 200

## we will delete by id instead of name to avoid confusion with duplicate names with different ids, origin, category, etc.
@app.delete("/delete_dish/<int:dish_id>")
@jwt_required()
def delete_dish(dish_id):
    
    
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user or user.role != "manager":
        return jsonify({"msg": "Unauthorized"}), 403
    
    dish = FoodItem.query.get(dish_id)
    if dish:
        db.session.delete(dish)
        db.session.commit()
        return jsonify({"message": f"Plat '{dish.name}' supprimé avec succès"}), 200
    else:
        return jsonify({"error": "Plat non trouvé"}), 404

    
@app.get("/menu")
def get_menu():
    starters=FoodItem.query.filter_by(course="Entrée").all()
    main_courses=FoodItem.query.filter_by(course="Plat").all()
    desserts=FoodItem.query.filter_by(course="Dessert").all()
    menu = {
        
        "starters": [item.to_dict() for item in starters],
        "main_courses": [item.to_dict() for item in main_courses],
        "desserts": [item.to_dict() for item in desserts]
    }
    return jsonify(menu), 200



@app.post("/register")
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "customer")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.post("/login")
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": token,
        "user": user.to_dict()
    }), 200


@app.get("/protected")
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    return jsonify({"message": "Access granted", "user": user.to_dict()}), 200