#!/usr/bin/env python

from BrickPi import BrickPi, PORT_A, PORT_B, time

from BrickPiOriginal import BrickPiOriginal, PORT_1, PORT_2, PORT_3, PORT_4, TYPE_SENSOR_TOUCH, BrickPiSetup, BrickPiSetupSensors, BrickPiUpdateValues, ser

import logging

class MyLogger():
	def info(self, message):
		print message

class Acu():
	def __init__(self, azimuth_power = 30, elevation_power=30, elevation_tollerance=5, azimuth_tolerance = 5, logger = None):
		self.mypi = BrickPi(ser = ser)
		
		self.azimuth_motor = self.mypi.motors[PORT_A]
		self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()
		self.azimuth = self.azimuth_current_pos - 180
		self.azimuth_power = azimuth_power

		self.elevation_motor = self.mypi.motors[PORT_B]
		self.elevation_current_pos = self.elevation_motor.get_position_in_degrees()
		self.elevation = self.elevation_current_pos
		self.elevation_power = elevation_power

		self.elevation_tollerance = elevation_tollerance
		self.azimuth_tolerance = azimuth_tolerance

		BrickPiOriginal.SensorType[PORT_1] = TYPE_SENSOR_TOUCH
		BrickPiOriginal.SensorType[PORT_2] = TYPE_SENSOR_TOUCH
		BrickPiSetupSensors()

		if (logger is None):
			self.logger = MyLogger()
		else :
			self.logger = logger;

		self.logger.info('Initial azimuth position: %d' % (self.azimuth_current_pos))
		self.logger.info('Initial elevation position: %d' % (self.elevation_current_pos))
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
		return self.azimuth

	def get_brick_pi_azimuth(self):
		return self.azimuth_current_pos

	def get_elevation(self):
		return self.elevation

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

	def set_elevation(self, value):

		if (value < 0):
			value = 0

		if (value > 90):
			value = 90

		number_of_iterations = 0
		tollerant_difference = abs(value - self.elevation_current_pos)/2 if abs(value - self.elevation_current_pos) <= self.elevation_tollerance else self.elevation_tollerance

		self.logger.info("\n===============================================")
		self.logger.info("Elevation is at " + str(self.elevation_current_pos))
		self.logger.info("Setting elevation to " + str(value))
		self.logger.info("Tollerant difference is " + str(tollerant_difference))
		self.logger.info("")

		while (abs(value - self.elevation_current_pos) > tollerant_difference):
			number_of_iterations += 1
			self.logger.info("Iteration # " + str(number_of_iterations))
			self.logger.info("------------------------")
			self.logger.info("Elevation is at: " + str(self.elevation_current_pos))
			self.logger.info("value: " + str(value))
			self.logger.info("Tollerant difference is " + str(tollerant_difference))

			if (self.elevation_current_pos > value):
				self.logger.info("Current position is higher than desired degree, decreasing it")
				
				rotate_value = (self.elevation_current_pos - value) if (number_of_iterations <= 2) else 1/float(number_of_iterations)

				self.logger.info("rotate_value: " + str(rotate_value))
				self.elevation_motor.rotate(self.elevation_power, -1 * rotate_value)
				self.elevation_motor.update_position()

				prev_position = self.elevation_current_pos;
				self.elevation_current_pos = self.elevation_motor.get_position_in_degrees()

				if (self.elevation_current_pos > 180 and prev_position < 180):
					self.logger.info("We went overboard, we've set it at " + str(self.elevation_current_pos) + " let's reverse")
					# until it becomes again lower
					while self.elevation_current_pos > 180:
						self.reverse_elevation(360 - self.elevation_current_pos + tollerant_difference)
						self.logger.info("self.elevation_current_pos: " + str(self.elevation_current_pos))
					self.logger.info("We reversed")

					if (abs(self.elevation_current_pos-value) <= tollerant_difference):
						value = self.elevation_current_pos
						self.logger.info("updating value to after reversing because it is good enough " + str(self.elevation_current_pos))


			elif (self.elevation_current_pos < value):
				self.logger.info("Current position is lower than desired degree, increasing it")

				rotate_value = (value - self.elevation_current_pos) if (number_of_iterations <= 2) else 1/float(number_of_iterations)

				self.logger.info("rotate_value: " + str(rotate_value))
				self.elevation_motor.rotate(self.elevation_power, rotate_value)
				self.elevation_motor.update_position()

				prev_position = self.elevation_current_pos;
				self.elevation_current_pos = self.elevation_motor.get_position_in_degrees()

				# we can't go overboard (modulo) when top is 90 degrees
				# no need to check that here

			time.sleep(0.1)

		self.elevation = value

		self.logger.info("New position: " + str(self.elevation_current_pos) + ", wanted: "  + str(value))
		self.logger.info("===============================================\n")


	def set_azimuth(self, value):
		if (value >= 180):
			value = 179

		if (value <= -180):
			value = -179

		value_to_set = value + 180

		number_of_iterations = 0
		tollerant_difference = abs(value_to_set - self.azimuth_current_pos)/2 if abs(value_to_set - self.azimuth_current_pos) <= self.azimuth_tolerance else self.azimuth_tolerance

		BrickPiUpdateValues()
		sensors = [{
			'brickpi' : BrickPiOriginal,
			'port' : PORT_1,
			'update_values_method' : BrickPiUpdateValues
		}]

		self.logger.info("\n===============================================")
		self.logger.info("Azimuth is at " + str(self.azimuth_current_pos))
		self.logger.info("Setting azimuth to " + str(value) + " (that is " + str(value_to_set) + " for BrickPi)")
		self.logger.info("Tollerant difference is " + str(tollerant_difference))
		self.logger.info("")

		while (abs(value_to_set - self.azimuth_current_pos) > tollerant_difference):
			number_of_iterations += 1
			BrickPiUpdateValues()

			self.logger.info("Iteration # " + str(number_of_iterations))
			self.logger.info("------------------------")
			self.logger.info("Azimuth is at: " + str(self.azimuth_current_pos))
			self.logger.info("value_to_set: " + str(value_to_set))
			self.logger.info("Tollerant difference is " + str(tollerant_difference))
			
			if (self.azimuth_current_pos > value_to_set):
				self.logger.info("Current position is higher than desired degree, decreasing it")
				
				rotate_value = (self.azimuth_current_pos - value_to_set) if (number_of_iterations <= 2) else 1/float(number_of_iterations)

				self.logger.info("rotate_value: " + str(rotate_value))
				# ret_value = self.azimuth_motor.rotate(self.azimuth_power, -1 * rotate_value, sensors = sensors)
				ret_value = self.azimuth_motor.rotate(self.azimuth_power, -1 * rotate_value)
				if (ret_value == False):
					break
				self.azimuth_motor.update_position()

				prev_position = self.azimuth_current_pos;
				self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()

				if (self.azimuth_current_pos > prev_position):
					self.logger.info("We went overboard, we've set it at " + str(self.azimuth_current_pos) + " let's reverse")
					# until it becomes again lower
					while self.azimuth_current_pos > 180:
						# ret_value = self.reverse_azimuth(360 - self.azimuth_current_pos + tollerant_difference, sensors)
						ret_value = self.reverse_azimuth(360 - self.azimuth_current_pos + tollerant_difference)
						if (ret_value == False):
							break
						self.logger.info("self.azimuth_current_pos: " + str(self.azimuth_current_pos))
					self.logger.info("We reversed")

					if (abs(self.azimuth_current_pos-value_to_set) <= tollerant_difference):
						value_to_set = self.azimuth_current_pos
						self.logger.info("updating value_to_set to after reversing because it is good enough " + str(self.azimuth_current_pos))

				# self.azimuth = self.azimuth_current_pos - 180

			elif (self.azimuth_current_pos < value_to_set):
				self.logger.info("Current position is lower than desired degree, increasing it")

				rotate_value = (value_to_set - self.azimuth_current_pos) if (number_of_iterations <= 2) else 1/float(number_of_iterations)

				self.logger.info("rotate_value: " + str(rotate_value))
				# ret_value = self.azimuth_motor.rotate(self.azimuth_power, rotate_value, sensors = sensors)
				ret_value = self.azimuth_motor.rotate(self.azimuth_power, rotate_value)
				if (ret_value == False):
					break
				self.azimuth_motor.update_position()

				prev_position = self.azimuth_current_pos;
				self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()

				if (self.azimuth_current_pos < prev_position):
					self.logger.info("We went overboard, we've set it at " + str(self.azimuth_current_pos) + " let's reverse")
					# until it becomes again higher
					while self.azimuth_current_pos < 180:
						# ret_value = self.reverse_azimuth(-1 * (self.azimuth_current_pos + tollerant_difference), sensors)
						ret_value = self.reverse_azimuth(-1 * (self.azimuth_current_pos + tollerant_difference))
						if (ret_value == False):
							break
						self.logger.info("self.azimuth_current_pos: " + str(self.azimuth_current_pos))
					self.logger.info("We reversed")

					if (abs(self.azimuth_current_pos-value_to_set) <= tollerant_difference):
						value_to_set = self.azimuth_current_pos
						self.logger.info("updating value_to_set to after reversing because it is good enough " + str(self.azimuth_current_pos))

				# self.azimuth = self.azimuth_current_pos - 180

			time.sleep(0.1)

		# TODO - set to desired (what we have got as param) or real?
		self.azimuth = value

		self.logger.info("New position: " + str(self.azimuth_current_pos) + ", wanted: "  + str(value_to_set))
		self.logger.info("===============================================\n")