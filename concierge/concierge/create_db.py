from concierge import create_app, db

app = create_app()
ctx = app.test_request_context()
ctx.push()
db.drop_all()
db.create_all()
ctx.pop()

