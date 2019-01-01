from convertOrbit import create_orbit
import json

def version_calc(version):
	ver_int = int(version[1:3])
	rev_int = int(version[4:7])
	return ver_int + rev_int

def latest_version(ver1, ver2):
	sum1 = version_calc(ver1)
	sum2 = version_calc(ver2)
	if sum1 >= sum2:
		return ver1
	return ver2

file_to_read = "new_files.log"
versions_pred = {}
versions_def = {}
ephem_type = {}
matched_file_names_predictive = {}
matched_file_names_definitive = {}
matched_files_final = {}

with open("fileMap.js") as f:
	for line in f:
		cons_vals = line.split(",")
		cons_vals[0] = cons_vals[0][15:]
		cons_vals[len(cons_vals) - 1] = cons_vals[len(cons_vals) - 1][:-2]
		for i in cons_vals:
			curr = i.split(":")
			curr[0] = curr[0].replace("\"", "")
			curr[0] = curr[0][1:]
			curr[1] = curr[1].replace("\"", "")
			curr[1] = curr[1][1:]
			matched_files_final[curr[0]] = curr[1]

with open(file_to_read) as f:
	f = f.readlines()

counter = 0
total = len(f)
ephem_dict = {0: "-d", 1: "-p", 2: "-g"}

for line in f:
	# get year, num, ver, ephemeris
	split_filename = line[:-1].split("_")
	if len(split_filename) <= 1:
		continue
	ephemeris_type = split_filename[3]
	if ephemeris_type == "Definitive":
		ephemeris = 0
	elif ephemeris_type == "Predictive":
		ephemeris = 1
	else:
		ephemeris = 2
	date = split_filename[4]
	year = date.split("-")[0]
	num = date.split("-")[1]
	ver = split_filename[5].split(".")[0]
	create_orbit(year, num, ver, ephemeris)
	counter += 1
	if date in versions_pred:
		if ephemeris == 1:
			current = versions_pred[date]
			versions_pred[date] = latest_version(current, ver)
	if date in versions_def:
		if ephemeris == 0:
			current = versions_def[date]
			versions_def[date] = latest_version(current, ver)
	else:
		if ephemeris == 0:
			versions_def[date] = ver
		elif ephemeris == 1:
			versions_pred[date] = ver
	if date in versions_def:
		if ephemeris == 0:
			current = versions_def[date]
			versions_def[date] = latest_version(current, ver)
	if ephemeris == 1:
		matched_file_names_predictive[date] = year + "-" + num + "_" + versions_pred[date] + ephem_dict[ephemeris] + ".czml"
	elif ephemeris == 0:
		matched_file_names_definitive[date] = year + "-" + num + "_" + versions_def[date] + ephem_dict[ephemeris] + ".czml"
	print(str(counter) + " files of " + str(total) + " converted")

for pair in matched_file_names_predictive.items():
	matched_files_final[pair[0]] = pair[1]

for pair in matched_file_names_definitive.items():
	matched_files_final[pair[0]] = pair[1]

with open("fileMap.js", "w") as outfile:
	outfile.write("var fileMap = ")
	json.dump(matched_files_final, outfile)
	outfile.write(";");
	outfile.close()
