from re import DEBUG
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash,jsonify,g
from werkzeug.exceptions import abort
import sqlite3
import logging
#keep count of all connections created till now
_count = 0

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global _count
    connection = sqlite3.connect('database.db')
    _count = _count + 1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post


# Define the main route of the web application 
@app.route('/')
def index():
    app.logger.info("Getting DB Connection")
    connection = get_db_connection()
    app.logger.info("Got DB Connection")
    posts = connection.execute('SELECT * FROM posts').fetchall()
    app.logger.info("Number of posts %s", len(posts))
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info("The article '%s' does not exist", post_id)
      return render_template('404.html'), 404
    else:
      app.logger.info("Article '%s' retrieved", post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("'About Us' page is retrieved")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info("A new article '%s' created successfully", title)
            return redirect(url_for('index'))

    return render_template('create.html')

#Define the healthz endpoint
@app.route("/healthz")
def healthz():
    try:
        connection = get_db_connection()
        curzor = connection.cursor()
        curzor.execute("SELECT count(title) from posts")
        result = curzor.fetchone()
        number_posts = result[0]
        connection.close
        return jsonify("result","OK - healthy")
    except Exception:
        return jsonify("result","ERROR - unhealthy"),500 

#Define the metrics endpoint
@app.route("/metrics")
def metrics():
    connection = get_db_connection()
    curzor = connection.cursor()
    curzor.execute("SELECT count(title) from posts")
    result = curzor.fetchone()
    number_posts = result[0]
    app.logger.info("Count of pozts - %s", number_posts)
    connection.close
    return jsonify(db_connection_count=_count, post_count=number_posts),200


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level= logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
