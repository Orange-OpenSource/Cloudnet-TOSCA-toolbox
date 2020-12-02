# simple structured logging
import json
import sys
import os

outfile = None # file object to output to
template = ""  # name of the template file
return_code=0  # all OK by default

def configure(template_filename, log_filename) : 
	global outfile, template
	template=template_filename
	if log_filename : 
		outfile=open(log_filename,'a')

def diagnostic(gravity, file, message, cls, **kwargs) :
	global return_code, outfile, template
	if gravity=='info' or outfile == None : return
	return_code = 1
	if file == "":
		file = template
	kwargs.update(gravity=gravity, file=file, message=message, cls=cls)
	json.dump(kwargs, outfile, skipkeys=True)
	outfile.write('\n') # message separator
