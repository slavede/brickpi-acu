#!/usr/bin/env python

import json

from flask import Flask,request,Response
from acu import Acu

import logging
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__)

acu_data_file = open('data/acu.dat', 'r')
data = acu_data_file.read()
acu_data_file.close()

initial_azimuth = float(data.split(',')[0])
initial_elevation = float(data.split(',')[1])

file_handler = TimedRotatingFileHandler('/var/log/brickpi-flask.log', when="d", interval=1, backupCount=2)
app.logger.addHandler(file_handler)
acu = Acu(logger = app.logger, initial_azimuth=initial_azimuth, initial_elevation=initial_elevation)

@app.route('/acu/azimuth', methods=['PUT'])
def azimuth_put():
	acu.set_azimuth(float(request.data))

	response = Response(
		response = str(acu.get_azimuth()),
		status = 200,
		mimetype = "html/text");

	acu_data_file = open('data/acu.dat', 'w')
	acu_data_file.write(str(acu.get_azimuth()) + ',' + str(acu.get_elevation()))

	return response

@app.route('/acu/azimuth', methods=['GET'])
def azimuth_get():
	response = Response(
		# response = str(acu.get_brick_pi_azimuth() - 180),
		response = str(acu.get_azimuth()),
		status = 200,
		mimetype = "html/text");

	return response


@app.route('/acu/elevation', methods=['PUT'])
def elevation_put():
	print "Got elevation put:" + str(request.data)
	acu.set_elevation(float(request.data))

	response = Response(
		response = str(acu.get_elevation()),
		status = 200,
		mimetype = "html/text");

	acu_data_file = open('data/acu.dat', 'w')
	acu_data_file.write(str(acu.get_azimuth()) + ',' + str(acu.get_elevation()))
	return response

@app.route('/acu/elevation/change', methods=['PUT'])
def change_elevation():

	acu.change_elevation(float(request.data))

	response = Response(
		response = str(acu.get_elevation()),
		status = 200,
		mimetype = "html/text");

	return response

@app.route('/acu/azimuth/change', methods=['PUT'])
def change_azimuth():

	acu.change_azimuth(float(request.data))

	response = Response(
		response = str(acu.get_azimuth()),
		status = 200,
		mimetype = "html/text");

	return response

@app.route('/acu/elevation', methods=['GET'])
def elevation_get():
	response = Response(
		# response = str(acu.get_brick_pi_elevation()),
		response = str(acu.get_elevation()),
		status = 200,
		mimetype = "html/text");

	return response


@app.route('/acu/reset_azimuth', methods=['PUT'])
def reset_azimuth():

	acu.reset_azimuth()

	response = Response(
		response = json.dumps(
			{
			}),
		status = 200,
		mimetype = "application/json");

	return response

@app.route('/acu/reset_elevation', methods=['PUT'])
def reset_elevation():

	acu.reset_elevation()

	response = Response(
		response = json.dumps(
			{
			}),
		status = 200,
		mimetype = "application/json");

	return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
