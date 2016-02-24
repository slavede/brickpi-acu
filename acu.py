#!/usr/bin/env python

from BrickPi import BrickPi, PORT_A, PORT_B, time

from BrickPiOriginal import BrickPiOriginal, PORT_1, PORT_2, PORT_3, PORT_4, TYPE_SENSOR_TOUCH, BrickPiSetup, BrickPiSetupSensors, BrickPiUpdateValues, ser

import logging
import decimal
import math

class MyLogger():
	def info(self, message):
		print message

class Acu():

	def __init__(self, azimuth_power = 125, elevation_power=75, elevation_power_down=75, elevation_tollerance=5, azimuth_tolerance = 5, logger = None, azimuth_coef = 57, elevation_coef = 13, initial_elevation = 0, initial_azimuth = 0):
		self.mypi = BrickPi(ser = ser)
		
		self.azimuth_motor = self.mypi.motors[PORT_A]
		self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()
		# self.azimuth = self.azimuth_current_pos - 180
		self.azimuth = initial_azimuth
		self.azimuth_power = azimuth_power
		self.azimuth_coef = azimuth_coef

		self.elevation_motor = self.mypi.motors[PORT_B]
		self.elevation_current_pos = self.elevation_motor.get_position_in_degrees()
		# self.elevation = self.elevation_current_pos
		self.elevation = initial_elevation
		self.elevation_power = elevation_power
		self.elevation_power_down = elevation_power_down
		self.elevation_coef = elevation_coef

		self.elevation_tollerance = elevation_tollerance
		self.azimuth_tolerance = azimuth_tolerance

		self.elevation_in_progress = False
		self.azimuth_in_progress = False

		BrickPiOriginal.SensorType[PORT_1] = TYPE_SENSOR_TOUCH
		BrickPiOriginal.SensorType[PORT_2] = TYPE_SENSOR_TOUCH
		BrickPiSetupSensors()

		if (logger is None):
			self.logger = MyLogger()
		else :
			self.logger = logger;

		self.logger.info('Initial azimuth position: %d' % (self.azimuth))
		self.logger.info('Initial elevation position: %d' % (self.elevation))
		# self.logger.info('self.azimuth_touch ' + str(self.azimuth_touch))

	def reset_azimuth(self):
		BrickPiOriginal.MotorEnable[PORT_A] = 1
		BrickPiUpdateValues()

		if (BrickPiOriginal.SensorType[PORT_1] != 1):
			BrickPiOriginal.MotorSpeed[PORT_A] = 30

		BrickPiUpdateValues()

		while(BrickPiOriginal.Sensor[PORT_1] != 1):
			BrickPiUpdateValues()
			time.sleep(0.05)

		BrickPiOriginal.MotorSpeed[PORT_A] = -30
		BrickPiUpdateValues()

	def reset_elevation(self):
		BrickPiOriginal.MotorEnable[PORT_B] = 1
		BrickPiUpdateValues()

		if (BrickPiOriginal.SensorType[PORT_2] != 1):
			BrickPiOriginal.MotorSpeed[PORT_B] = 30

		BrickPiUpdateValues()

		while(BrickPiOriginal.Sensor[PORT_2] != 1):
			BrickPiUpdateValues()
			time.sleep(0.05)

		BrickPiOriginal.MotorSpeed[PORT_B] = -30
		BrickPiUpdateValues()


	def get_azimuth(self):
		return round(self.azimuth, 2)

	def get_brick_pi_azimuth(self):
		return self.azimuth_current_pos

	def get_elevation(self):
		return round(self.elevation, 2)

	def get_brick_pi_elevation(self):
		return self.elevation_current_pos

	def reverse_azimuth(self, value, sensors = []):
		self.logger.info("Reversing for " + str(value))
		# ret_value = self.azimuth_motor.rotate(self.azimuth_power, value, sensors)
		ret_value = self.azimuth_motor.rotate(self.azimuth_power, value)
		if (ret_value == False):
			return False
		self.azimuth_motor.update_position()
		self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()

	def reverse_elevation(self, value):
		self.elevation_motor.rotate(self.elevation_power, value)
		self.elevation_motor.update_position()
		self.elevation_current_pos = self.elevation_motor.get_position_in_degrees()

	def change_elevation(self, value):
		self.elevation_in_progress = True

		self.logger.info('\Changing elevation by ' + (str(value)))
		self.logger.info('self.elevation: ' + str(self.elevation));
		
		encoder_before = self.mypi.Encoder[PORT_B]
		self.logger.info('encoder_before' + str(encoder_before))

		self.logger.info("rotate_value: " + str(value))

		self.elevation_motor.rotate(self.elevation_power_down, value * self.elevation_coef)
		self.elevation_motor.update_position()

		encoder_after = self.mypi.Encoder[PORT_B]

		self.logger.info('encoder_after' + str(encoder_after))

		self.logger.info('Wanted to move for ' + str(value))
		self.logger.info('Moved for ' + str(((encoder_after - encoder_before)/self.elevation_coef)/2))

		elevation_in_progress = False

	def change_azimuth(self, value):
		self.logger.info('\Changing azimuth by ' + (str(value)))
		self.logger.info('self.azimuth: ' + str(self.azimuth));
		
		encoder_before = self.mypi.Encoder[PORT_A]
		self.logger.info('encoder_before' + str(encoder_before))

		self.logger.info("rotate_value: " + str(value))

		self.azimuth_motor.rotate(self.azimuth_power, -1 * value * self.azimuth_coef)
		self.azimuth_motor.update_position()

		encoder_after = self.mypi.Encoder[PORT_A]

		self.logger.info('encoder_after' + str(encoder_after))

		self.logger.info('Wanted to move for ' + str(value))
		self.logger.info('Moved for ' + str(((encoder_after - encoder_before)/self.azimuth_coef)/2))

	def set_elevation(self, value):
		self.elevation_in_progress = True
		self.logger.info('\nSetting elevation to ' + (str(value)))
		
		encoder_before = self.mypi.Encoder[PORT_B]
		self.logger.info('encoder_before' + str(encoder_before))

		if (value >= 90):
			value = 90

		if (value <= 0):
			value = 0

		self.logger.info('self.elevation: ' + str(self.elevation));
		self.logger.info('value_to_set: ' + str(value));

		rotate_value = None
		action = None
		if (self.elevation > value):
				rotate_value = (self.elevation - value)

				action = 'decrease'

				self.logger.info("Current position is higher than desired degree, decreasing it")
				self.logger.info("rotate_value: " + str(rotate_value))

				self.elevation_motor.rotate(self.elevation_power_down, -1 * rotate_value * self.elevation_coef)
				time.sleep(0.1)
				self.elevation_motor.update_position()

		elif (self.elevation < value):
				rotate_value = (value - self.elevation) 

				self.logger.info("Current position is lower than desired degree, increasing it")
				self.logger.info("rotate_value" + str(rotate_value))

				self.elevation_motor.rotate(self.elevation_power, rotate_value * self.elevation_coef)
				time.sleep(0.1)
				self.elevation_motor.update_position()

		time.sleep(0.1)
		encoder_after = self.mypi.Encoder[PORT_B]

		self.logger.info('encoder_after' + str(encoder_after))

		self.elevation = self.elevation + ((encoder_after - encoder_before)/float(self.elevation_coef))/2

		if (self.elevation < 0):
			self.logger.info('We went under 0, reseting it to 0')
			self.elevation = 0
		elif (self.elevation > 90):
			self.logger.info('We went over 90, reseting it to 90')
			self.elevation = 90

		self.logger.info('Wanted to move for ' + str(rotate_value))
		self.logger.info('Moved for ' + str(((encoder_after - encoder_before)/float(self.elevation_coef))/2))

		self.elevation_in_progress = False

	# def set_elevation(self, value):

	# 	if (value < 0):
	# 		value = 0

	# 	if (value > 90):
	# 		value = 90

	# 	number_of_iterations = 0
	# 	tollerant_difference = abs(value - self.elevation_current_pos)/2 if abs(value - self.elevation_current_pos) <= self.elevation_tollerance else self.elevation_tollerance

	# 	self.logger.info("\n===============================================")
	# 	self.logger.info("Elevation is at " + str(self.elevation_current_pos))
	# 	self.logger.info("Setting elevation to " + str(value))
	# 	self.logger.info("Tollerant difference is " + str(tollerant_difference))
	# 	self.logger.info("")

	# 	while (abs(value - self.elevation_current_pos) > tollerant_difference):
	# 		number_of_iterations += 1
	# 		self.logger.info("Iteration # " + str(number_of_iterations))
	# 		self.logger.info("------------------------")
	# 		self.logger.info("Elevation is at: " + str(self.elevation_current_pos))
	# 		self.logger.info("value: " + str(value))
	# 		self.logger.info("Tollerant difference is " + str(tollerant_difference))

	# 		if (self.elevation_current_pos > value):
	# 			self.logger.info("Current position is higher than desired degree, decreasing it")
				
	# 			rotate_value = (self.elevation_current_pos - value) if (number_of_iterations <= 2) else 1/float(number_of_iterations)

	# 			self.logger.info("rotate_value: " + str(rotate_value))
	# 			self.elevation_motor.rotate(self.elevation_power, -1 * rotate_value)
	# 			self.elevation_motor.update_position()

	# 			prev_position = self.elevation_current_pos;
	# 			self.elevation_current_pos = self.elevation_motor.get_position_in_degrees()

	# 			if (self.elevation_current_pos > 180 and prev_position < 180):
	# 				self.logger.info("We went overboard, we've set it at " + str(self.elevation_current_pos) + " let's reverse")
	# 				# until it becomes again lower
	# 				while self.elevation_current_pos > 180:
	# 					self.reverse_elevation(360 - self.elevation_current_pos + tollerant_difference)
	# 					self.logger.info("self.elevation_current_pos: " + str(self.elevation_current_pos))
	# 				self.logger.info("We reversed")

	# 				if (abs(self.elevation_current_pos-value) <= tollerant_difference):
	# 					value = self.elevation_current_pos
	# 					self.logger.info("updating value to after reversing because it is good enough " + str(self.elevation_current_pos))


	# 		elif (self.elevation_current_pos < value):
	# 			self.logger.info("Current position is lower than desired degree, increasing it")

	# 			rotate_value = (value - self.elevation_current_pos) if (number_of_iterations <= 2) else 1/float(number_of_iterations)

	# 			self.logger.info("rotate_value: " + str(rotate_value))
	# 			self.elevation_motor.rotate(self.elevation_power, rotate_value)
	# 			self.elevation_motor.update_position()

	# 			prev_position = self.elevation_current_pos;
	# 			self.elevation_current_pos = self.elevation_motor.get_position_in_degrees()

	# 			# we can't go overboard (modulo) when top is 90 degrees
	# 			# no need to check that here

	# 		time.sleep(0.1)

	# 	self.elevation = value

	# 	self.logger.info("New position: " + str(self.elevation_current_pos) + ", wanted: "  + str(value))
	# 	self.logger.info("===============================================\n")

	def set_azimuth(self, value):
		self.azimuth_in_progress = True
		self.logger.info('Setting azimuth to ' + (str(value)))
		
		encoder_before = self.mypi.Encoder[PORT_A]
		self.logger.info('encoder_before' + str(encoder_before))

		if (value >= 180):
			value = 179

		if (value <= -180):
			value = -180

		self.logger.info('self.azimuth: ' + str(self.azimuth));
		self.logger.info('value_to_set: ' + str(value));

		rotate_value = None
		if (self.azimuth > value):
				rotate_value = (self.azimuth - value)

				self.logger.info("Current position is higher than desired degree, decreasing it")
				self.logger.info("rotate_value: " + str(rotate_value))

				self.azimuth_motor.rotate(self.azimuth_power, rotate_value * self.azimuth_coef)
				self.elevation_motor.update_position()

		elif (self.azimuth < value):
				rotate_value = (value - self.azimuth) 

				self.logger.info("Current position is lower than desired degree, increasing it")
				self.logger.info("rotate_value" + str(rotate_value))

				self.azimuth_motor.rotate(self.azimuth_power, -1 * rotate_value * self.azimuth_coef)
				self.elevation_motor.update_position()

		encoder_after = self.mypi.Encoder[PORT_A]

		self.logger.info('encoder_after' + str(encoder_after))

		self.azimuth = self.azimuth - ((encoder_after - encoder_before)/float(self.azimuth_coef))/2

		if (self.azimuth < -180):
			self.logger.info('We went under -180, reseting it to -180');
			self.azimuth = -180

		if (self.azimuth > 179):
			self.logger.info('We went over 179, reseting it to 179');
			self.azimuth = 179

		self.logger.info('Wanted to move for ' + str(rotate_value))
		self.logger.info('Moved for ' + str(((encoder_after - encoder_before)/float(self.azimuth_coef))/2))

		self.azimuth_in_progress = False


	# def set_azimuth(self, value):
	# 	if (value >= 180):
	# 		value = 179

	# 	if (value <= -180):
	# 		value = -179

	# 	value_to_set = value + 180

	# 	number_of_iterations = 0
	# 	tollerant_difference = abs(value_to_set - self.azimuth_current_pos)/2 if abs(value_to_set - self.azimuth_current_pos) <= self.azimuth_tolerance else self.azimuth_tolerance

	# 	BrickPiUpdateValues()
	# 	sensors = [{
	# 		'brickpi' : BrickPiOriginal,
	# 		'port' : PORT_1,
	# 		'update_values_method' : BrickPiUpdateValues
	# 	}]

	# 	self.logger.info("\n===============================================")
	# 	self.logger.info("Azimuth is at " + str(self.azimuth_current_pos))
	# 	self.logger.info("Setting azimuth to " + str(value) + " (that is " + str(value_to_set) + " for BrickPi)")
	# 	self.logger.info("Tollerant difference is " + str(tollerant_difference))
	# 	self.logger.info("")

	# 	while (abs(value_to_set - self.azimuth_current_pos) > tollerant_difference):
	# 		number_of_iterations += 1
	# 		BrickPiUpdateValues()

	# 		self.logger.info("Iteration # " + str(number_of_iterations))
	# 		self.logger.info("------------------------")
	# 		self.logger.info("Azimuth is at: " + str(self.azimuth_current_pos))
	# 		self.logger.info("value_to_set: " + str(value_to_set))
	# 		self.logger.info("Tollerant difference is " + str(tollerant_difference))
			
	# 		if (self.azimuth_current_pos > value_to_set):
	# 			self.logger.info("Current position is higher than desired degree, decreasing it")
				
	# 			rotate_value = (self.azimuth_current_pos - value_to_set) if (number_of_iterations <= 2) else 1/float(number_of_iterations)

	# 			self.logger.info("rotate_value: " + str(rotate_value))
	# 			# ret_value = self.azimuth_motor.rotate(self.azimuth_power, -1 * rotate_value, sensors = sensors)
	# 			ret_value = self.azimuth_motor.rotate(self.azimuth_power, -1 * rotate_value)
	# 			if (ret_value == False):
	# 				break
	# 			self.azimuth_motor.update_position()

	# 			prev_position = self.azimuth_current_pos;
	# 			self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()

	# 			if (self.azimuth_current_pos > prev_position):
	# 				self.logger.info("We went overboard, we've set it at " + str(self.azimuth_current_pos) + " let's reverse")
	# 				# until it becomes again lower
	# 				while self.azimuth_current_pos > 180:
	# 					# ret_value = self.reverse_azimuth(360 - self.azimuth_current_pos + tollerant_difference, sensors)
	# 					ret_value = self.reverse_azimuth(360 - self.azimuth_current_pos + tollerant_difference)
	# 					if (ret_value == False):
	# 						break
	# 					self.logger.info("self.azimuth_current_pos: " + str(self.azimuth_current_pos))
	# 				self.logger.info("We reversed")

	# 				if (abs(self.azimuth_current_pos-value_to_set) <= tollerant_difference):
	# 					value_to_set = self.azimuth_current_pos
	# 					self.logger.info("updating value_to_set to after reversing because it is good enough " + str(self.azimuth_current_pos))

	# 			# self.azimuth = self.azimuth_current_pos - 180

	# 		elif (self.azimuth_current_pos < value_to_set):
	# 			self.logger.info("Current position is lower than desired degree, increasing it")

	# 			rotate_value = (value_to_set - self.azimuth_current_pos) if (number_of_iterations <= 2) else 1/float(number_of_iterations)

	# 			self.logger.info("rotate_value: " + str(rotate_value))
	# 			# ret_value = self.azimuth_motor.rotate(self.azimuth_power, rotate_value, sensors = sensors)
	# 			ret_value = self.azimuth_motor.rotate(self.azimuth_power, rotate_value)
	# 			if (ret_value == False):
	# 				break
	# 			self.azimuth_motor.update_position()

	# 			prev_position = self.azimuth_current_pos;
	# 			self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()

	# 			if (self.azimuth_current_pos < prev_position):
	# 				self.logger.info("We went overboard, we've set it at " + str(self.azimuth_current_pos) + " let's reverse")
	# 				# until it becomes again higher
	# 				while self.azimuth_current_pos < 180:
	# 					# ret_value = self.reverse_azimuth(-1 * (self.azimuth_current_pos + tollerant_difference), sensors)
	# 					ret_value = self.reverse_azimuth(-1 * (self.azimuth_current_pos + tollerant_difference))
	# 					if (ret_value == False):
	# 						break
	# 					self.logger.info("self.azimuth_current_pos: " + str(self.azimuth_current_pos))
	# 				self.logger.info("We reversed")

	# 				if (abs(self.azimuth_current_pos-value_to_set) <= tollerant_difference):
	# 					value_to_set = self.azimuth_current_pos
	# 					self.logger.info("updating value_to_set to after reversing because it is good enough " + str(self.azimuth_current_pos))

	# 			# self.azimuth = self.azimuth_current_pos - 180

	# 		time.sleep(0.1)

	# 	# TODO - set to desired (what we have got as param) or real?
	# 	self.azimuth = value

	# 	self.logger.info("New position: " + str(self.azimuth_current_pos) + ", wanted: "  + str(value_to_set))
	# 	self.logger.info("===============================================\n")
