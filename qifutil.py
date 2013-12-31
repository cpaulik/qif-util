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

import re
class Rule(list):
	def __init__(self,category):
		self.category=category

	def __str__(self):
		return("%s\n\t"%(self.category)+"\n\t".join([str(item) for item in self])+"\n\n")

	def match(self,record):
		for (code,regex) in self: #If each regex is matched
			value_matched=False
			for value in record[code]: #If any value in record matches regex
				if(regex.search(value)):
					break
			else:
				return(False)
		return(True)
			

	
class Rules(list):
	def __init__(self, f):
		category=None
		rule=None
		super().__init__()
		for line in f:
			line=line.rstrip()
			if(not line): #Blank line
				if rule: self.append(rule)
				rule=None
			elif(line[0]=="#"): #Comment
				continue
			elif(line[0]=="\t" or line[0]==" "): #Regex
				(code,x,regex)=line.strip().partition(":")
				rule.append((code,re.compile(regex)))
			else:
				if line: rule=Rule(line)

	def apply(self,record):
		for rule in self:
			if(rule.match(record)):
				category=rule.category
				l=0
				while True:
					l=category.find("*",l)
					if(l<0): break
					lcode=category[l+1]
					category=category.replace("*%s"%(lcode),record[lcode][0] if(record[lcode]) else "")
					l+=len(record[lcode][0]) if(record[lcode]) else 0
						
				record.category=category
				
				return(record)
		return(record)
