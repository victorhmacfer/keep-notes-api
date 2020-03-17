

from app import db


labels = db.Table('labels',
    db.Column('label_text', db.String(30), db.ForeignKey('label.text'), primary_key=True),
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True)
)

class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    is_pinned = db.Column(db.Boolean, nullable=False)
    is_checklist = db.Column(db.Boolean, nullable=False)
    is_archived = db.Column(db.Boolean, nullable=False)
    title = db.Column(db.String(120), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    color_name = db.Column(db.Integer, db.ForeignKey('color.name'), nullable=False)

    lines = db.relationship('Line', backref='note')
    image = db.relationship('Image', backref='note')
    labels = db.relationship('Label', secondary=labels, lazy='subquery',
        backref='notes')


class Label(db.Model):
    text = db.Column(db.String(30), primary_key=True)

