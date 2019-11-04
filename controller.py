from config import *
import RPi.GPIO as GPIO
import threading
import time

class DogCamServo():
	Name=""
	Pin=0
	CurrentAngle=0
	_Hardware=None
	
	def __init__(self, InName, GPIOPin):
		self.Name = InName.lower()
		self.Pin = GPIOPin
		GPIO.setup(GPIOPin, GPIO.OUT)
		self._Hardware = GPIO.PWM(GPIOPin, 50)
		self._Hardware.start(DogCamConfig.StartPulse)
		
	def __eq__(self, Other):
		if instanceof(Other, str):
			return self.Name == Other.lower()
		else:
			return super().__eq__(Other)
			
	def __del__(self):
		self._Hardware.stop()

class DogCamController():
	Servos = {}
	
	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		
		self.Servos.update("pan", DogCamServo("pan", DogCamConfig.pan))
		self.Servos.update("tilt", DogCamServo("tilt", DogCamConfig.tilt))
		
	def __del__(self):
		self.Servos = {}		
		GPIO.cleanup()


# TODO: Write movement from the tester
# TODO: Program step movement
# TODO: Make this work asyncly?
# TODO: fuuuuuuuuuuuuuuuck
