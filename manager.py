from flask import Flask


app = Flask(__name__)


@app.rout('/index')
def index():
    return 'index'


if __name__ == '__main__':
    app.run()
