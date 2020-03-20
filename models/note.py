

from app import db
from .image import Image


labels = db.Table('labels',
    db.Column('label_text', db.String(30), db.ForeignKey('label.text'), primary_key=True),
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True)
)

class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    is_pinned = db.Column(db.Boolean, nullable=False)
    is_archived = db.Column(db.Boolean, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    text = db.Column(db.String(4000), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    color_name = db.Column(db.Integer, db.ForeignKey('color.name'), nullable=False)

    images = db.relationship('Image', backref='note')
    labels = db.relationship('Label', secondary=labels, lazy='subquery',
        backref='notes')

    # FIXME: handle keyerrors and bad values for keys
    @classmethod
    def from_json_dict(cls, json_dict):
        user_id = int(json_dict['user_id'])
        title = json_dict['title']
        text = json_dict['text']
        is_pinned = True if json_dict['pinned'] == 'true' else False
        is_archived = True if json_dict['archived'] == 'true' else False
        color_name = json_dict['color_name']

        the_note = cls(
            user_id=user_id, 
            title=title,
            text=text,
            is_pinned=is_pinned,
            is_archived=is_archived,
            color_name=color_name)

        for i in json_dict['images']:
            img = Image(url=i['url'], note_id=the_note.id)
            the_note.images.append(img)

        for label_text in json_dict['labels']:
            the_label = Label(text=label_text)
            the_note.labels.append(the_label)
        
        return the_note
                  



    def to_dict(self):
        return {'user_id': self.user_id, 'title': self.title, 'text': self.text,
            'pinned': self.is_pinned, 'archived': self.is_archived,
            'color_name': self.color_name}





class Label(db.Model):
    text = db.Column(db.String(30), primary_key=True)

