from flask import Flask, render_template, request, redirect, url_for, send_file, make_response, send_from_directory

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.due).all()  # こちらに変更
        return render_template('index.html', posts=posts, today=date.today())

    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')

        due = datetime.strptime(due, '%Y-%m-%d')
        new_post = Post(title=title, detail=detail, due=due)

        db.session.add(new_post)
        db.session.commit()
        return redirect('/')


@app.route('/create')
def create():
    return render_template('create.html')


@app.route('/detail/<int:id>')
def read(id):
    post = Post.query.get(id)

    return render_template('detail.html', post=post)


@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')

        db.session.commit()
        return redirect('/')


@app.route('/function')
def function():
    test = 1+2
    return render_template('function.html', result=test)


@app.route('/graph1')
def graph1():
    import matplotlib.pyplot
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import io
    import random

    fig, ax = matplotlib.pyplot.subplots()
    ax.set_title(u'IMINASHI GRAPH')
    x_ax = range(1, 284)
    y_ax = [x * random.randint(436, 875) for x in x_ax]
    ax.plot(x_ax, y_ax)

    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    canvas.print_png(buf)
    data = buf.getvalue()

    response = make_response(data)
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Length'] = len(data)
    return response


@app.route('/graph2')
def graph2():
    import matplotlib.pyplot
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import random
    import string
    import os

    class TempImage(object):

        def __init__(self, file_name):
            self.file_name = file_name

        def create_png(self):
            fig, ax = matplotlib.pyplot.subplots()
            ax.set_title(u'IMINASHI GRAPH 2')
            x_ax = range(1, 284)
            y_ax = [x * random.randint(436, 875) for x in x_ax]
            ax.plot(x_ax, y_ax)

            canvas = FigureCanvasAgg(fig)
            canvas.print_figure(self.file_name)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            os.remove(self.file_name)

    chars = string.digits + string.ascii_letters
    img_name = ''.join(random.choice(chars) for i in range(64)) + '.png'

    with TempImage(img_name) as img:
        img.create_png()
        return send_file(img_name, mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True)
