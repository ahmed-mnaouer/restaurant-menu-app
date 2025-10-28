from flask import Flask, jsonify, request
from models import User, db, FoodItem
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

CORS(app)

# -------------------------------
# Database configuration
# -------------------------------
if os.getenv("DOCKER_ENV"):
    # Inside Docker
    DB_URI = "postgresql://postgres:Mokhtar1.@postgres:5432/restaurantdb"
else:
    # Local environment
    DB_URI = "postgresql://postgres:Mokhtar1.@localhost:5432/restaurantdb"

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

# -------------------------------
# JWT configuration
# -------------------------------
import secrets

_jwt_secret = os.environ.get("JWT_SECRET_KEY") or os.environ.get("SECRET_KEY") or os.environ.get("FLASK_SECRET_KEY")
if not _jwt_secret:
    # Generate a temporary secret for development if none provided.
    # In production you MUST set JWT_SECRET_KEY (or SECRET_KEY) via environment variables.
    _jwt_secret = secrets.token_urlsafe(32)
    print("⚠️  No JWT_SECRET_KEY/SECRET_KEY found in environment — using a generated temporary secret. Set JWT_SECRET_KEY in env for production.")

app.config["JWT_SECRET_KEY"] = _jwt_secret
# Ensure Flask's SECRET_KEY is set as well (some extensions/readers expect it)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or app.config.get("SECRET_KEY") or _jwt_secret

jwt = JWTManager(app)

# -------------------------------
# Database initialization function
# -------------------------------
def initialize_database(app):
    """Create tables and sanity-check DB connection."""
    print("🏗️ Initializing database...")
    with app.app_context():
        try:
            db.engine.connect()
            print("✅ Database connection successful")

            db.create_all()
            print("✅ Database tables created/verified")

            count = FoodItem.query.count()
            print(f"📊 Current food items in database: {count}")
            return True
        except Exception as e:
            print(f"❌ Database initialization error: {str(e)}")
            raise

# Automatically initialize DB only in local CLI mode
if os.environ.get("FLASK_RUN_FROM_CLI"):
    initialize_database(app)

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
    
    data = request.get_json() or {}
    
    # Required fields validation
    required_fields = ['name', 'course']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Field '{field}' is required"}), 400

    # Type conversion for numeric fields
    try:
        price = float(data['price']) if data.get('price') else None
        calories = int(data['calories']) if data.get('calories') and data['calories'] != '' else None
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid value for price (must be a number) or calories (must be an integer)"}), 400

    # Get the next available ID
    try:
        max_id = db.session.query(db.func.max(FoodItem.id)).scalar() or 0
        next_id = max_id + 1
    except Exception as e:
        print(f"❌ Failed to get next ID: {e}")
        return jsonify({"error": "Failed to generate new ID"}), 500

    # Create FoodItem and persist to DB
    item = FoodItem(
            id=next_id,  # Explicitly set the next available ID
            name=data['name'],
            variant=data.get('variant') or None,
            course=data['course'],
            ingredients=data.get('ingredients'),
            description=data.get('description'),
            price=price,
            category=data.get('category'),
            country_origin=data.get('country_origin') or None,
            availability=data.get('availability', 'Disponible'),
            calories=calories
    )

    db.session.add(item)
    try:
        db.session.commit()
    except Exception as e:
        # Rollback and return a clear error message instead of crashing
        db.session.rollback()
        print(f"❌ Failed to add dish: {e}")
        return jsonify({"error": "Failed to add dish", "details": str(e)}), 500

    return jsonify(item.to_dict()), 201
    
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

def init_db(retries=5, delay=5):
    import time
    from sqlalchemy.exc import OperationalError
    
    for attempt in range(retries):
        try:
            with app.app_context():
                db.create_all()
                from import_data import import_csv_data
                import_csv_data()
                # Ensure Postgres sequence for food_items.id is set to max(id)+1
                try:
                    # Set the sequence last_value to the current max(id).
                    # Using is_called = true so nextval() returns max(id)+1.
                    seq_sql = (
                        "SELECT setval(pg_get_serial_sequence('food_items','id'), "
                        "COALESCE((SELECT MAX(id) FROM food_items), 0), true);"
                    )
                    db.session.execute(seq_sql)
                    db.session.commit()
                    print("✅ food_items sequence synced to max(id)")
                except Exception as seq_e:
                    # Non-fatal: log and continue. This may happen on SQLite or non-Postgres DBs.
                    db.session.rollback()
                    print(f"⚠️ Could not sync food_items sequence: {seq_e}")
            print("Database initialized successfully!")
            return
        except OperationalError as e:
            if attempt + 1 == retries:
                print(f"Could not connect to database after {retries} attempts. Error: {e}")
                raise
            print(f"Database connection attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)