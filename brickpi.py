#!/usr/bin/env python

import json

from flask import Flask,request,Response
from acu import Acu

import logging
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__)

file_handler = TimedRotatingFileHandler('/var/log/brickpi-flask.log')
app.logger.addHandler(file_handler)
acu = Acu(logger = app.logger)

@app.route('/acu/azimuth', methods=['PUT'])
def azimuth_put():

	acu.set_azimuth(int(request.json['value']))

	response = Response(
		response = json.dumps(
			{
				"value" : acu.get_azimuth(),
				"brick_pi_value" : acu.get_brick_pi_azimuth() - 180
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


@app.route('/acu/elevation', methods=['PUT'])
def elevation_put():

	acu.set_elevation(int(request.json['value']))

	response = Response(
		response = json.dumps(
			{
				"value" : acu.get_elevation(),
				"brick_pi_value" : acu.get_brick_pi_elevation()
			}),
		status = 200,
		mimetype = "application/json");

	return response

@app.route('/acu/elevation', methods=['GET'])
def elevation_get():
	response = Response(
		response = json.dumps(
			{
				"value" : acu.get_elevation()
			}),
		status = 200,
		mimetype = "application/json");

	return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)