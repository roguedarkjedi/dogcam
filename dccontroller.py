from dcservoraw import DogCamServoRaw
import json

class DogCamController():
  __Servos = {}
  __RelAngle = 0.0
  AIDisabled = False
  Instance = None
  
  def __init__(self):
    if DogCamController.Instance is None:
      DogCamController.Instance = self
    else:
      self = DogCamController.Instance
      return
      
    DogCamServo.InitGPIO()
    self.__ReadConfig()
    print("DogCam Ready")
    
  def __del__(self):
    print("Shutting down robot")
    self.ResetAllServos()
    self.StopServoLoops()
    self.__Servos = {}  
    DogCamServo.CleanupGPIO()

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
