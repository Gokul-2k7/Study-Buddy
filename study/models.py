from main import db
from auth.models import User

class Document(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    filename=db.Column(db.String(150), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Document('{self.filename}', '{self.user_id}')"