from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import mapped_column , Mapped 
from sqlalchemy import Integer, String , Float 
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField , FloatField 
from wtforms.validators import DataRequired ,  NumberRange
import requests


movie_collection_url = "https://api.themoviedb.org/3/search/movie"
movie_url = 'https://api.themoviedb.org/3/movie/'
movie_img_url = 'https://image.tmdb.org/t/p/w1280' # Global

headers = {
    'Access-Control-Allow-Origin': "*",
    "accept": "application/json",
    "Authorization": "Bearer TOKEN"
}



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.sqlite3'

db = SQLAlchemy(app)

class MyForm(FlaskForm):
    rating = FloatField(label='Your Rating out of 10 e.g 7.5' , validators=[DataRequired() , NumberRange(min=0 , max=10 )])
    review = StringField(label='Your Review' , validators=[DataRequired()])
    submit = SubmitField(label='Done')

class AddMovie(FlaskForm):
    title = StringField(label='Movie Title' , validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')

class Movie(db.Model):
    id : Mapped[int] = mapped_column('movies' , primary_key=True)
    title : Mapped[str] = mapped_column(String(250),nullable=False)
    year  :  Mapped[int] = mapped_column(Integer,nullable=False)
    description  :  Mapped[str] = mapped_column(String(250),nullable=False)
    rating  :  Mapped[float] = mapped_column(Float,nullable=False)
    ranking :  Mapped[int] = mapped_column(Integer,nullable=False)
    review :  Mapped[str] = mapped_column(String(250),nullable=False)
    img_url :  Mapped[str] = mapped_column(String(250),nullable=False)

    def __init__(self , title ,year ,description , rating,ranking,review  , img_url):
        self.title  = title
        self.year  = year
        self.description  = description
        self.rating  = rating
        self.ranking  = ranking
        self.review  = review
        self.img_url  = img_url

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    movies = db.session.query(Movie).order_by(Movie.rating.desc()).all()
    i = 1
    for movie in movies:
        movie.ranking = i
        i+=1
    db.session.commit()
    # stmt = select(Movie).order_by(asc(users_table.c.name))        
    return render_template("index.html" , movies = movies)

@app.route("/edit/<int:movie_id>" , methods = ['GET' , 'POST'])
def edit(movie_id):                 #{{url_for('edit' ,movie_id =  movie.id)}}
    form = MyForm()
    movie = Movie.query.filter_by(id = movie_id).first()
    if form.validate_on_submit() and request.method=='POST':
        rating = form.rating.data           # Retreiving Form data
        review = form.review.data
        
        movie.rating = rating
        movie.review = review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie = movie , form = form)
    
@app.route("/delete/<int:movie_id>" , methods = ['GET' , 'POST'])
def delete(movie_id):                 #{{url_for('edit' ,movie_id =  movie.id)}}
    movie = Movie.query.filter_by(id = movie_id).first()
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/select/<id>')
def select(id):
    movie_url = 'https://api.themoviedb.org/3/movie/' + str(id)
    response = requests.get(movie_url,headers=headers).json()
    print(response)
    title  = response["title"]
    year  = response["release_date"]
    description  = response["overview"]
    rating = response["vote_average"]
    ranking = "None"
    review   = response["tagline"]
    try:
        img_url =  movie_img_url +response["poster_path"]
    except:
        img_url = 'None'
    print(response,'\n\n')
    print(title ,year ,description , rating,ranking,review  , img_url, '\n\n')
    movie = Movie(title , year ,description , rating , ranking , review , img_url)
    db.session.add(movie)
    db.session.commit()
    return redirect(url_for('edit' ,movie_id =  movie.id))

    
@app.route('/addMovie', methods = ['GET' , 'POST'])
def addMovie():
    form = AddMovie()
    if  form.validate_on_submit() and request.method=='POST':
        movie_name = form.title.data
        # all Movies list
        response = requests.get(movie_collection_url , headers=headers , params={'query':movie_name}).json()['results']
        return render_template('select.html' , movies = response)
    return render_template('add.html' , form = form)
if __name__ == '__main__':
    app.run(debug=True)
