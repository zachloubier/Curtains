import json
import os.path

class Config:
	config_file_name = 'config.json'

	def set(key, value):
		config = self.get()

		config[key] = value
		
		with open(self.config_file_name, 'w') as outfile:
			json.dump(config, outfile)

	def get(key = None):
		config = {}
		if os.path.exists(self.config_file_name):
			with open(self.config_file_name, 'r') as outfile:
				config = json.load(outfile)

		if key is None:
			val = config
		else:
			try:
				val = config[key]
			except KeyError:
				val = config

		return val

	def calibrate():
		interval_qty = 5
		interval_length = 5

		config = {
			"state": 0,
			"interval_qty": interval_qty,
			"interval_length": interval_length

		}