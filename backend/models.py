# backend/models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    date_of_sale = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # e.g., 'sold', 'not sold'
    category = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "dateOfSale": self.date_of_sale.strftime('%Y-%m-%d'),
            "status": self.status,
            "category": self.category
        }
