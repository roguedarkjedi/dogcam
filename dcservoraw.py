from dcservo import DogCamServoBase
import RPi.GPIO as GPIO
import time

class DogCamServoRaw(DogCamServoBase):
  __Start=0.0
  __Pulse=0.0
  __Hardware=None
  
  def __init__(self, InName, InPin, InStart, InPulseBound, ZeroAngle=0, Steps=0.0, LowerBounds=0.0, UpperBounds=180.0):
    self.__Start = InStart
    self.__Pulse = InPulseBound
    GPIO.setup(InPin, GPIO.OUT)
    self.__Hardware = GPIO.PWM(InPin, 50)
    self.__Hardware.start(self.__Start)
    
    super().__init__(InName, InPin, InZeroAngle=ZeroAngle, InSteps=Steps, InLowerBounds=LowerBounds, InUpperBounds=UpperBounds)

  def __del__(self):
    self.__Hardware.stop()
    
  @staticmethod
  def InitGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
  @staticmethod
  def CleanupGPIO():
    GPIO.cleanup()
  
  # Moves to exact position, sets no values
  def _MoveToPosition(self, angle):
    print(f"{self.Name}: Moving to position {angle}")
    dutyCycle = angle / self.__Pulse + self.__Start
    self.__Hardware.ChangeDutyCycle(dutyCycle)
    
    # Give hardware time to move
    time.sleep(0.2)

    # Do not repeat the duty cycle commands, flush them
    self.__Hardware.ChangeDutyCycle(0)
