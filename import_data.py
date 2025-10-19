import pandas as pd
from models import db, FoodItem
from app import app

def import_data():
    df = pd.read_csv("restaurant_menu_refined.csv")

    with app.app_context():
        for _, row in df.iterrows():
            item = FoodItem(
                id=int(row["id"]),
                name=row["name"],
                course=row["course"],
                ingredients=row["ingredients"],
                description=row["description"],
                price=row["price"],
                category=row["category"],
                country_origin=row["country_origin"],
                availability=row["availability"],
                calories=row["calories"]
            )
            db.session.add(item)
        db.session.commit()
        print("✅ Data imported successfully!")

if __name__ == "__main__":
    import_data()
