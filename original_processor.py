from ivm_reader import czml_generator_ivm
from mighti_reader import czml_generator_mighti
from uv_reader import czml_generator_uv

file_to_read = "original_files.log"
ivm_files = []
version_check = {}

def sort_type(filename):
	split_name = filename.split("_")
	type = split_name[2]
	return type

def extract_date(filename):
	split_name = filename.split("_")
	date = split_name[4]
	return date

def version_calc(filename):
	split_name = filename.split("_")
	version = split_name[5]
	ver_int = int(version[1:3])
	rev_int = int(version[4:7])
	return ver_int + rev_int

def validate(date, curr_ver, file_type):
	if date not in version_check or version_check[date + "-" + file_type] < curr_ver:
		if file_type[:-2] == "IVM":
			czml_generator_ivm(line[:-1])
		elif file_type[:-2] == "MIGHTI":
			czml_generator_mighti(line[:-1])
		elif file_type == "EUV":
			czml_generator_uv(line[:-1])
	version_check[date + "-" + file_type] = curr_ver

with open(file_to_read) as f:
	f = f.readlines()

for line in f:
	if line[-3 : -1] == "NC":
		type = sort_type(line)
		filename = line[:-1]
		date = extract_date(filename)
		curr_ver = version_calc(filename)
		if (type == "MIGHTI-A" or type == "MIGHTI-B") and (date == "2017-05-27" or date == "2017-05-28" or date == "2017-05-29") and (curr_ver == 2):
			print(filename)
			validate(date, curr_ver, type)
