

from app import db


class Line(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)

    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)

    sub_lines = db.relationship('SubLine', backref='line')

    