import RPi.GPIO as GPIO
import asyncio
import time
import pytweening

__all__ = ("DogCamController")

class DogCamServo:
  Name=""
  Pin=0
  ShouldLoop=False
  __CurrentAngle=0.0
  __TargetAngle=0.0
  # Servos have odd stepping differences, adjust here
  __StepsUp=0.0
  __StepsDown=0.0
  __Start=0.0
  __Pulse=0.0
  __Hardware=None
  
  def __init__(self, InName, GPIOPin, InStart, InPulseBound, InStepsUp, InStepsDown):
    self.Name = InName.lower()
    self.Pin = GPIOPin
    self.__Start = InStart
    self.__Pulse = InPulseBound
    GPIO.setup(GPIOPin, GPIO.OUT)
    self.__StepsUp = InStepsUp
    self.__StepsDown = InStepsDown
    self.__Hardware = GPIO.PWM(GPIOPin, 50)
    self.__Hardware.start(self.__Start)
    
    self.Reset()
    
    print(f"{self.Name}: ready for motion")
    
    self.ShouldLoop = True
    asyncio.get_event_loop().create_task(self.__ServoLoop())
      
  def __del__(self):
    print(f"{self.Name}: Shutting off hardware")
    self.ShouldLoop = False
    self.Reset()
    self.__Hardware.stop()
    
  def Reset(self):
    self.__SetBothAngles(0)
    
    self.__MoveToPosition(0)
    time.sleep(1)
    self.__MoveToPosition(0)
    print(f"{self.Name}: reset")
    
  def GetCurrentAngle(self):
    return self.__CurrentAngle
    
  def __SetBothAngles(self, angle):
    self.__TargetAngle = angle
    self.__CurrentAngle = angle
    
  def __SetTargetAngle(self, angle):
    if angle < 0.0:
      angle = 0.0
    elif angle > 180.0:
      angle = 180.0
    
    self.__TargetAngle = angle

  def MoveToAbsoluteAngle(self, angle):
    if angle == 0.0:
      self.Reset()
    else:
      self.__MoveToPosition(angle)
      self.__SetBothAngles(angle)
      
  def MoveToInterpAngle(self, angle):
    if angle == 0.0:
      self.Reset()
    else:
      self.__SetTargetAngle(angle)
      print(f"{self.Name}: Moving location to {angle}")
  
  def MoveToRelativeAngle(self, angle):
    self.__SetTargetAngle(self.__CurrentAngle + angle)
    print(f"{self.Name}: Setting relative location to {self.__TargetAngle}")
    
  async def __InterpPosition(self, angle):
    self.__CurrentAngle = angle
    self.__MoveToPosition(self.__CurrentAngle)
  
  # Moves to exact position, sets no values
  def __MoveToPosition(self, angle):
    print(f"{self.Name}: Moving to position {angle}")
    dutyCycle = angle / self.__Pulse + self.__Start
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
          Movement = pytweening.easeInQuad(abs(self.__TargetAngle / AdjustedLoc))
          Movement = Movement*-self.__TargetAngle+AdjustedLoc-self.__StepsDown
          WillOverShot = Movement <= self.__TargetAngle
        else:
          Movement = pytweening.easeInQuad(abs(AdjustedLoc / self.__TargetAngle))
          Movement = Movement*self.__TargetAngle+AdjustedLoc+self.__StepsUp
          WillOverShot = Movement >= self.__TargetAngle
        
        print(f"{self.Name}: moving {Movement} to {self.__TargetAngle}")
        
        if WillOverShot or self.__TargetAngle < 0.0 or self.__TargetAngle > 180.0:
          print(f"{self.Name}: We there")
          self.__MoveToPosition(self.__TargetAngle)
          self.__SetBothAngles(self.__TargetAngle)
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
    # InName, GPIOPin, InStart, InPulseBound, InStepsUp, InStepsDown
    self.__Servos = {
    "pan": DogCamServo("pan", 27, 2.2, 18.0, 1.5, 2.0), 
    "tilt": DogCamServo("tilt", 17, 4.5, 18.0, 2.15, 4.0)}
    
    print("Controllers are ready")
    
  def __del__(self):
    print("Shutting down robot")
    self.ResetAllServos()
    self.StopServoLoops()
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
        TheServo.MoveToInterpAngle(InterpAngle)
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
    for servo in self.__Servos.values():
      servo.Reset()

  def StopServoLoops(self):
    for servo in self.__Servos.values():
      servo.ShouldLoop = False
      
  def GetCurrentAngle(self, ServoName:str):
    if ServoName.lower() in self.__Servos:
      return self.__Servos[ServoName.lower()].GetCurrentAngle()
    else:
      return 0.0
