#!/usr/bin/env python3

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
    return render_template('index.html', place=place, figure=Cor.plot_cases(escape(place)), regions=Cor.regions)


def main():
    app.run()


if __name__ == '__main__':
    main()
