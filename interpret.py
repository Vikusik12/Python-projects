import sys
import re
import argparse
import xml.etree.ElementTree as ET
#CALL RETURN LABEL JUMP JUMPIFEQ JUMPIFNEQ DPRINT BREAK READ move type? 
keysWord = {
        "MOVE":2,"READ":2,
		"RETURN":0,"CREATEFRAME":0,"PUSHFRAME":0,"POPFRAME":0,
        "DEFVAR":1,"CALL":1,
		"STRI2INT":3,"INT2CHAR":2,
		"ADD":3,"SUB":3,"MUL":3,"IDIV":3,
        "PUSHS":1,"POPS":1,
        "LT":3,"GT":3,"EQ":3,
        "AND":3,"OR":3,"NOT":2,
        "WRITE":1, "CONCAT":3, "STRLEN":2,
        "GETCHAR":3, "SETCHAR":3, "TYPE":2,
        "LABEL":1, "JUMP":1, "JUMPIFEQ":3, "JUMPIFNEQ":3,
        "EXIT":1, "DPRINT":1, "BREAK":0
        }

typesOfopcodes = {
        "MOVE": ['var', ['bool', 'int', 'string', 'nil','var']],
        "CREATEFRAME":[],"PUSHFRAME":[],"POPFRAME":[],
        "DEFVAR":['var'],
        "CALL":['label'],"RETURN":[],
        "PUSHS":[['bool', 'int', 'string', 'nil','var']],"POPS":['var'],
        "ADD":['var', ['int','var'], ['int','var']],"SUB":['var', ['int','var'], ['int','var']],"MUL":['var', ['int','var'], ['int','var']],
		"IDIV":['var', ['int','var'], ['int','var']],
        "LT":['var', ['bool', 'int', 'string', 'nil','var'], ['bool', 'int', 'string', 'nil','var']],
		"GT":['var', ['bool', 'int', 'string', 'nil','var'], ['bool', 'int', 'string', 'nil','var']],
		"EQ":['var', ['bool', 'int', 'string', 'nil','var'], ['bool', 'int', 'string', 'nil','var']],
        "AND":['var', ['bool','var'],['bool','var']],"OR":['var', ['bool','var'],['bool','var']],"NOT":['var',['bool','var']],
        "INT2CHAR":['var',['int','var']],"STRI2INT":['var', ['string','var'],['int','var']],"READ":['var','type'],
        "WRITE":[['bool', 'int', 'string', 'nil','var']], "CONCAT":['var',['string','var'],['string','var']], "STRLEN":['var',['string','var']],
        "GETCHAR":['var',['string','var'],['int','var']], "SETCHAR":['var',['int','var'],['string','var']], "TYPE":['var',['bool', 'int', 'string', 'nil','var']],
        "LABEL":['label'], "JUMP":['label'], "JUMPIFEQ":['label',['bool', 'int', 'string', 'nil','var'],['bool', 'int', 'string', 'nil','var']],
		"JUMPIFNEQ":['label',['bool', 'int', 'string', 'nil','var'],['bool', 'int', 'string', 'nil','var']],
        "EXIT":[['int','var']], "DPRINT":[['bool', 'int', 'string', 'nil','var']], "BREAK":[]
        }

fileSource = ''
wasInputFlag = False
inputFile = ''
def checkArg():
	global fileSource
	global wasInputFlag
	global inputFile
	if len(sys.argv) > 3:
		sys.exit(10)
	# --- Print argument "--help" ---
	if sys.argv[1] == "--help":
		print("The script loads the XML representation of the program and this program")
		print("using input according to command line parameters, it interprets and generates output")
		print("interpret.py --source=file or --input=file")
		sys.exit(0)
	# --- Check arguments ---
	elif len(sys.argv) == 2 and sys.argv[1][:9] == "--source=" :
		try:
			fileSource = open(sys.argv[1][9:], 'r')
			inputFile = sys.stdin
		except:
			exit(11)
	elif len(sys.argv) == 2 and sys.argv[1][:8] == "--input=":
		try:
			wasInputFlag = True
			fileSource = sys.stdin
			inputFile = open(sys.argv[1][8:], 'r')
		except:
			exit(11)
		

	elif len(sys.argv) == 3 and sys.argv[1][:9] == "--source=" and sys.argv[2][:8] == "--input=" :
		try:
			wasInputFlag = True
			inputFile = open(sys.argv[2][8:], 'r')
			fileSource = open(sys.argv[1][9:], 'r')
		except:
			exit(11)
	elif len(sys.argv) == 3 and sys.argv[1][:8] == "--input=" and sys.argv[2][:9] == "--source=" :
		try:
			wasInputFlag = True
			inputFile = open(sys.argv[1][8:], 'r')
			fileSource = open(sys.argv[2][9:], 'r')
		except:
			exit(11)
	else:
		sys.exit("Invalid argument")

# --- The function arranges the function calls in sorted order ---
def sort(parent,attr):
	parent[:] = sorted(parent,key=lambda child: 
int(child.get(attr)))		
	
if __name__ == "__main__":
	checkArg()
	try:
		tree = ET.parse(fileSource)
	except:
		exit(11)
	# Check root node 
	root = tree.getroot()
	if root.tag != 'program' or root.attrib.get('language') != 'IPPcode21':
			exit(31)
	#--Possible name values
	for name, value in root.attrib.items():
		if name == 'name' or name == 'description' or name == 'language':
			continue
		else:
			exit(32)
	#--checking for the correct file format	
	orderKeys = []
	for child in root:
		if child.tag != 'instruction':
			exit(31)
		cattr = list(child.attrib.keys())
		if not ('order' in cattr) or not ('opcode' in cattr):
			exit(32)
		order = child.attrib['order']
		opcode = child.attrib['opcode']
		if opcode.upper() not in keysWord.keys():
			exit(32)
		order = int(order)
		if order in orderKeys or order <= 0:
			exit(32)
		else:
			orderKeys.append(order)
		argKeys = []
		if keysWord[opcode.upper()] != len(child):
			exit(32)
		for argv in child:
			if not(re.match(r"arg[123]",argv.tag)):
				exit(32)
			argIndex = int(argv.tag[3:])
			if argIndex in argKeys:
				exit(32)
			else:
				argKeys.append(argIndex)
			typeAttr = argv.get("type")

	sort(root,'order')
#--Frames		
GF = {} #dict
TF = None
LF = [] #arrays

#--Stacks
DataStack = []
CallStack = []
labels = {}

class Operations:
#--Declaration of labels
	def declareLabel(self,name):
		if name in labels.keys():
			exit(52)
		labels[name] = None
		labels[name] = position
# --- Realizace "jumpu"
	def jumpLabel(self,name):
		if name not in labels.keys():
			exit(52)
		value = labels[name]
		global position
		position = value

	def declareVariable(self, variable):
		variable = variable.split('@', 1) #GF@counter  frame = counter
		name = variable[1]     # name = counter
		frame = variable[0]    # frame = GF
		if (frame == 'GF'):
			# --- Check for duplicity ---
			if name in GF.keys():
				exit(52)
			# - - - Frame identification ---
			GF[name] = None
		elif (frame == 'TF'):
			if TF == None:
				exit(55)
			if name in TF.keys():
				exit(52)
			TF[name] = None
		elif(frame == 'LF'):
			if len(LF) == 0:
				exit(55)
			
			if name in LF[len(LF) - 1].keys():
				exit(52)
			LF[len(LF) - 1][name] = None
			
	def setVariable(self, variable, value):
		variable = variable.split('@', 1)
		name = variable[1]
		frame = variable[0]
		if (frame == 'GF'):
			# ---Check if there is ---
			if name not in GF.keys():
				exit(54)
			# --- Add this value ---
			GF[name] = value
		elif (frame == 'TF'):
			if TF == None:
				exit(55)
			if name not in TF.keys():
				exit(54)
			TF[name] = value

		elif(frame == 'LF'):
			if len(LF) == 0:
				exit(55)
			if name not in LF[len(LF) - 1].keys():
				exit(52)
			LF[len(LF) - 1][name] = value
		
	def getVariable(self, variable):
		variable = variable.split('@', 1)
		name = variable[1]
		frame = variable[0]
		if (frame == 'GF'):
			if name not in GF.keys():
				exit(54)
			# --- Get this value ---
			value = GF[name]
		elif (frame == 'TF'):
			if TF == None:
				exit(55)
			if name not in TF.keys():
				exit(54)
			value = TF[name]
		elif(frame == 'LF'):
			if len(LF) == 0:
				exit(55)
			
			if name not in LF[len(LF) - 1].keys():
				exit(54)
			value = LF[len(LF) - 1][name]
		if value == None:
			exit(56)
		return value

	def isValueCorrespondsToType(self, value, typ):
		# --- Check is value corresponds to type
		if typ == 'var':
			if value[:3] == "LF@" or value[:3] == "GF@" or value[:3] == "TF@":
				return 
			else:
				exit(32)
		elif typ == 'bool':
			if value.lower() == "true" or value.lower() == "false":
				return 
			else:
				exit(32)
		elif typ == 'int':
			if re.match("[-+]?\d+$", value) == None:
				exit(32)
		elif typ == 'string':
			if value == None:
				return
			if '#' in value:
				exit(32)
		elif typ == 'nil':
			if re.match("nil", value) == None:
				exit(32)
		elif typ == 'label':
			if '#' in value:			
				exit(32)
		elif typ == 'type':
			if value != "int" and value != "bool" and value != "string" and value != "nil":
				exit(32)
		
	def getConstTypeAndValue(self, value, typ):
		#--- Correctly stored type and value
		if typ == 'bool':
			if value.lower() == "true":
				return {'type': 'bool', 'value': True}
			elif value.lower() == "false":
				return {'type': 'bool', 'value': False}

		elif typ == 'int':
			return {'type': 'int', 'value': int(value)}
			
		elif typ == 'string':
			if value == None:
				return {'type': 'string', 'value': ''}

			result = ""
			i = 0
			while i < len(value):
				if value[i] == '\\':
					result += chr(int(value[i+1]+value[i+2]+value[i+3]))
					i+=4
				else:
					result += value[i]
					i+=1
			
			return {'type': 'string', 'value': result}
		elif typ == 'nil':
			return {'type': 'nil', 'value': 'nil'}

#--The method puts the arguments in ascending order
	def __init__(self, opcode, args):
		self.args = []
		for arg in args:
			self.args.append(None)
		 
		for arg in args:
			self.isValueCorrespondsToType(arg.text, arg.attrib['type'])
			if arg.tag == 'arg1':
				self.arg1 = {'type': arg.attrib['type'], 'value': arg.text}
				self.args[0] = self.arg1 
			elif arg.tag == 'arg2':
				self.arg2 = {'type': arg.attrib['type'], 'value': arg.text}
				self.args[1] = self.arg2
			elif arg.tag == 'arg3':
				self.arg3 = {'type': arg.attrib['type'], 'value': arg.text}
				self.args[2] = self.arg3
		self.opcode = opcode.upper()
	
	def checkArgsTypes(self):
 	#--- Сorrect type matching
		typesList = typesOfopcodes[self.opcode]
		for i in range(len(typesList)):
			if not self.args[i]['type'] in typesList[i]:
				exit(53)
#---Executing an instruction depending on the opcode
	def doInstruction(self):
		if self.opcode == 'MOVE':
			self._MOVE()
		elif self.opcode == 'DEFVAR':
			self._DEFVAR()
		elif self.opcode == 'CREATEFRAME':
			self._CREATEFRAME()
		elif self.opcode == 'PUSHFRAME':
			self._PUSHFRAME() 
		elif self.opcode == 'POPFRAME':
			self._POPFRAME()
		elif self.opcode == 'WRITE':
			self._WRITE()
		elif self.opcode == "ADD":
			self._ADD()
		elif self.opcode == "SUB":
			self._SUB()
		elif self.opcode == "MUL":
			self._MUL()
		elif self.opcode == "IDIV":
			self._IDIV()
		elif self.opcode == "STRLEN":
			self._STRLEN()
		elif self.opcode == "CONCAT":
			self._CONCAT()
		elif self.opcode == "GETCHAR":
			self._GETCHAR()
		elif self.opcode == "SETCHAR":
			self._SETCHAR()
		elif self.opcode == "TYPE":
			self._TYPE()
		elif self.opcode == "AND":
			self._AND()
		elif self.opcode == "OR":
			self._OR()
		elif self.opcode == "NOT":
			self._NOT()
		elif self.opcode == "LT":
			self._LT()
		elif self.opcode == "GT":
			self._GT()
		elif self.opcode == "EQ":
			self._EQ()
		elif self.opcode == "INT2CHAR":
			self._INT2CHAR()
		elif self.opcode == "STRI2INT":
			self._STRI2INT()
		elif self.opcode == "PUSHS":
			self._PUSHS()
		elif self.opcode == "POPS":
			self._POPS()
		elif self.opcode == "EXIT":
			self._EXIT()
		elif self.opcode == "READ":
			self._READ()
		elif self.opcode == "CALL":
			self._CALL()
		elif self.opcode == "RETURN":
			self._RETURN()
		elif self.opcode == "JUMP":
			self._JUMP()
		elif self.opcode == "LABEL":
			self._LABEL()
		elif self.opcode == "JUMPIFEQ":
			self._JUMPIFEQ()
		elif self.opcode == "JUMPIFNEQ":
			self._JUMPIFNEQ()
		elif self.opcode == "DPRINT":
			self._DPRINT()
		elif self.opcode == "BREAK":
			self._BREAK()

# --- Instruction MOVE ---
	def _MOVE(self):
		value = None
		if self.arg2['type'] == 'var':
			value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])
		self.setVariable(self.arg1['value'], {'type': value['type'], 'value': value['value']})

# --- Instruction DEFVAR ---
	def _DEFVAR(self):
		value = None
		if self.arg1['type'] == 'var':
			self.declareVariable(self.arg1['value'])

# --- Instruction CREATEFRAME ---
	def _CREATEFRAME(self):
		TF = {}

# --- Instruction PUSHFRAME ---
	def _PUSHFRAME(self):
		global TF
		if TF == None:
			exit(55)
		LF.append(TF) # set LF
		TF = None #Reset TF

# --- Instruction POPFRAME ---
	def _POPFRAME(self):
		if len(LF) == 0:
			exit(56)
		TF = LF.pop()

# --- Instruction WRITE ---
	def _WRITE(self):
		value = None
		if self.arg1['type'] == 'var':
			value = self.getVariable(self.arg1['value'])
		else:
			value = self.getConstTypeAndValue(self.arg1['value'], self.arg1['type'])

		if value['type'] == 'bool':
			if value == False:
				value['value'] = "false"
			else:
				value['value'] = "true"
		value['value'] = str(value['value'])
		print(value['value'], end='')
# --- Instruction ADD ---
	def _ADD(self):
		value = None
		nevalue = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != 'int' or nevalue['type'] != 'int':
			exit(53)

		result = value['value'] + nevalue['value']
		self.setVariable(self.arg1['value'], {'type': 'int', 'value': result})
# --- Instruction SUB ---
	def _SUB(self):
		value = None
		nevalue = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != 'int' or nevalue['type']!= 'int':
			exit(53)

		result = value['value'] - nevalue['value']
		self.setVariable(self.arg1['value'], {'type': 'int', 'value': result})
# --- Instruction MUL ---
	def _MUL(self):
		value = None
		nevalue = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != 'int' or nevalue['type'] != 'int':
			exit(53)

		result = value['value'] * nevalue['value']
		self.setVariable(self.arg1['value'], {'type': 'int', 'value': result})
# --- Instruction IDIV ---
	def _IDIV(self):
		value = None
		nevalue = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != 'int' or nevalue['type'] != 'int':
			exit(53)

		if nevalue['value'] == 0:
			exit(57)

		result = value['value'] / nevalue['value']
		self.setVariable(self.arg1['value'], {'type': 'int', 'value': result})
# --- Instruction STRLEN ---
	def _STRLEN(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if (value['type'] != 'string'):
			exit(53)
		result = len(value['value'])

		self.setVariable(self.arg1['value'], {'type': 'int', 'value': result})
# --- Instruction CONCAT ---
	def _CONCAT(self):
		value = None
		nevalue = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])
		
		if value['type'] != 'string' or nevalue['type'] != 'string':
			exit(53)
		result = value['value'] + nevalue['value']
		self.setVariable(self.arg1['value'], {'type': 'string', 'value': result})
# --- Instruction GETCHAR ---
	def _GETCHAR(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != 'string' or nevalue['type'] != 'int':
			exit(53)

		ret = len(value['value']) - 1

		if nevalue['value'] > ret or nevalue['value'] < 0:
			exit(58)
		result = value['value'][nevalue['value']]
		self.setVariable(self.arg1['value'], {'type': 'string', 'value': result})
# --- Instruction SETCHAR ---
	def _SETCHAR(self):
		value = None
		nevalue = None
		firstVar = self.getVariable(self.arg1['value'])
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != 'int' or nevalue['type'] != 'string' or firstVar['type'] != 'string':
			exit(53)

		ret = len(firstVar['value']) - 1
		if value['value'] > ret or value['value'] < 0:
			exit(58)
		if len(nevalue['value']) == 0:
			exit(58)
		if len(nevalue['value']) > 1:
			nevalue = nevalue['value'][0]
			#pa p ousek 2 r
			#pa r ousek
		result = firstVar['value'][:value['value']] + nevalue['value']+ firstVar['value'][value['value']+1:]
		self.setVariable(self.arg1['value'], {'type': 'string', 'value': result})
# --- Instruction AND ---
	def _AND(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != 'bool' or nevalue['type'] != 'bool':
			exit(53)

		result = (value['value'] and nevalue['value'])
		self.setVariable(self.arg1['value'], {'type': 'bool', 'value': result})
# --- Instruction OR ---
	def _OR(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != 'bool' or nevalue['type'] != 'bool':
			exit(53)
			
		result = (value['value'] or nevalue['value'])
		self.setVariable(self.arg1['value'], {'type': 'bool', 'value': result})
# --- Instruction NOT ---
	def _NOT(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if value['type'] != 'bool':
			exit(53)
			
		result = not value['value']
		self.setVariable(self.arg1['value'], {'type': 'bool', 'value': result})
# --- Instruction LT ---
	def _LT(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])
		
		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != nevalue['type']:
			exit(53)
		if value['type'] == 'nil' or nevalue['type'] == 'nil':
			exit(53)
		result = value['value'] < nevalue['value']
		self.setVariable(self.arg1['value'], {'type': 'bool', 'value': result})
# --- Instruction GT ---
	def _GT(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])
		
		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != nevalue['type']:
			exit(53)
		if value['type'] == 'nil' or nevalue['type'] == 'nil':
			exit(53)		
		result = value['value'] > nevalue['value']
		self.setVariable(self.arg1['value'], {'type': 'bool', 'value': result})
# --- Instruction EQ ---
	def _EQ(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])
		
		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])

		if value['type'] != nevalue['type']:
			exit(53)
		result = value['value'] == nevalue['value']
		self.setVariable(self.arg1['value'], {'type': 'bool', 'value': result})	
# --- Instruction INT2CHAR ---
	def _INT2CHAR(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if value['type'] != 'int':
			exit(53)
		try:
			char = chr(value['value'])
		except:
			exit(58)
		self.setVariable(self.arg1['value'], {'type': 'string', 'value': char})
# --- Instruction STR2INT ---
	def _STRI2INT(self):
		value = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
			nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])
		if value['type'] != 'string' or nevalue['type'] != 'int':
			exit(53)
		ret = len(value['value']) - 1
		if nevalue['value'] > ret or nevalue['value'] < 0:
			exit(58)
		try:
			ordin = ord(value['value'][nevalue['value']])
		except:
			exit(58)
		self.setVariable(self.arg1['value'], {'type': 'int', 'value': ordin})
# --- Instruction READ ---
	def _READ(self):
		if wasInputFlag:
			value = inputFile.readline()
		else:
			try:
				value = input()
			except:
				value = ''

		typ = self.arg2['value']

		if value == None:
			if typ == 'string':
				value = {'type': 'string', 'value': ''}
			else:
				value = {'type': 'nil', 'value': 'nil'}
		else:
			if typ == 'bool':
				if value.lower() == "true":
					value = {'type': 'bool', 'value': True}
				elif value.lower() == "false":
					value = {'type': 'bool', 'value': False} 
				else:
		   			value = {'type': 'nil', 'value': 'nil'}
			elif typ == 'int':
				if re.match("[-+]?\d+$", value) == None:
					value = {'type': 'nil', 'value': 'nil'}
				else:
					value = {'type': 'int', 'value': int(value)}
			elif typ == 'string':
				if value == None:
					value = {'type': 'string', 'value': ''}
				elif '#' in value:
					value = {'type': 'nil', 'value': 'nil'}
				else:
					value = {'type': 'string', 'value': value}
			elif typ == 'nil':
				value = {'type': 'nil', 'value': 'nil'}

		self.setVariable(self.arg1['value'], value)

# --- Instruction PUSHS ---
	def _PUSHS(self):
		value = None
		if self.arg1['type'] == 'var':
	 		value = self.getVariable(self.arg1['value'])
		else:
			value = self.getConstTypeAndValue(self.arg1['value'], self.arg1['type'])
		DataStack.append(value)
# --- Instruction POPS ---
	def _POPS(self):
		if len(DataStack) == 0:
			exit(56)
		self.setVariable(self.arg1['value'], DataStack.pop())
# --- Instruction EXIT ---
	def _EXIT(self):
		value = None
		if self.arg1['type'] == 'var':
	 		value = self.getVariable(self.arg1['value'])
		else:
			value = self.getConstTypeAndValue(self.arg1['value'], self.arg1['type'])
		if value['type'] != 'int':
			exit(53)
		exit(value['value'])
# --- Instruction TYPE ---
	def _TYPE(self):
		if self.arg2['type'] == 'var':
			value = self.arg2['value'] 
			variable = self.arg2['value'].split('@', 1)
			name = variable[1]
			frame = variable[0]
			if (frame == 'GF'):
				if name not in GF.keys():
					value = None
				else:
					value = GF[name]
			elif (frame == 'TF'):
				if TF == None or name not in TF.keys():
					value = None
				else:
					value = TF[name]
			elif(frame == 'LF'):
				if len(LF) == 0 or name not in LF[len(LF) - 1].keys():
					value = None
				else:
					value = LF[len(LF) - 1][name]
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])
		if value == None:
			self.setVariable(self.arg1['value'], {'type':'string', 'value':''})  			
		elif value['type'] == 'string' or value['type'] == 'int' or value['type'] == 'bool' or value['type'] == 'nil':
			self.setVariable(self.arg1['value'], {'type': 'string', 'value': value['type']})

# --- Instruction LABEL ---
	def _LABEL(self):
		if self.arg1['type'] == 'label':
			self.declareLabel(self.arg1['value'])
# --- Instruction JUMP ---
	def _JUMP(self):
		if self.arg1['type'] == 'label':
			self.jumpLabel(self.arg1['value'])	
# --- Instruction JUMPIFEQ ---
	def _JUMPIFEQ(self):
		value = None
		nevalue = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])
		if value['type'] != nevalue['type'] and (value['type'] !='nil' and nevalue['type'] != 'nil'):
			exit(53)

		jumpeq = value['value'] == nevalue['value']
		if self.arg1['type'] == 'label' and jumpeq:
			self.jumpLabel(self.arg1['value'])
# --- Instruction JUMPIFNEQ ---
	def _JUMPIFNEQ(self):
		value = None
		nevalue = None
		if self.arg2['type'] == 'var':
	 		value = self.getVariable(self.arg2['value'])
		else:
			value = self.getConstTypeAndValue(self.arg2['value'], self.arg2['type'])

		if self.arg3['type'] == 'var':
	 		nevalue = self.getVariable(self.arg3['value'])
		else:
			nevalue = self.getConstTypeAndValue(self.arg3['value'], self.arg3['type'])
		if value['type'] != nevalue['type'] and (value['type'] !='nil' and nevalue['type'] != 'nil'):
			exit(53)

		jumpeq = value['value'] != nevalue['value']
		if self.arg1['type'] == 'label' and jumpeq:
			self.jumpLabel(self.arg1['value'])
# --- Instruction CALL ---
	def _CALL(self):
		if self.arg1['type'] == 'label':
			CallStack.append(position + 1)
		self.jumpLabel(self.arg1['value'])
# --- Instruction RETURN ---
	def _RETURN(self):
		if len(CallStack) == 0:
			exit(56)
		global position
		position = CallStack.pop()
		
# --- Instruction DPRINT ---
	def _DPRINT(self):
		sys.stderr.write(self.arg1['value'])
# --- Instruction BREAK ---
	def _BREAK(self):
		number = int(child.attrib['order']) - 1
		number = str(number)
		sys.stderr.write( "Number of instructions executed is " + number)
#--loop about writing a "LABELS" to dictionary labels		
position = 0
while position < len(root):
	child = root[position]

	if child.attrib['opcode'].upper() == 'LABEL':
		instruction = Operations(child.attrib['opcode'], child)
		instruction.checkArgsTypes()
		instruction.doInstruction()
	position += 1

#--main loop reading XML code
position = 0
while position < len(root):
	child = root[position]
	if child.attrib['opcode'].upper() != 'LABEL':
		instruction = Operations(child.attrib['opcode'], child)
		instruction.checkArgsTypes()
		instruction.doInstruction()
	position += 1