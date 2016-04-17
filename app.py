from flask import Flask, request
from clarifai.client import ClarifaiApi
import urllib2
from bs4 import BeautifulSoup
import sendgrid

from twilio import twiml

app_id = '<client_id>'
client_secret = '<client_secret>'

clarifai_api = ClarifaiApi(app_id, client_secret)
sg = sendgrid.SendGridClient('<SENDGRID_APIKEY>')

app = Flask(__name__)

def clarifai_rec(img_url):
	result = clarifai_api.tag_image_urls(img_url)
	retval = result['results'][0]['result']['tag']['classes'][0]
	return retval

def get_shop_link(item):
	item = item.replace(" ", "+")
	base_url = "http://www.amazon.com/s?url=search-alias%3Daps&field-keywords=" + item
	url_parse = urllib2.urlopen(base_url)
	soup = BeautifulSoup(url_parse, "html.parser")

	final_link = ""
	productDivs = soup.findAll('li', attrs={'id' : 'result_1'})
	for div in productDivs:
    		final_link = div.a['href']
	return final_link


@app.route('/sms', methods=['POST'])
def sms():
	get_item = clarifai_rec(request.values.get('MediaUrl0'))
	text_body = request.values.get('Body')
	text_body = text_body.lower()
	link = get_shop_link(get_item)

	message = sendgrid.Mail()

	message.add_to(text_body)
	message.set_from("hackrutest@gmail.com")
	message.set_subject("Your Amazon Link")
	message.set_html(link)

	sg.send(message)
	return "Works"


if __name__ == "__main__":
    app.run(debug=True,host = '0.0.0.0')
