import sys
sys.path.append('.')
from database import SessionLocal
from prediction import predict_career
from models import User

db = SessionLocal()
user = db.query(User).first()
if user:
    res = predict_career(skills=['Python'], db=db, current_user=user)
    print('KEYS:', res.keys())
    print('FOO:', res.get('FOO'))
else:
    print('No User found')
