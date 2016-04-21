import RPi.GPIO as GPIO
from flask import Flask
from time import sleep

GPIO.setmode(GPIO.BOARD)

app = Flask(__name__)

# Open motor
openMotorA = 16
openMotorB = 18
openMotorC = 22

# Close motor
closeMotorA = 23
closeMotorB = 21
closeMotorC = 19

# Setup motors
GPIO.setup(openMotorA, GPIO.OUT)
GPIO.setup(openMotorB, GPIO.OUT)
GPIO.setup(openMotorC, GPIO.OUT)

GPIO.setup(closeMotorA, GPIO.OUT)
GPIO.setup(closeMotorB, GPIO.OUT)
GPIO.setup(closeMotorC, GPIO.OUT)

@app.route("/open")
def open():
	print "opening"
	# Pull down on the open motor
	#GPIO.output(openMotorA, GPIO.HIGH)
	#GPIO.output(openMotorB, GPIO.LOW)
	#GPIO.output(openMotorC, GPIO.HIGH)

	# Unwind the close motor so the sting 
	# doesn't get caught on the wheel
	#GPIO.output(openMotorA, GPIO.LOW)
	#GPIO.output(openMotorB, GPIO.HIGH)
	#GPIO.output(openMotorC, GPIO.HIGH)

	# Set a default to only pull down
	# a maximum of 10 seconds
	#sleep(10)
	#stop()

@app.route("/close")
def close():
	# Pull down on the open motor
	GPIO.output(closeMotorA, GPIO.HIGH)
	GPIO.output(closeMotorB, GPIO.LOW)
	GPIO.output(closeMotorC, GPIO.HIGH)

	# Unwind the close motor so the sting 
	# doesn't get caught on the wheel
	GPIO.output(closeMotorA, GPIO.LOW)
	GPIO.output(closeMotorB, GPIO.HIGH)
	GPIO.output(closeMotorC, GPIO.HIGH)

	# Set a default to only pull down
	# a maximum of 10 seconds
	sleep(10)
	stop()

@app.route("/stop")
def stop():
	# Shut off both motors
	GPIO.output(closeMotorC, GPIO.LOW)
	GPIO.output(openMotorC, GPIO.LOW)

	GPIO.cleanup

if __name__ == "__main__":
	app.run()
