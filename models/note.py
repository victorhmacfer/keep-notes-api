

from app import db
from .image import Image

from collections import OrderedDict


labels = db.Table('labels',
    db.Column('label_text', db.String(30), db.ForeignKey('label.text'), primary_key=True),
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True)
)

class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    text = db.Column(db.String(4000), nullable=False)
    pinned = db.Column(db.Boolean, nullable=False)
    archived = db.Column(db.Boolean, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    color_name = db.Column(db.Integer, db.ForeignKey('color.name'), nullable=False)

    images = db.relationship('Image', backref='note')
    labels = db.relationship('Label', secondary=labels, lazy='subquery',
        backref='notes')


    def to_json_dict(self):
        the_dict = OrderedDict()
        the_dict['id'] = str(self.id)
        the_dict['title'] = self.title
        the_dict['text'] = self.text
        the_dict['pinned'] = 'true' if self.pinned else 'false'
        the_dict['archived'] = 'true' if self.archived else 'false'
        the_dict['user_id'] = str(self.user_id)
        the_dict['color_name'] = self.color_name

        image_dicts_list = [i.to_dict() for i in self.images]
        the_dict['images'] = image_dicts_list

        # SORTS THE LABEL DICTS BY THE TEXT STRING SO IT ALWAYS PRODUCES
        # THE SAME LIST FOR OUTPUT TO THE CLIENT.
        label_dicts_list = [lab.to_dict() for lab in self.labels]
        label_dicts_list.sort(key=lambda d: d['text'])
        
        the_dict['labels'] = label_dicts_list

        return the_dict



def create_note_from_json_dict(json_dict):
    user_id = int(json_dict['user_id'])
    title = json_dict['title']
    text = json_dict['text']
    pinned = True if json_dict['pinned'] == 'true' else False
    archived = True if json_dict['archived'] == 'true' else False
    color_name = json_dict['color_name']

    the_note = Note(
        user_id=user_id,
        title=title,
        text=text,
        pinned=pinned,
        archived=archived,
        color_name=color_name)

    for i in json_dict['images']:
        img = Image(url=i['url'], note_id=the_note.id)
        the_note.images.append(img)

    for label in json_dict['labels']:
        label_text = label['text']
        label_in_db = Label.find_by_text(label_text)
        if label_in_db is not None:
            the_label = label_in_db
        else:
            the_label = Label(text=label_text)
        the_note.labels.append(the_label)

    return the_note



class Label(db.Model):
    text = db.Column(db.String(30), primary_key=True)

    @classmethod
    def find_by_text(cls, txt):
        return cls.query.filter_by(text=txt).first()

    def to_dict(self):
        return {'text': self.text}
