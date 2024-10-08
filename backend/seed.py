# backend/seed.py

import requests
from datetime import datetime
from .models import db, Transaction

def seed_database(app):
    with app.app_context():
        db.create_all()

        # Fetch data from third-party API
        response = requests.get('https://s3.amazonaws.com/roxiler.com/product_transaction.json')
        if response.status_code == 200:
            data = response.json()
            for item in data:
                # Parse dateOfSale
                try:
                    date_of_sale = datetime.strptime(item['dateOfSale'], '%Y-%m-%d')
                except ValueError:
                    continue  # Skip records with invalid dates

                transaction = Transaction(
                    product_id=item.get('product_id'),
                    title=item.get('title'),
                    description=item.get('description'),
                    price=item.get('price'),
                    date_of_sale=date_of_sale,
                    status=item.get('status'),
                    category=item.get('category')
                )
                db.session.add(transaction)
            db.session.commit()
            print("Database seeded successfully.")
        else:
            print("Failed to fetch data from the third-party API.")
