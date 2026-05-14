from web_app.init import create_app

app=create_app()
from web_app.init import db
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)