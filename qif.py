# Copyright 2013 Matt Smith <matt@forsetti.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#http://en.wikipedia.org/wiki/Quicken_Interchange_Format

from datetime import datetime

	
class QIFRecord(list):
	#dict access return/accept list of strings, properties return/accept objects
	
	def __init__(self,account_name,account_type,record):
		self.account_name=account_name
		self.account_type=account_type
		super().__init__(record)
		
	def __getitem__(self,key):
		values=[]
		for k,v in self:
			if(k==key): values.append(v)
		return(values)

	def __setitem__(self,key,values):
		for t in self:
			if(t[0]==key): self.remove(t)
		for v in values:
			self.append((key,v))
		
	@property
	def date(self):
            if not self['D']:
                return None

            datestr = self['D'][-1]
            if "'" not in datestr:
                return(datetime.strptime(datestr,"%m/%d/%Y"))
            else:
                # if year is in "'<year since 2000>" format
                # handle appropriately
                return(datetime.strptime(datestr,"%m/%d'%y"))
	
	@property	
	def amount(self):
            if not self['T']:
                return 0
            else: 
                # handle comma in value
                return(float(self['T'][-1].replace(',', '')))

	@property
	def address(self):
		return("\n".join(self['A']) if self['A'] else None)
	
	@property
	def memo(self):
		return("\n".join(self['M']) if self['M'] else None)

	@property
	def payee(self):
		return("\n".join(self['P']) if self['P'] else None)
		
	@memo.setter
	def memo(self,value):
		self["M"]=value.split('\n')
	
	@property
	def category(self):
		return(self["L"][-1] if self['L'] else None)
		
	@category.setter
	def category(self,category):
		self["L"]=[category]
	

	def __str__(self):
		return(("\n".join("%s%s"%(code, value) for code,value in self))+"\n^\n")
		
	def __lt__(self,other):
		return(self.date<other.date)

class QIF(list):
	def __init__(self,account_name=None,account_type=None):
		self.account_type=account_type
		self.account_name=account_name
		super().__init__()
		
	def __str__(self):
		last_name=None
		last_type=None
		s=""
		
		for record in self:
			if(not last_name==record.account_name):
				s+="!Account\nN%s\nT%s\n^\n!Type:%s\n"%(record.account_name,record.account_type,record.account_type)
				last_name=record.account_name
				last_type=record.account_type
			elif(not last_type==record.account_type):
				s+="!Type:%s"%(account.account_name,account.account_type,account.account_type)
				last_type=record.account_type				
			s+=str(record)
		return(s)
		
class QIFReader:
	def __init__(self,source):
		self.account_type=None
		self.account_name=None
		self.account=None
		self.source=source
		
	def __iter__(self):
		state=None
		account=None
		
		record=[]
		
		for line in self.source:
			line=line.strip()
			if(not(line)): continue #Skip blank lines
			if(line.startswith("!Account")):
				state="account"
			elif(state=="account" and line[0]=='N'):
				self.account_name=line[1:].strip()
			elif(state=="account" and line[0]=='T'):
				self.account_type=line[1:].strip()
			elif(state=="account" and line[0]=='^'):
				state=None
			elif(state==None and line.startswith("!Type:")):
				self.account_type=line[6:].strip()
				state="record"
			elif(state=="record" and line[0]=='^'):
				yield(QIFRecord(self.account_name,self.account_type,record))
				record=[]
			elif(state=="record"):
				record.append((line[0],line[1:].strip()))
		if(record): raise ValueError("QIF malformed, does not end on record ending")

class QIFWriter:
	def __init__(self,target,account_name=None,account_type=None):
		self.account_name=account_name
		self.account_type=account_type
		self.target=target
		self.count=0

	def write(self,record):
		if(not self.account_name and record.account_name):
			self.account_name=record.account_name
			self.account_type=record.account_type
			
		if(self.count==0 and self.account_name and self.account_type):
			self.target.write("!Account\nN%s\nT%s\n^\n!Type:%s\n"%(self.account_name,self.account_type,self.account_type))
		if((self.count==0 and not (self.account_name)) or (not (self.account_type==record.account_type))):
			self.target.write("!Type:%s\n"%(record.account_type))
			self.account_type=record.account_type

		self.target.write(str(record))
		self.count+=1
