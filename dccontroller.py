import RPi.GPIO as GPIO
import asyncio
import time
import pytweening

__all__ = ("DogCamController")

class DogCamServo:
  Name=""
  Pin=0
  __CurrentAngle=0.0
  __TargetAngle=0.0
  Start=0.0
  Pulse=0.0
  ShouldLoop=False
  __Hardware=None
  
  def __init__(self, InName, GPIOPin, InStart, InPulseBound):
    self.Name = InName.lower()
    self.Pin = GPIOPin
    self.Start = InStart
    self.Pulse = InPulseBound
    GPIO.setup(GPIOPin, GPIO.OUT)
    self.__Hardware = GPIO.PWM(GPIOPin, 50)
    self.__Hardware.start(self.Start)
    
    self.Reset()
    
    print(f"{self.Name} ready for motion")
    
    self.ShouldLoop = True
    asyncio.get_event_loop().create_task(self.__ServoLoop())
    
  def __eq__(self, Other):
    if instanceof(Other, str):
      return self.Name == Other.lower()
    else:
      return super().__eq__(Other)
      
  def __del__(self):
    print(f"Shutting off {self.Name} hardware")
    self.ShouldLoop = False
    self.Reset()
    self.__Hardware.stop()
    
  def Reset(self):
    self.__CurrentAngle = 0
    self.__TargetAngle = self.__CurrentAngle
    
    self.__MoveToPosition(0)
    time.sleep(1)
    self.__MoveToPosition(0)
    print(f"{self.Name} reset")

  def MoveToAbsoluteAngle(self, angle):
    if angle == 0.0:
      self.Reset()
    else:
      self.__MoveToPosition(angle)
      self.__CurrentAngle = angle
      self.__TargetAngle = angle
      
  def MoveToInterpAngle(self, angle):
    if angle == 0.0:
      self.Reset()
    else:
      self.__TargetAngle = angle
      print(f"Setting location to {angle}")
  
  def MoveToRelativeAngle(self, angle):
    self.__TargetAngle = self.__CurrentAngle + angle
    print(f"Setting relative location to {self.__TargetAngle}")
    
  async def __InterpPosition(self, angle):
    self.__CurrentAngle = angle
    self.__MoveToPosition(self.__CurrentAngle)
  
  # Moves to exact position, sets no values
  def __MoveToPosition(self, angle):
    print(f"Moving to position {angle}")
    dutyCycle = angle / self.Pulse + self.Start
    self.__Hardware.ChangeDutyCycle(dutyCycle)
    
    # Give hardware time to move
    time.sleep(0.2)
    
    # Do not repeat the duty cycle commands, flush them
    self.__Hardware.ChangeDutyCycle(0)
    
  async def __ServoLoop(self):
    while self.ShouldLoop is True:
      # We need to move
      if self.__TargetAngle != self.__CurrentAngle:
        AdjustedLoc = self.__CurrentAngle
        if AdjustedLoc == 0.0:
          AdjustedLoc = 1.0
          
        # Determine where we should go
        if self.__CurrentAngle > self.__TargetAngle:
          Movement = pytweening.easeInQuad(self.__TargetAngle / AdjustedLoc)
          Movement = Movement*-self.__TargetAngle+AdjustedLoc-2.0
          WillOverShot = Movement <= self.__TargetAngle
        else:
          Movement = pytweening.easeInQuad(AdjustedLoc / self.__TargetAngle)
          Movement = Movement*self.__TargetAngle+AdjustedLoc+2.0
          WillOverShot = Movement >= self.__TargetAngle
        
        print(f"Servo {self.Name} moving {Movement} to {self.__TargetAngle}")
        
        if WillOverShot:
          print("We there")
          self.__MoveToPosition(self.__TargetAngle)
          self.__CurrentAngle = self.__TargetAngle
        else:
          await self.__InterpPosition(Movement)

        continue
        
      await asyncio.sleep(0.1)
    

class DogCamController:
  __Servos = {}
  Instance = None
  
  def __init__(self):
    if DogCamController.Instance is None:
      DogCamController.Instance = self
    else:
      self = DogCamController.Instance
      return
      
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    self.__Servos = {"pan": DogCamServo("pan", 27, 3.45, 18.0), 
    "tilt": DogCamServo("tilt", 17, 4.5, 18.0)}
    
    print("Controllers are ready")
    
  def __del__(self):
    print("Shutting down robot")
    self.ResetAllServos()
    self.__Servos = {}  
    GPIO.cleanup()

  def MoveServoTo(self, ServoName:str, RelativeAngle=0.0, InterpAngle=0.0, AbsoluteAngle=0.0):
    if ServoName.lower() in self.__Servos:
      TheServo = self.__Servos[ServoName.lower()]
      if RelativeAngle != 0.0:
        TheServo.MoveToRelativeAngle(RelativeAngle)
        TheAngle = RelativeAngle
      elif AbsoluteAngle != 0.0:
        TheServo.MoveToAbsoluteAngle(AbsoluteAngle)
        TheAngle = AbsoluteAngle
      elif InterpAngle != 0.0:
        TheServo.MoveToInterpAngle(AbsoluteAngle)
        TheAngle = InterpAngle
      else:
        TheAngle = 0.0
        TheServo.Reset()
      print(f"Moving {ServoName} to {TheAngle}")
    else:
      print(f"Servo {ServoName.lower()} is not a valid servo!")
      
  def ResetServo(self, ServoName:str):
    if ServoName.lower() in self.__Servos:
      self.__Servos[ServoName.lower()].Reset()
    else:
      print(f"Servo {ServoName.lower()} does not exist!")
      
  def ResetAllServos(self):
    for name,servo in self.__Servos:
      servo.Reset()
