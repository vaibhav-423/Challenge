# backend/routes.py

from flask import Blueprint, request, jsonify
from sqlalchemy import or_, func
from datetime import datetime
from .models import db, Transaction

routes = Blueprint('routes', __name__)

@routes.route('/api/init', methods=['GET'])
def initialize_database():
    from .seed import seed_database
    from flask import current_app
    seed_database(current_app)
    return jsonify({"message": "Database initialized with seed data."}), 200

@routes.route('/api/transactions', methods=['GET'])
def list_transactions():
    month = request.args.get('month')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    if not month:
        return jsonify({"error": "Month parameter is required."}), 400

    try:
        month_number = datetime.strptime(month, '%B').month
    except ValueError:
        return jsonify({"error": "Invalid month name."}), 400

    query = Transaction.query.filter(func.strftime('%m', Transaction.date_of_sale) == f"{month_number:02d}")

    if search:
        search_filter = or_(
            Transaction.title.ilike(f"%{search}%"),
            Transaction.description.ilike(f"%{search}%"),
            func.cast(Transaction.price, db.String).ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    pagination = query.order_by(Transaction.id).paginate(page, per_page, error_out=False)
    transactions = [t.to_dict() for t in pagination.items]

    return jsonify({
        "transactions": transactions,
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    }), 200

@routes.route('/api/statistics', methods=['GET'])
def statistics():
    month = request.args.get('month')

    if not month:
        return jsonify({"error": "Month parameter is required."}), 400

    try:
        month_number = datetime.strptime(month, '%B').month
    except ValueError:
        return jsonify({"error": "Invalid month name."}), 400

    total_sale = db.session.query(func.sum(Transaction.price)).filter(
        func.strftime('%m', Transaction.date_of_sale) == f"{month_number:02d}",
        Transaction.status == 'sold'
    ).scalar() or 0

    total_sold = db.session.query(func.count(Transaction.id)).filter(
        func.strftime('%m', Transaction.date_of_sale) == f"{month_number:02d}",
        Transaction.status == 'sold'
    ).scalar()

    total_not_sold = db.session.query(func.count(Transaction.id)).filter(
        func.strftime('%m', Transaction.date_of_sale) == f"{month_number:02d}",
        Transaction.status == 'not sold'
    ).scalar()

    return jsonify({
        "totalSaleAmount": total_sale,
        "totalSoldItems": total_sold,
        "totalNotSoldItems": total_not_sold
    }), 200

@routes.route('/api/bar-chart', methods=['GET'])
def bar_chart():
    month = request.args.get('month')

    if not month:
        return jsonify({"error": "Month parameter is required."}), 400

    try:
        month_number = datetime.strptime(month, '%B').month
    except ValueError:
        return jsonify({"error": "Invalid month name."}), 400

    price_ranges = [
        (0, 100),
        (101, 200),
        (201, 300),
        (301, 400),
        (401, 500),
        (501, 600),
        (601, 700),
        (701, 800),
        (801, 900),
        (901, float('inf'))
    ]

    labels = []
    data = []

    for lower, upper in price_ranges:
        if upper == float('inf'):
            label = f"{lower}-above"
            count = db.session.query(func.count(Transaction.id)).filter(
                func.strftime('%m', Transaction.date_of_sale) == f"{month_number:02d}",
                Transaction.price >= lower
            ).scalar()
        else:
            label = f"{lower}-{upper}"
            count = db.session.query(func.count(Transaction.id)).filter(
                func.strftime('%m', Transaction.date_of_sale) == f"{month_number:02d}",
                Transaction.price.between(lower, upper)
            ).scalar()
        labels.append(label)
        data.append(count)

    return jsonify({
        "labels": labels,
        "data": data
    }), 200

@routes.route('/api/pie-chart', methods=['GET'])
def pie_chart():
    month = request.args.get('month')

    if not month:
        return jsonify({"error": "Month parameter is required."}), 400

    try:
        month_number = datetime.strptime(month, '%B').month
    except ValueError:
        return jsonify({"error": "Invalid month name."}), 400

    categories = db.session.query(
        Transaction.category,
        func.count(Transaction.id)
    ).filter(
        func.strftime('%m', Transaction.date_of_sale) == f"{month_number:02d}"
    ).group_by(Transaction.category).all()

    result = {category: count for category, count in categories}

    return jsonify(result), 200

@routes.route('/api/combined-data', methods=['GET'])
def combined_data():
    month = request.args.get('month')
    if not month:
        return jsonify({"error": "Month parameter is required."}), 400

    from flask import current_app
    from .routes import list_transactions, statistics, bar_chart, pie_chart
    # Reuse the functions to get data
    transactions_response = list_transactions()
    statistics_response = statistics()
    bar_chart_response = bar_chart()
    pie_chart_response = pie_chart()

    if transactions_response[1] != 200:
        return transactions_response
    if statistics_response[1] != 200:
        return statistics_response
    if bar_chart_response[1] != 200:
        return bar_chart_response
    if pie_chart_response[1] != 200:
        return pie_chart_response

    combined = {
        "transactions": transactions_response[0].json["transactions"],
        "statistics": statistics_response[0].json,
        "barChart": bar_chart_response[0].json,
        "pieChart": pie_chart_response[0].json
    }

    return jsonify(combined), 200
