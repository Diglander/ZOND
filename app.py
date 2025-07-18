from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Привет, мир Flask!</h1><p>Мое первое приложение работает!</p>'

if __name__ == '__main__':
    app.run(debug=True)