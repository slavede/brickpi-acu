# brickpi-acu
Flask REST API for controlling antenna attached to Mindstorm LEGO motor

Since LEGO Mindstorm motor has issues with rotating for particular degree (http://www.dexterindustries.com/topic/accuracy-of-rotating-a-motor/) I used modified BrickPi.py library from https://github.com/dwalton76/LegoDigitalClock.

Still, it had some issue with precision so I tweaked acu class to toggle until it's inside acceptable error (defaults to 5 degrees).
