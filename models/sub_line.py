

from app import db

class SubLine(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)

    line_id = db.Column(db.Integer, db.ForeignKey('line.id'), nullable=False)