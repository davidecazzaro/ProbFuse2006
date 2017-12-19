#!/usr/bin/env python
# -*- coding: utf-8 -*-

# plot library for our purposes
from lib.plotutils import *

def main():

	# input verify
	input_folder="input/evaluations"
	output_folder="output/plots"
	# folders check
	folder_check(input_folder)
	folder_check(output_folder, False)

	# get the files from our input folder
	file_list = get_eval_files(input_folder)

	# extract from input:
	# for every file, we extract a dictionary containing all the evaluations (i.e. map, precision/recall)
	feature_per_file = {}
	for file in file_list:
		# removes the useless directory path ("input/evaluations") and the extension (".txt")
		method_name = file[18:-4]
		feature_per_file[method_name] = extract_features(file)
	
	# for every evaluation result, let's filter out only the features we're interested in:

	maps = map_filter(feature_per_file)

	# plotting map
	plot_map(maps, show=False)

if __name__ == '__main__':
   main()