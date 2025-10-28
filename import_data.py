import pandas as pd
from models import db, FoodItem
import os

def import_csv_data():
    csv_path = os.path.join(os.path.dirname(__file__), "restaurant_menu_refined.csv")

    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)

    if db.session.query(FoodItem).first():
        print("ℹ️  `food_items` table already contains data — skipping CSV import to avoid duplicates.")
        return

    for _, row in df.iterrows():
        item = FoodItem(
            id=int(row["id"]),
            name=row["name"],
            variant=row["variant"],
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

    try:
        db.session.commit()
        print(f"✅ Imported {len(df)} food items from {csv_path}")
    except Exception as e:
        # Rollback on any failure (e.g. unique constraint). Let the caller see the error after rollback.
        db.session.rollback()
        print(f"❌ Failed to import CSV data: {e}")
        raise
