import os

from paste.deploy import loadapp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = loadapp('config:development.ini', relative_to='.')
    return app
