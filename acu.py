#!/usr/bin/env python

from BrickPi import *

class Acu():
	def __init__(self, azimuth_power = 30, azimuth_rotate_degree = 0.025, elevation_power = 30, elevation_rotate_degree = 0.25):
		self.mypi = BrickPi()

		self.azimuth_motor = self.mypi.motors[PORT_A]
		self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()
		self.azimuth = self.azimuth_current_pos - 180
		self.azimuth_power = azimuth_power
		self.azimuth_rotate_degree = azimuth_rotate_degree

		print "Initial azimuth position: " + str(self.azimuth_current_pos)
	
	def get_azimuth(self):
		return self.azimuth


	def get_brick_pi_azimuth(self):
		return self.azimuth_current_pos

	def set_azimuth(self, value):
		if (value > 180):
			value = 180

		if (value < -180):
			value = -180

		value_to_set = value + 180

		print "Setting azimuth to " + str(value) + " (that is " + str(value_to_set) + " for BrickPi)";

		if (self.azimuth_current_pos > value_to_set):
			print "Current position is higher than desired degree, decreasing it\n"
			while self.azimuth_current_pos > value_to_set:
				self.azimuth_motor.rotate(self.azimuth_power, -1 * self.azimuth_rotate_degree)
				self.azimuth_motor.update_position()

				self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()
				self.azimuth = self.azimuth_current_pos - 180

				print "Current position: " + str(self.azimuth_current_pos)

		elif (self.azimuth_current_pos < value_to_set):
			print "Current position is lower than desired degree, increasing it\n"
			while self.azimuth_current_pos < value_to_set:
				self.azimuth_motor.rotate(self.azimuth_power, self.azimuth_rotate_degree)
				self.azimuth_motor.update_position()

				self.azimuth_current_pos = self.azimuth_motor.get_position_in_degrees()
				self.azimuth = self.azimuth_current_pos - 180

				print "Current position: " + str(self.azimuth_current_pos)

		# TODO - set to desired (what we have got as param) or real?
		self.azimuth = value

		print "New position: " + str(self.azimuth_current_pos)