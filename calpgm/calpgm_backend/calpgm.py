#import calexcept
import datetime
import math
import subprocess
import os.path

import numpy as np 
import pandas as pn
import time
import struct
import fileinput

class InitializeError(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return rept(self.value)

class ExecuteError(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return rept(self.value)

class IdiotCheck(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return rept(self.value)



class calpgm(object):

	# All available parameters for SPCAT

	__PARAMS_RIGID = {'A':10000,'B':20000,'C':30000}
	__PARAMS_DISTORT_A = {'DelJ': 200,'DelJK':1100,'DelK':2000,'delJ':40100,'delK':41000}
	__PARAMS_DISTORT_S = {'DJ': 200, 'DJK':2000,'DK':2000,'d1':40100,'d2':50000}

	__HEX_DISTORT_A = {'PhiJ': 300,'PhiJK':1200,'PhiKJ':2100,'PhiK':3000,'phiJ':40200,'phiJK':41100,'phiK':42000}
	__HEX_DISTORT_S = {'HJ': 300, 'HJK': 1200,'HKJ': 2100,'HK':3000,'h1':40200,'h2':50100,'h3':60000}

	__OCT_DISTORT_A = {'LJ': 400, 'LJJK': 1330, 'LJK': 2200, 'LKKJ': 3100, 'LK': 4000, 'lJ': 40300, 'lJK': 41200, 'lKJ': 42100, 'lK': 43000} 
	__OCT_DISTORT_S = {'LJ': 400, 'LJJK': 1330, 'LJK': 2200, 'LKKJ': 3100, 'LK': 4000, 'l1': 40300, 'l2': 50200, 'l3': 60100, 'l4': 70000}

	__QUAD = {'1_5Xaa': 110010000, '1_5Xbb': 110020000, '1_5Xcc': 110030000, 'Xab': 110610000, 'Xbc': 110210000, 'Xac': 110410000, '0_25Xb-c':110040000}
	
	ALL_PARAMS = dict(__PARAMS_RIGID.items() + __PARAMS_DISTORT_S.items() + __PARAMS_DISTORT_A.items() + __HEX_DISTORT_A.items() + __HEX_DISTORT_S.items() + __OCT_DISTORT_A.items() + __OCT_DISTORT_S.items() + __QUAD.items()) 



	# PARAMETERS
	name = "molecule"
	filename = "default"
	max_freq = 20.0
	dipoles = [1.0,1.0,1.0]
	temp = 2
	spin = 0
	reduction = 'a'
	J_min = 0
	J_max = 20
	inten = -10.0
	temp = 2.0


	# Containers for rotational constants, etc
	initial_vals = []
	initial_vals_rigid = [0.0,0.0,0.0]
	current_vals = []
	current_vals_rigid = [0.0,0.0,0.0]

	def spincalc(self,input_spin):
		if input_spin == math.floor(float(input_spin)):
			input_spin = int(2*float(input_spin)+1)
		else:
			input_spin = 2*int(math.ceil(float(input_spin)))

		return input_spin

	def read(self, data):
		if self.current_vals:
			self.current_vals = []
		for i in range(0, len(data)):
			self.current_vals.append([])
			self.current_vals[i].append(data[i][0])
			self.current_vals[i].append(data[i][1])

			if data[i][0] == 'A':
				self.current_vals_rigid[0] = float(data[i][1])
			if data[i][0] == 'B':
				self.current_vals_rigid[1] = float(data[i][1])
			if data[i][0] == 'C':
				self.current_vals_rigid[2] = float(data[i][1])

		if not self.initial_vals:
			self.initial_vals = self.current_vals
			self.initial_vals_rigid = self.current_vals_rigid

	def from_file(self, input_file):
		data = open(input_file, 'r')
		output = []
		for i, line in enumerate(data):
			output.append([])
			output[i].append(line.split()[0])
			output[i].append(line.split()[1])
		#print output
		return output


	def add_params(self,new_dict):
		self.ALL_PARAMS = dict(ALL_PARAMS.items()+new_dict.items())

	def get_params(self):
		return self.current_vals

	def get_init_params(self):
		return self.initial_vals

	def error_message(errortype, message,severity=0):
		print '\n\n=========== '+ str(errortype)+ 'ERROR AT: '+datetime.datetime.now().strftime("%a %b %d %I:%M:%S %Y")+'==========='
		print ""
		print 'You screwed up! This is why:'
		print '-----------------'
		print str(message)
		print '-----------------'
		if severity == 0:
			print 'Continue with caution!\n\n'
		if severity == 1:
			print 'Honestly you shouldn\'t have even gotten here! Shame on you!'
		if severity == 2:
			print 'This probably breaks your routine. Check your code!!!'

	# List of kwargs relevant for calpgm (so far)
	# - data: input parameters (list of lists)
	# - name: molecule name (default: "molecule")
	# - max_freq: max frequency for predictions (default: 20 GHz)
	# - dipoles: [ua,ub,uc] in floats
	# - temp : temperature in Kelvin (default 2.0)
	# - spin : nuclear spin (e.g. 1 for nitrogen 14-containing molecules, 1.5 for chlorine, default 0)
	# - reduction: 'a' or 's' (specifies which watson reduction to use, default 'a')
	# - J_min/J_max : min/max J for predictions (0/20 default)
	# - inten: intensity cutoff (log strength, default -10.0)
	def __init__(self,**kwargs):
		print 'CALPGM constructor initialized\n'
		self.spin = self.spincalc(self.spin)
		try:
			for key, value in kwargs.iteritems():

				if key == 'data':
					if isinstance(value,basestring):
						self.read(self.from_file(value))
					else:
						self.read(value)

				elif key == 'filename':
					if isinstance(value,basestring):
						filename = value

				elif key == 'max_freq':
					max_freq = float(value)

				elif key == 'dipoles':
					dipoles = value

				elif key == 'temp':
					temp = value

				elif key == 'spin':
					spin = self.spincalc(value)	

				elif key == 'reduction':
					reduction = value

				elif key == 'J_min' or key == 'j_min':
					J_min = value

				elif key == 'J_max' or key == 'j_max':
					J_max = value

				elif key == 'inten' or key == 'intensity':
					inten = value

				elif key == 'new_params':
					try:
						if isinstance(value,dict):
							self.add_params(value)
						else:
							raise InitializeError(str(key)+ ' is not a valid dictionary.')
							pass
					except InitializeError as e:
						self.error_message("InitializeError", e.value,0)


				else:
					raise InitializeError(str(key)+' is not a valid argument of calpgm()')
					pass 


		except InitializeError as e: 
			self.error_message("InitializeError",e.value,0)




class spcat(calpgm):

	init_var = ""
	init_int = ""

	cur_var = ""
	cur_int = ""

	pfunc = 1.0 # Partition function for the object stored as a float

	def qrotcalc(self):
		A = self.current_vals_rigid[0]
		B = self.current_vals_rigid[1]
		C = self.current_vals_rigid[2]

		return round((5.3311*10**6)*self.temp**(1.5)*(A*B*C)**(-0.5),3)

	def to_var(self):

		num_params = len(self.current_vals)

		timestamp = datetime.datetime.now().strftime("%a %b %d %I:%M:%S %Y")

		output  = "%s                                        %s \n" %(self.name,timestamp)
		output += "   %s  999   51    0    0.0000E+000    1.0000E+005    1.0000E+000 1.0000000000\n" %(str(num_params))
		output += "%s   %s  1  0  99  0  1  1  1  1  -1   0\n" %(self.reduction,str(self.spin))
		for i in range(0, num_params):

			key_value = str(self.ALL_PARAMS[self.current_vals[i][0]])
			output += "          %s  %s  1.0E-010 /%s \n" %(str(key_value),str(self.current_vals[i][1]),str(self.current_vals[i][0]))

		if self.init_var == "":
			self.init_var = output
		self.cur_var = output


	def to_int(self):
		 self.pfunc = self.qrotcalc()

		 output  = "%s \n"%(self.name)
		 output += "0  91  %s  %s  %s  %s  %s %s  %s\n"%(str(self.pfunc), str(self.J_min), str(self.J_max),"-10","-10",str(self.max_freq), str(self.temp))
		 output += " 001  %s \n" %(str(self.dipoles[0]))
		 output += " 002  %s \n" %(str(self.dipoles[1]))
		 output += " 003  %s \n" %(str(self.dipoles[2]))

		 if self.init_int == "":
		 	self.init_int = output
		 self.cur_int = output

	def get_var(self):
		return self.cur_var

	def get_var_init(self):
		return self.init_var

	def get_int(self):
		return self.cur_int

	def get_int_init(self):
		return self.init_int

	def to_file(self,**kwargs):
		if 'filename' in kwargs:
			out_name = kwargs['filename']
		else: 
			out_name = self.filename

		for key, value in kwargs.iteritems():

			if key == 'type' and value == 'var':
					if 'v' in kwargs:
						if kwargs['v'] == 'init' or kwargs['v'] == 'initial' or kwargs['v'] == 'i':
							output = open(out_name+'.var','wb')
							output.write(self.init_var)
							output.close()
						elif kwargs['v'] == 'cur' or kwargs['v'] == 'current' or kwargs['v'] == 'c':
							output = open(out_name+'.var','wb')
							output.write(self.cur_var)
							output.close()
						else:
							output = open(out_name+'.var','wb')
							output.write(self.cur_var)
							output.close()

			if key == 'type' and value == 'int':
					if 'v' in kwargs:
						if kwargs['v'] == 'init' or kwargs['v'] == 'initial' or kwargs['v'] == 'i':
							output = open(out_name+'.int','wb')
							output.write(self.init_int)
							output.close()
						elif kwargs['v'] == 'cur' or kwargs['v'] == 'current' or kwargs['v'] == 'c':
							output = open(out_name+'.int','wb')
							output.write(self.cur_int)
						else:
							output = open(out_name+'.var','wb')
							output.write(self.cur_var)
							output.close()

	def execute(self, **kwargs):
		try:
			if 'filename' in kwargs:
				output_name = kwargs['filename']
			else: 
				output_name = self.filename

			if 'v' in kwargs:
				if kwargs['v'] == 'init' or kwargs['v'] == 'initial' or kwargs['v'] == 'i':
					if self.init_int != "" and self.init_var != "":

						self.to_file(type='var',filename=output_name,v='i')
						self.to_file(type='int',filename=output_name,v='i')

						# For *nix systems:
						a = subprocess.Popen("./spcat "+output_name,stdout=subprocess.PIPE,shell=True)
						a.stdout.read()
					if self.init_int == "" or self.init_var == "":
						raise ExecuteError('Empty int or var during execute step')

				elif kwargs['v'] == 'cur' or kwargs['v'] == 'current' or kwargs['v'] == 'c':
					if self.cur_var != "" and self.cur_int != "":

						self.to_file(type='var',filename=output_name,v='c')
						self.to_file(type='int',filename=output_name,v='c')

						# For *nix systems:
						a = subprocess.Popen("./spcat "+output_name,stdout=subprocess.PIPE,shell=True)
						a.stdout.read()

					if self.cur_int == "" or self.cur_var == "":
						raise ExecuteError('Empty int or var during execute step')

		except ExecuteError as e:
			self.error_message("ExecuteError",e.value,1)




	def read_cat(self, **kwargs):
	# Returns a pandas data frame with the following columns:
	# - freq  <--- frequency of transition in MHz
	# - inten <--- -log(10) of intensity
	# - J_up / Ka_up / Kc_up <--- QNs of upper state
	# - J_down / Ka_down / Kc_down <--- QNs of lower state
	# - uncert <--- line uncertainties (0 unless you set uncertainties in constants in var file)

		# Checks to see if user wants to filter cat by frequency
		if "min_freq" in kwargs:
			min_freq = kwargs['min_freq']
		else:
			min_freq = 0.0

		if "max_freq" in kwargs:
			max_freq = kwargs['max_freq']
		else:
			max_freq = self.max_freq


		# Checks to see if user wants to filter cat by intensity	
		try: 
		
			if "min_inten" in kwargs:
				if min_inten <= 0.0: # log scale idiot check
					min_inten = kwargs['min_inten']
			else: 
				min_inten = self.inten

			if "max_inten" in kwargs:
				if max_inten > min_inten and max_inten <= 0.0: # Idiot check
					max_inten = kwargs['max_inten']
				else:
					max_inten = 0.0
					raise IdiotCheck('Check your intensities!')
			else:
				max_inten = 0.0

		except IdiotCheck as e:
			self.error_message("IdiotCheck",e.value,1)

		try:
			if not os.path.isfile(self.filename+".cat"):
				raise IOError
			else:
				pass 

		except IOError:
			msg = 'Can\'t find a CAT file with the filename:' + self.filename+".cat\n"
			msg += 'SPCAT has not been executed yet for this object. Please run execute() before you read_cat().'
			self.error_message("IOError",msg,2)


		names = ['freq','uncert','inten','J_up',"Ka_up","Kc_up","J_down","Ka_down","Kc_down"]

		cat_file = []
		f = open(self.filename+".cat")
		for line in f:
			print line
			if float(line[3:13]) > min_freq and float(line[3:13]) < max_freq:
				if float(line[13:21]) < max_inten and float(line[13:21]) > min_inten:
					cat_file.append([float(line[3:13]),float(line[13:21]),float(line[22:29]),int(line[55:57]),int(line[57:59]),int(line[59:61]),int(line[67:69]),int(line[69:71]),int(line[71:73])])
		print cat_file

		if "pretty" in kwargs:
			if kwargs['pretty'] == 1:
				names = ['freq','uncert','inten','J_up',"Ka_up","Kc_up","J_down","Ka_down","Kc_down"]
				df = pn.DataFrame(np.array(cat_file),columns=names)
				return df

		return cat_file


		
	def __init__(self, **kwargs):
		if 'norun' in kwargs:
			if kwargs['norun'] == 1:
				pass
		elif 'data' in kwargs:
			if kwargs['data'] != "" and kwargs['data'] != None:
				super(spcat,self).__init__(**kwargs)
				self.to_var()
				self.to_int()
		pass

def cat_reader(freq_high,freq_low,flag): #reads output from SPCAT

    if flag == "default":
        fh = open("default.cat")

    if flag == "refit":
        fh = open("refit.cat")

    linelist = []
    for line in fh:
        if line[8:9]==".": 
            freq = line[3:13]
            inten = line[22:29]
            qnum_up = line[55:61]
            qnum_low = line[67:73]
            uncert = line[13:21]
            if float(freq)> freq_low and float(freq)<freq_high:#<<<<<<<<<<<<<<<<<<<<
                linelist.append((inten,freq, qnum_up, qnum_low,uncert))
    linelist.sort()
    fh.close()
    return linelist

butt = spcat(data='data')
#print butt.get_var() + "\n\n"
#print butt.get_int()

butt.execute(v='c')

total_time = 0
for i in range(0,100):
	t1 = time.time()
	butt.read_cat()
	t2=time.time()
	total_time += t2-t1

h = butt.read_cat()

#t2=time.time()
print 'the average time read_cat took was: ' + str(total_time/100)

total_time = 0
for i in range(0,100):
	t1 = time.time()
	cat_reader(2000000.0,0.0,"default")
	t2 = time.time()
	total_time += t2-t1
print 'the time it took Ians routine was: ' + str(total_time/100)