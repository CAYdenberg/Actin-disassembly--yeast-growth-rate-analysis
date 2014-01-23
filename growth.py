#read all the data into a library indexed by strain number

#extract the genotype into a series of boolean values and the total number of mutations

#create a 2-dimensional array for output

#find 0 < n < 3 mutations, alphabetically ordered, find each mutant + 1,
#enter values into the 2-di array

class Strain(object):
  genotype = ''
  growth = []
  error = []
  numMut = 1
  mutations = []
  strainNum = ''
  def __init__(self, RawGenotype, Growth, Error, StrainNum):
    self.growth = Growth
    self.error = Error
    self.mutations = []
    self.genotype = ''
    GenotypesList = RawGenotype.split('?')
    self.numMut = len(GenotypesList) - 1
    self.strainNum = StrainNum
    for Gene in GenotypesList:
      if Gene == 'WT':
        continue
      elif Gene == 'gmf':
        self.mutations.append('gmf1')
      elif Gene != '':
        self.mutations.append(Gene)
    self.mutations.sort()
    if len(self.mutations) == 0:
      self.genotype = 'WT'
    else:
      self.genotype = ' '.join(self.mutations)

class Interaction(object):
  base = object
  comparison = object
  outputText = ''
  color = '#666'  
  def __init__(self, BaseStrain, ComparisonStrain):
    self.outputText = ''
    self.color = '#666'
    if BaseStrain and ComparisonStrain:
      self.base = BaseStrain
      self.comparison = ComparisonStrain
      Temp = 0
      BreakTempFound = False
      while Temp < 4 and BreakTempFound == False:
        MutEffect = self.comparison.growth[Temp] / self.base.growth[Temp]
        if MutEffect < 0.5:
          BreakTempFound = True
        else:
          Temp += 1
      self.outputText = str(Temp) + ' ~ ' + str( MutEffect )
      if Temp == 4:
        self.color = '#006600'
      elif Temp == 3:
        self.color = '#CCCC00'
      elif Temp == 2:
        self.color = '#FFFF00'
      elif Temp == 1:
        self.color = '#FF9900'
      elif Temp == 0:
        self.color = '#FF6600'
    else:
      self.outputText = 'ND'
      self.color = 'Black'

#write text in an SVG file      
def WriteText(File, Text, XPos, YPos):
  File.write('<text x = "' + str(XPos) + '" y = "' + str(YPos) + '">' + Text + '</text>\n')
  print Text

#create rectangles (boxes) in an SVG file
def WriteBox(File, Color, XPos, YPos):
  SvgFile.write('<rect x = "' + str(SvgX) + '" y = "' + str(SvgY) + 
  '" width = "50" height = "50" style = "fill:' + Color + '" />')  


#main script         
Strains = {}

from copy import *

InFile = open('master_data.txt', 'r')
LineNum = 0
for Line in InFile:
  DataList = Line.split(',')
  StrainNum = DataList[1]
  Genotype = DataList[0]
  x = 2
  Growth = []
  Error = []
  while x < 10:
    CurrentGrowth = float( DataList[x] ) + float( DataList[x+1] ) / 2
    CurrentError = abs( float( DataList[x] ) - CurrentGrowth )
    Growth.append(CurrentGrowth)
    Error.append(CurrentError)
    x += 2
  NewStrain = Strain(Genotype, Growth, Error, StrainNum)
  Strains[NewStrain.genotype] = NewStrain
  LineNum += 1

Cols = ['aip1', 'cap2', 'crn1', 'gmf1', 'srv2', 'twf1']
Lines = ['WT']
for x in range(0, 6):
  Lines.append(Cols[x])
for x in range(0, 6):
  for y in range(x+1, 6):
    Lines.append(Cols[x] + ' ' + Cols[y])
for x in range(0, 6):
  for y in range(x+1, 6):
    for z in range(y+1, 6):
      Lines.append(Cols[x] + ' ' + Cols[y] + ' ' + Cols[z])

OutFile = open('growth_rates_parsed.txt', 'w')
SvgFile = open('growth_rate_heatmap.svg', 'w')

SvgX = 100
SvgY = 50

OutFile.write('\t')
SvgFile.write('<?xml version="1.0" ?><svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">')

for Col in Cols:
  OutFile.write(Col + '\t')
  WriteText(SvgFile, Col, SvgX, SvgY)
  SvgX += 50
OutFile.write('\n')

SvgY += 50
SvgX = 0

for Line in Lines:
  try:
    BaseStrain = Strains[Line]
    OutFile.write(BaseStrain.genotype + '\t')
    WriteText(SvgFile, BaseStrain.genotype, SvgX, SvgY)
  except:
    continue
  SvgX += 50    
  for Col in Cols:
    if Col in BaseStrain.mutations:
      OutFile.write('\t')
      WriteBox(SvgFile, 'Black', SvgX, SvgY)
    else:
      CompositeMutations = copy(BaseStrain.mutations)
      CompositeMutations.append(Col)
      CompositeMutations.sort()
      SearchStr = ' '.join(CompositeMutations)
      try:
        ComparisonStrain = Strains[SearchStr]
        CurrentCell = Interaction(BaseStrain, ComparisonStrain)
      except:
        CurrentCell = Interaction(False, False)
      OutFile.write(CurrentCell.outputText + '\t')
      WriteBox(SvgFile, CurrentCell.color, SvgX, SvgY)
    SvgX += 50
  OutFile.write('\n')
  SvgY += 50
  SvgX = 0
  
OutFile.close()  
SvgFile.write('</svg>')
SvgFile.close()     