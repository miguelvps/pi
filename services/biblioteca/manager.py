from flaskext.script import Manager

from biblioteca.app import app


manager = Manager(app)


if __name__ == "__main__":
    manager.run()
