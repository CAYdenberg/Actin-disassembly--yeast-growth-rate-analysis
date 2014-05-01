#this script extracts growth curves from a Tecan plate reader and creates 
#list of doubling time. Raw data to be analyzed should be placed in the "raw"
#directory. A single text file listing filenames, column headings,
#calculated doubling time, and R2 (confidence) will be
#created in response.

#Note that the Tecan can create files in a variety of formats. This script
#is built for tab-separated text files in which each column represents a single
#well.

#The doubling time is calculated between OD 0.200 and 0.500. 

#from arrays of x and y values, calculate linear regression statistics
#m - the slope
#b - the y-intercept
#r2 - the R-squared (goodness of fit)
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

#calculates the growth rate (1/the doubling time) for the range of values
#between OD 0.200 and 0.500
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
  global digits #regex to find digits, necessary to extract time values
  
  InFile = open(InFileName, 'r')
  Times = []
  ODs = {} #dict of data for each column
  ColNames = [] #list of column names
  
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
  #print out the information for each well to a new line
  for ColName in ColNames:
    if ColName:
      GrowthRate = GetGrowthRate(Times, ODs[ColName])
      if GrowthRate:
        OutString = InFileName + '\t' + ColName + '\t' + GrowthRate
        OutFile.write(OutString + '\n')
        print OutString

#main script
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