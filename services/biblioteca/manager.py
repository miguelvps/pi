from flaskext.script import Manager, Server

from biblioteca.app import app


manager = Manager(app)
manager.add_command("runserver", Server(port = 5002))


if __name__ == "__main__":
    manager.run()
