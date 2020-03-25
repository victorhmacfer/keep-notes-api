

from app import db

class Image(db.Model):

    url = db.Column(db.String(200), primary_key=True)

    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), primary_key=True)


    def to_dict(self):
        return {'url': self.url}


