import RPi.GPIO as GPIO
import asyncio
import time
import json

__all__ = ("DogCamController")

class DogCamServo:
  Name=""
  Pin=0
  ShouldLoop=False
  __CurrentAngle=0.0
  __TargetAngle=0.0
  __Start=0.0
  __Pulse=0.0
  __ServoDelta=0.0
  __ZeroAngle=0
  __Steps=0.0
  __LowerBounds=0.0
  __UpperBounds=180.0
  __Hardware=None
  
  def __init__(self, InName, GPIOPin, InStart, InPulseBound, ZeroAngle=0, Steps=0.0, LowerBounds=0.0, UpperBounds=0.0):
    self.Name = InName.lower()
    self.Pin = GPIOPin
    self.__Start = InStart
    self.__Pulse = InPulseBound
    GPIO.setup(GPIOPin, GPIO.OUT)
    self.__Hardware = GPIO.PWM(GPIOPin, 50)
    self.__Hardware.start(self.__Start)
    self.__ZeroAngle = ZeroAngle
    self.__Steps=Steps
    self.__LowerBounds = LowerBounds
    self.__UpperBounds = UpperBounds

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
    self.__SetBothAngles(self.__ZeroAngle)
    
    self.__MoveToPosition(self.__ZeroAngle)
    time.sleep(1)
    self.__MoveToPosition(self.__ZeroAngle)
    print(f"{self.Name}: reset")
    
  def GetCurrentAngle(self):
    return self.__CurrentAngle
    
  def __SetBothAngles(self, angle):
    self.__TargetAngle = angle
    self.__CurrentAngle = angle
    
  def __SetTargetAngle(self, angle):
    if angle < self.__LowerBounds:
      angle = self.__LowerBounds
    elif angle > self.__UpperBounds:
      angle = self.__UpperBounds
      
    self.__TargetAngle = angle
    
    self.__ServoDelta = abs(self.__CurrentAngle - angle) / self.__Steps

  def MoveToAbsoluteAngle(self, angle):
    if angle == self.__ZeroAngle:
      self.Reset()
    else:
      self.__MoveToPosition(angle)
      self.__SetBothAngles(angle)
      
  def MoveToInterpAngle(self, angle):
    if angle == self.__ZeroAngle:
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
          Movement = self.__CurrentAngle - self.__ServoDelta
          WillOverShot = Movement <= self.__TargetAngle
        else:
          Movement = self.__CurrentAngle + self.__ServoDelta
          WillOverShot = Movement >= self.__TargetAngle
        
        print(f"{self.Name}: moving {Movement} to {self.__TargetAngle}")
        
        if WillOverShot or self.__TargetAngle < self.__LowerBounds or self.__TargetAngle > self.__UpperBounds:
          print(f"{self.Name}: We there")
          self.__ServoDelta = 0.0
          self.__MoveToPosition(self.__TargetAngle)
          self.__SetBothAngles(self.__TargetAngle)
        else:
          await self.__InterpPosition(Movement)

        continue

      await asyncio.sleep(0.4)

class DogCamController:
  __Servos = {}
  __RelAngle = 0.0
  Instance = None
  
  def __init__(self):
    if DogCamController.Instance is None:
      DogCamController.Instance = self
    else:
      self = DogCamController.Instance
      return
      
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    self.__ReadConfig()
    print("DogCam Ready")
    
  def __del__(self):
    print("Shutting down robot")
    self.ResetAllServos()
    self.StopServoLoops()
    self.__Servos = {}  
    GPIO.cleanup()

  def __ReadConfig(self):
    with open("./config.json","r") as cfg_file:
      ConfigBlob = json.load(cfg_file)
      
      self.__RelAngle = ConfigBlob["DefaultRelativeAngle"]
      for item in ConfigBlob["Servos"]:
        if not "name" in item or not "pin" in item or not "start" in item:
          raise KeyError("Missing required configuration!")

        Name = item["name"]
        ZeroLoc = 0.0
        Step = ConfigBlob["DefaultStep"]
        LowBound = 0.0
        HighBound = ConfigBlob["DefaultHigh"]

        if "zero" in item:
          ZeroLoc = item["zero"]
        if "step" in item:
          Step = item["step"]
        if "low" in item:
          LowBound = item["low"]
        if "high" in item:
          HighBound = item["high"]

        self.__Servos[Name] = DogCamServo(Name, item["pin"], item["start"], 
          item["pulse"], ZeroAngle=ZeroLoc, Steps=Step, LowerBounds=LowBound,
          UpperBounds=HighBound)
        print(f"Imported servo: {Name}")

      print("Config imported!")

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
  
  def MoveServoLeft(self):
    self.MoveServoTo("pan", RelativeAngle=-self.__RelAngle)
  def MoveServoRight(self):
    self.MoveServoTo("pan", RelativeAngle=self.__RelAngle)
  def MoveServoUp(self):
    self.MoveServoTo("tilt", RelativeAngle=-self.__RelAngle)
  def MoveServoDown(self):
    self.MoveServoTo("tilt", RelativeAngle=self.__RelAngle)
    
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
