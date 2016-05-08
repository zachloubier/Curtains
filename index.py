env = 'prod'

if env != 'dev':
	import RPi.GPIO as GPIO

from flask import Flask, render_template, request
from time import sleep
from sys import argv
import time, json, os.path, urlparse

#import config
# Define Config Class
class Config:
	config_file_name = 'config.json'

	defaults = {
		"state": 0,
		"state_closed": 0,
		"interval_qty": 5
	}

	# Set a config value
	def set(self, key, value=None):
		config = self.get()
		orig_config = self.get()

		# If key is a dictionary, loop over all items to update
		if isinstance(key, dict):
			for k, v in key.iteritems():
				config[k] = v
		elif value != None:
			# Don't update if value is not provided
			config[key] = value

		# Only update file if we've actually made changes
		if orig_config != config:
			# Attempt to sort..
			new_config = {}
			for k in sorted(config):
				new_config[k] = config[k]

			with open(self.config_file_name, 'w') as outfile:
				json.dump(new_config, outfile)

	# Get a config value
	def get(self, key = None):
		config = {}
		if os.path.exists(self.config_file_name):
			with open(self.config_file_name, 'r') as outfile:
				try:
					config = json.load(outfile)
				except ValueError:
					config = {}

		# If no key provided, return the whole config object
		if key is None:
			val = config
		else:
			try:
				val = config[key]
			except KeyError:
				# If the key provided was invalid, return the whole config object
				val = config

		return val

	def reset(self):
		self.set(self.defaults)

Config = Config()

#import curtains
# Define Curtains Class
class Curtains:
	# Open motor
	open_motor_a = 16
	open_motor_b = 18
	open_motor_c = 22

	# Close motor
	close_motor_a = 22
	close_motor_b = 23
	close_motor_c = 19

	def __init__(self):
		if env != 'dev':
			GPIO.setmode(GPIO.BCM)

			# Setup motors
			GPIO.setup(self.open_motor_a, GPIO.OUT)
			GPIO.setup(self.open_motor_b, GPIO.OUT)
			#GPIO.setup(self.open_motor_c, GPIO.OUT)

			GPIO.setup(self.close_motor_a, GPIO.OUT)
			GPIO.setup(self.close_motor_b, GPIO.OUT)
			#GPIO.setup(self.close_motor_c, GPIO.OUT)
	
	def _open(self):
		print "opening"
		if env != 'dev':
			# Pull down on the open motor
			GPIO.output(self.open_motor_a, True)
			GPIO.output(self.open_motor_b, False)
			#GPIO.output(self.open_motor_c, GPIO.HIGH)

			# Unwind the close motor so the sting
			# doesn't get caught on the wheel
			GPIO.output(self.close_motor_a, False)
			GPIO.output(self.close_motor_b, True)
			#GPIO.output(self.close_motor_c, GPIO.HIGH)

	def _close(self):
		print "closing"
		if env != 'dev':
			# Pull down on the close motor
			GPIO.output(self.close_motor_a, True)
			GPIO.output(self.close_motor_b, False)
			#GPIO.output(self.close_motor_c, GPIO.HIGH)

			# Unwind the open motor so the sting
			# doesn't get caught on the wheel
			GPIO.output(self.open_motor_a, False)
			GPIO.output(self.open_motor_b, True)
			#GPIO.output(self.open_motor_c, GPIO.HIGH)

	def move(self, to_state=0):
		current_state = Config.get('state')

		to_state = int(to_state)
		
		print 'Current State: ' + str(current_state)
		print 'To State: ' + str(to_state)
		print 'Interval Qty: ' + str(Config.get('interval_qty'))
		print 'State Closed: ' + str(Config.get('state_closed'))
		if to_state < Config.get('interval_qty') and to_state >= Config.get('state_closed'):
			diff = current_state - to_state
			
			print 'Diff: ' + str(diff)
			
			# Only continue if there is a difference
			if diff != 0:
				if diff < 0:
					self._open()
				elif diff > 0:
					self._close()

				# Set a default to only pull down
				# a maximum of <interval_length> seconds
				interval_length = Config.get('interval_length')

				sleep_time = interval_length * abs(diff)
				
				sleep(sleep_time)
				
				self.stop()

				current_state = to_state

			Config.set('state', current_state)

		return current_state

	def stop(self):
		if env != 'dev':
			# Shut off both motors
			GPIO.output(self.close_motor_a, False)
			GPIO.output(self.close_motor_b, False)
			#GPIO.output(self.close_motor_c, False)

			GPIO.output(self.open_motor_a, False)
			GPIO.output(self.open_motor_b, False)
			#GPIO.output(self.open_motor_c, False)

			GPIO.cleanup

	def start_calibration(self, interval_qty=None):
		# Reset the config values
		Config.reset()

		if interval_qty is not None:
			Config.set('interval_qty', int(interval_qty))

		# Record the start time
		Config.set('calibrate_start_time', time.time())

		# Start closing the curtains
		self._close()

		return Config.get('state')

	def stop_calibration(self):
		# Stop the curtains from closing
		stop_time = time.time()
		self.stop()

		if Config.get('calibrate_start_time'):
			# Record the stop time
			Config.set('calibrate_stop_time', stop_time)

			# Calculate the distance and interval quantity
			total_time = stop_time - Config.get('calibrate_start_time')
			interval_qty = Config.get('interval_qty')
			interval_length = total_time / interval_qty

			Config.set('interval_length', interval_length)

			# Now re-open the curtains
			self.move(Config.get('interval_qty') - 1)

	def get_status(self):
		return json.dumps({"state": Config.get('state'), "intervals": Config.get('interval_qty')})

Curtains = Curtains()

#Curtains.move(1)

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/move", methods=['PUT'])
def move_curtains():
	if request.method == 'PUT':
		to_state = request.args.get('to_state')
		
		Curtains.move(to_state)

	return Curtains.get_status()

@app.route("/calibrate/start", methods=['PUT'])
def start_calibration():
	if request.method == 'PUT':
		new_interval_qty = request.args.get('interval_qty')

		Curtains.start_calibration(new_interval_qty)

	return Curtains.get_status()

@app.route("/calibrate/stop", methods=['PUT'])
def stop_calibration():
	if request.method == 'PUT':
		Curtains.stop_calibration()

	return Curtains.get_status()

@app.route("/state")
def get_state():
	return Curtains.get_status()

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)
