from app.main import app
from app.models.database import db, User, Asset, Transaction

def print_records():
    with app.app_context():
        print("=== USERS ===")
        users = User.query.all()
        if users:
            for user in users:
                print(user.to_dict())
        else:
            print("No users found.")

        print("\n=== ASSETS ===")
        assets = Asset.query.all()
        if assets:
            for asset in assets:
                print(asset.to_dict())
        else:
            print("No assets found.")

        print("\n=== TRANSACTIONS ===")
        transactions = Transaction.query.all()
        if transactions:
            for tx in transactions:
                print(tx.to_dict())
        else:
            print("No transactions found.")

if __name__ == '__main__':
    print_records()
