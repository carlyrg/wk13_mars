# basic flask app to render stuff
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

app = Flask(__name__)
# basic flask app to render stuff
from flask import Flask, render_template, redirect
from flask import jsonify
from flask import request
# from mission_to_mars_cg import scrape, marsFacts
import mission_to_mars_cg



app.config['MONGO_DBNAME'] = 'mars'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mars'
mongo = PyMongo(app)



@app.route('/')
def scrape_mars():

  mars_tweet = dict(mongo.db.tweet.find_one({}))
  mars_news = dict(mongo.db.news.find_one({}))
  mars_img = dict(mongo.db.feature_img.find_one({}))
  hemisphere_images = dict(mongo.db.hemisphere_images.find_one({}))
  mars_table = mission_to_mars_cg.marsFacts()
  print(mars_table)
  return render_template("scrape_mars.html", mars_tweet=mars_tweet, mars_news=mars_news, mars_img=mars_img, mars_hemispheres=hemisphere_images, mars_table=mars_table) 

@app.route('/scrape')
def scrape():
  mars = mongo.db.mars 
  mars_data = mission_to_mars_cg.scrape()
  mars.update({}, mars_data, upsert = True)
  return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
  app.run(debug=True, port=5545)

