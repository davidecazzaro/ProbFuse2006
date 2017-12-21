#!/usr/bin/env python
# -*- coding: utf-8 -*-

# plot library for our purposes
from lib.basic_retrieval_helpers import check_folders_exist
from lib.basic_retrieval_helpers import get_res_files
from lib.preprocessing import *

def main():
	ground_truth_path 	= "input/qrels.trec7.txt"
	input_folder_path 	= "input/ten_models"
	output_folder_path 	= "output/relevance_scores"

	# verifying and extracting inputs
	check_folders_exist(input_folder_path)
	check_ground_truth_exist(ground_truth_path)
	results_files = get_res_files(input_folder_path)

	# checking/creating output folders
	os.makedirs(os.path.dirname(output_folder_path+"/"), exist_ok=True)

	# our .res files (obviously) don't have the ground truth for each document extracted.
	# we must create our own set of input files compatible with the probFuse algorithm.

	# then, we extract the ground truth from the file in a proper data structure.
	gndt = extract_ground_truth(ground_truth_path)

	# then, we extract all the ten runs, properly, but we're just interested at the couple
	# doc/relevance, rather than its score, etc.
	# therefore, we extract every document returned by the query on a certain topic and we judge it
	# foreach run=1,...,10; the result will be in output/relevance_scores

	for filepath in results_files:

		# removes everything but the number of the run.
		# what we want, for example, is just "1", so that we can give the correct output name just below
		run_name = filepath[20:].split('/')[0]

		# this will write our "new" input file in the output folder, such that it'll be like: topic_id, doc_id, rel/notrel.
		evaluate_run(filepath, gndt, output_folder_path+"/rel"+run_name+".txt")

	print ("Done!")


if __name__ == '__main__':
   main()