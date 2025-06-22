from app.main import app
from app.models.database import db, User, Asset, Transaction

with app.app_context():
    print("=== USERS ===")
    for user in User.query.all():
        print(user.to_dict())

    print("\n=== ASSETS ===")
    for asset in Asset.query.all():
        print(asset.to_dict())

    print("\n=== TRANSACTIONS ===")
    for tx in Transaction.query.all():
        print(tx.to_dict())
