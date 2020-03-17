
from app import db

class Color(db.Model):

    name = db.Column(db.String(40), primary_key=True)

    notes = db.relationship('Note', backref='color')
