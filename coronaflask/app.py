from flask import Flask, render_template
from markupsafe import escape

if __package__ is None:
    import corona
else:
    from . import corona

app = Flask(__name__)
Cor = corona.Corona()


@app.route("/")
def world():
    return cor('World')


@app.route('/<place>')
def cor(place):
    if place not in Cor.regions:
        place = 'World'
    return render_template('index.html', place=place, figure=Cor.plot_cases(escape(place)), regions=Cor.regions)
