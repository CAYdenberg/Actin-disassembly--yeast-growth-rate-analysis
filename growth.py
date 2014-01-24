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
    self.rates = {'25C': None, '30C': None, '34C': None, '37C': None}
    #error estimates at the four temperatues
    self.errors = {'25C': None, '30C': None, '34C': None, '37C': None}
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
  def queryTemp(self, Temp):
    ReturnData = []
    for datapoint in self.rawData:
      if datapoint.temp == Temp:
        ReturnData.append(datapoint.data)
    return ReturnData
  def getAverage(self, Temp):
    ReleventData = self.queryTemp(Temp)
    Sum = 0.0
    N = 0
    for Datum in ReleventData:
      Sum += Datum
      N += 1
    self.rates[Temp] = Sum/N
    return Sum/N  

class Datapoint(object):
  def __init__(self, Expt, Data):
    self.expt = Expt
    self.data = Data
    Result = Pattern.search(Expt)
    if Result:
      Temp = Result.group(1)
      self.temp = Temp + 'C'
    else:
      self.temp = None    

class Interaction(object):  
  def __init__(self, BaseStrain, ComparisonStrain):
    global Temps
    self.outputText = ''
    self.color = '#666'
    if BaseStrain and ComparisonStrain:
      self.base = BaseStrain
      self.comparison = ComparisonStrain
      Temp = 0
      BreakTempFound = False
      for Temp in Temps:
        MutEffect = self.comparison.rates[Temp] / self.base.rates[Temp]
        if MutEffect < 0.5:
          break
      self.outputText = str(Temp) + ' ~ ' + str( MutEffect )
      if Temp == '37C' and MutEffect > 0.5:
        self.color = '#006600'
      elif Temp == '37C':
        self.color = '#CCCC00'
      elif Temp == '34C':
        self.color = '#FFFF00'
      elif Temp == '30C':
        self.color = '#FF9900'
      elif Temp == '25C':
        self.color = '#FF6600'
    else:
      self.outputText = 'ND'
      self.color = 'Black'

def GetStrain(Genotype):
  global Strains
  for StrainNum in Strains:
    if Strains[StrainNum].genotype == Genotype:
      return Strains[StrainNum]
  return False
    

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
import copy
Pattern = re.compile(r'\-\s(\d+)C\.txt')
Temps = ['25C', '30C', '34C', '37C']

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
InFile.close()

OutFile = open('growth_rates_parsed.txt', 'w')
for StrainNum in Strains:
  OutFile.write(StrainNum + '\t')
  OutFile.write(Strains[StrainNum].genotype + '\n')
  for Temp in Temps:
    Data = Strains[StrainNum].queryTemp(Temp)
    OutFile.write('\t' + Temp + '\t')
    for Datum in Data:
      OutFile.write(str(Datum) + '\t')
    Average = Strains[StrainNum].getAverage(Temp)
    OutFile.write(str(Average) + '\n')

Cols = ['aip1', 'cap2', 'crn1', 'gmf1', 'srv2', 'twf1']
Genotypes = ['WT']
for x in range(0, 6):
  Genotypes.append(Cols[x])
for x in range(0, 6):
  for y in range(x+1, 6):
    Genotypes.append(Cols[x] + ' ' + Cols[y])
for x in range(0, 6):
  for y in range(x+1, 6):
    for z in range(y+1, 6):
      Genotypes.append(Cols[x] + ' ' + Cols[y] + ' ' + Cols[z])

OutFile.write('SUMMARY\n')
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

for BaseGenotype in Genotypes:
  BaseStrain = GetStrain(BaseGenotype)
  if not BaseStrain:
    continue  
  OutFile.write(BaseGenotype + '\t')
  WriteText(SvgFile, BaseGenotype, SvgX, SvgY)
  SvgX += 50    
  for Col in Cols:
    if Col in BaseStrain.mutations:
      OutFile.write('\t')
      WriteBox(SvgFile, 'Black', SvgX, SvgY)
    else:
      CompositeMutations = copy.copy(BaseStrain.mutations)
      CompositeMutations.append(Col)
      CompositeMutations.sort()
      ComparisonGenotype = ' '.join(CompositeMutations)
      ComparisonStrain = GetStrain(ComparisonGenotype)
      #Note that ComparisonStrain can be False. Interaction can handle this.
      CurrentCell = Interaction(BaseStrain, ComparisonStrain)
      OutFile.write(CurrentCell.outputText + '\t')
      WriteBox(SvgFile, CurrentCell.color, SvgX, SvgY)
    SvgX += 50
  OutFile.write('\n')
  SvgY += 50
  SvgX = 0
  
OutFile.close()  
SvgFile.write('</svg>')
SvgFile.close()     