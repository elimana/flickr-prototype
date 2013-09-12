import requests
import json
from flask import Flask
from flask import render_template
from flask import request
from datetime import datetime
import googleizer
import os

g = googleizer.Googleizer()
app = Flask(__name__)
API_KEY = os.environ['FLICKR_KEY']

def getJSON(text, address, radius):
	if text == '' or address == '' or radius == '':
		text = 'single origin'
		address = '60-64 Reservoir St, Surry Hills NSW'
		radius = 0.2

	location = g.maps.geocode.forward(address)
	lat = float(location[0]['geometry']['location']['lat'])
	lon = float(location[0]['geometry']['location']['lng'])

	input_data = {'text': text, 'lat': lat, 'lon': lon, 'radius': radius*5, 'sort': 'date-posted-desc', 'method': 'flickr.photos.search', 'format': 'json', 'api_key': API_KEY}
	request = requests.get("http://ycpi.api.flickr.com/services/rest/", params = input_data)
	photos = json.loads(request.text.lstrip("jsonFlickrApi(").rstrip(")"))
	photos_out = int(photos['photos']['total'])

	input_data = {'text': text, 'lat': lat, 'lon': lon, 'radius': radius, 'sort': 'date-posted-desc', 'method': 'flickr.photos.search', 'format': 'json', 'api_key': API_KEY, 'extras': 'url_m, owner_name, date_upload'}
	request = requests.get("http://ycpi.api.flickr.com/services/rest/", params = input_data)
	photos = json.loads(request.text.lstrip("jsonFlickrApi(").rstrip(")"))
	photos_in = int(photos['photos']['total'])

	return (photos, photos_in, photos_out)

def getInfo(photos):
	info = []
	for photo in photos['photos']['photo']:
		title = photo['title']
		user = photo['ownername']
		date = datetime.fromtimestamp(float(photo['dateupload']))

		url = photo['url_m']
		info += [{'title': title, 'user': user, 'date': date, 'url': url}]
	return info

@app.route('/', methods = ['GET','POST'])
def new_index():
	info = None
	form = dict()
	photos_in = int()
	photos_out = int()
	percentage_in = ''
	radius = float()
	if request.method == 'POST':
		text = request.form['text']
		address = request.form['address']
		radius = float(request.form['radius'])
		photos, photos_in, photos_out = getJSON(text, address, radius)
		info = getInfo(photos)
		if photos_in > 0 and photos_out > 0:
			percentage_in = "{percent:.2f}".format(percent=((float(photos_in)/photos_out)*100))
		print info
	return render_template('index.html', form=request.form, info=info, photos_in=photos_in, photos_out=photos_out, percentage_in=percentage_in, radius=radius)

if __name__ == '__main__':
    app.run(debug=True)

