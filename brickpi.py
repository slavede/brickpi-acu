#!/usr/bin/env python

import json

from flask import Flask,request,Response
from acu import Acu

app = Flask(__name__)
acu = Acu()

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/acu/azimuth', methods=['PUT'])
def azimuth_put():

	acu.set_azimuth(int(request.json['value']))

	response = Response(
		response = json.dumps(
			{
				"azimuth" : acu.get_azimuth(),
				"brick_pi_azimuth" : acu.get_brick_pi_azimuth() - 180
			}),
		status = 200,
		mimetype = "application/json");

	return response

@app.route('/acu/azimuth', methods=['GET'])
def azimuth_get():
	response = Response(
		response = json.dumps(
			{
				"value" : acu.get_azimuth()
			}),
		status = 200,
		mimetype = "application/json");

	return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)