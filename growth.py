#read all the data into a library indexed by strain number

#extract the genotype into a series of boolean values and the total number of mutations

#create a 2-dimensional array for output

#find 0 < n < 3 mutations, alphabetically ordered, find each mutant + 1,
#enter values into the 2-di array

class Strain(object):
  def __init__(self, StrainNum, RawGenotype):
    self.mutations = []
    self.genotype = ''
    #list of objects containing Datapoint objects
    self.rawData = []
    #average rates at the four temperatures only
    self.rates = []
    #error estimates at the four temperatues
    self.errors = []
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
  def addData(self, Expt, Data):
    self.rawData.append(Datapoint(Expt, Data))

class Datapoint(object):
  def __init__(self, Expt, Data):
    self.expt = Expt
    self.data = Data
    Result = Pattern.search(Expt)
    if Result:
      Temp = Result.group(1)
      self.temp = Temp
    else:
      self.temp = None    

class Interaction(object):  
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
import re
Pattern = re.compile(r'\-\s(\d+)C\.txt')

Strains = {}

LookupFile = open('strain_names.txt', 'r')
for Line in LookupFile:
  Line = Line.rstrip()
  ColList = Line.split('\t')
  StrainNum = ColList[1]
  if StrainNum not in Strains:
    Strains[StrainNum] = Strain(StrainNum, ColList[0])
LookupFile.close()

InFile = open('growth_rates.txt', 'r')
for Line in InFile:
  Line = Line.rstrip()
  ColList = Line.split('\t')
  StrainNum = ColList[5]
  Strains[StrainNum].addData(ColList[0], float(ColList[2]))

print Strains
  
'''
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
'''
     