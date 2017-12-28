#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.plotutils import *

def main():

	# input verify
	input_folder="input/evaluations"
	output_folder="output/plots"

	# change these as needed, used to plot probfuse
	folder_with_res_to_evaluate = "./../ProbFuse2006/output/probfuse/"
	trec_eval_command = "./../materialeDelCorso/trec_eval.8.1/trec_eval"
	qrels_file = "./../materialeDelCorso/qrels.trec7.txt"

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
		method_name = file.split("/")
		method_name = method_name[-1] # take the file name
		method_name = method_name[:-4] # remove extension
		feature_per_file[method_name] = extract_features(file)
	
	# for every evaluation result, let's filter out only the features we're interested in:
	maps = map_filter(feature_per_file)

	# plotting map_comb
	plot_map_comb(maps, show=False, save=False)

	# plotting each probfuse model combination of t and x
	print("Getting all the scores of probfuse")
	scores = get_map_scores_for_probfuse(folder_with_res_to_evaluate, trec_eval_command, qrels_file)
	plot_each_probfuse_map(scores, sort_by="t")

if __name__ == '__main__':
   main()