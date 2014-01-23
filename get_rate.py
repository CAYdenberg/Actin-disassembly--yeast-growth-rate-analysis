#returns a list of numbers smoothed by averaging a sliding
#window of data points. 
#Input - an initial set of floats
#WindowSize - size of the sliding window to be averaged.
#WindowSize should be an odd number (5, 7, 9)
#So that the input and output lists are the same length,
#values of "None" are inserted at the beginning and at
#the end
#this function requires the math module
def Smooth(Input, WindowSize):
  OffsetSize = int(math.floor(WindowSize / 2))
  Smoothed = [None] * OffsetSize
  for x in range(OffsetSize, len(Input) - OffsetSize):
    Window = Input[x - OffsetSize : x + OffsetSize + 1]
    WindowSum = math.fsum(Window)
    WindowValue = WindowSum / KernelSize
    Smoothed.append(WindowValue)
  for x in range(len(Input) - OffsetSize, len(Input)):
    Smoothed.append(None)
  return Smoothed

#returns the numerical derivative of a list of numbers
#obtained by subtraction of each datapoint from the one
#previous.
#So that the input and output lists are the same length,
#the first item will have a value of None.
#Any datapoints that initially have a value of None
#will also have a value of None
def NumericDerive(Input):
  Derivs = [None]
  for x in range(1, len(Input)):
    try:
      Diff = Input[x] - Input[x - 1]
    except:
      Diff = None
    Derivs.append(Diff)
  return Derivs      


class RegressionLine:
  def __init__(self, xVals, yVals):
    if len(xVals) != len(yVals):
      raise exception('X and Y values must have the same length!')
    sumX = 0.0
    sumY = 0.0
    sumXY = 0.0
    sumXX = 0.0 
    sumYY = 0.0
    for n in range(0, len(xVals)):
      X = xVals[n]
      Y = yVals[n]
      sumX = sumX + X
      sumY = sumY + Y
      sumXY = sumXY + X * Y
      sumXX = sumXX + X * X
      sumYY = sumYY + Y * Y
    self.m = (len(xVals) * sumXY - sumX * sumY) / (len(xVals) * sumXX - sumX * sumX)
    self.b = (sumY - self.m * sumX) / len(xVals)
    self.r2 = math.pow((len(xVals) * sumXY - sumX * sumY)/math.sqrt((len(xVals) *
     sumXX - sumX * sumX) * (len(xVals) * sumYY - sumY * sumY)), 2)

def GetGrowthRate(Times, ODs):
  Logs = []
  StartRange = 0
  StopRange = 0
  x = 0
  #calc log2 values and find the logarithmic part of the curve
  for OD in ODs:
    Logs.append(math.log(OD, 2))
    if OD > 0.200 and not StartRange:
      StartRange = x
    elif OD > 0.500 and not StopRange:
      StopRange = x
    x += 1
  #fallback assigns StopRange to the last datapoint
  if not StopRange:
    StopRange = x - 1
  if not StartRange:
    return False
  else:
    Initial = RegressionLine(Times[StartRange:StopRange], Logs[StartRange:StopRange])
    return str(Initial.m) + '\t' + str(Initial.r2)  


def ParseFile(InFileName):
  global digits
  
  InFile = open(InFileName, 'r')
  Times = []
  ODs = {}
  ColNames = []
  
  #read in raw data
  LineNum = 0
  for Line in InFile:
    ColList = Line.split('\t')
    if LineNum == 0:
      for Col in ColList:
        if Col and Col != '':
          ColNames.append(Col)
          ODs[Col] = []
        else:
          ColNames.append(None)
    else:    
      ColNum = 0
      for Col in ColList:
        if ColNum == 0:
          #get the time and convert to minutes
          try:
            Result = digits.match(Col)
            Time = float(Result.group(1)) / 60.0
            Times.append(Time)
          except:
            break
        #note that break will cause any row missing a time
        #to skip ALL the data. The exception is row 0, which
        #is handled separately.
        else:
          try:
            OD = float(Col)
          except:
            ColNum += 1
            continue
          ColName = ColNames[ColNum]
          ODs[ColName].append(OD)  
        ColNum += 1
    LineNum += 1

  for ColName in ColNames:
    if ColName:
      GrowthRate = GetGrowthRate(Times, ODs[ColName])
      if GrowthRate:
        OutString = InFileName + '\t' + ColName + '\t' + GrowthRate
        OutFile.write(OutString + '\n')
        print OutString

import os      
import math
import re

OutFile = open('growth_rates.txt', 'w')

digits = re.compile(r'(\d+)')

Dir = 'raw/'
Files = os.listdir(Dir)

for File in Files:
  if os.path.isfile(Dir + File):
    ParseFile(Dir + File)

    



  

 