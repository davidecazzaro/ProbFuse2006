#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to keep code organized
from lib.basic_retrieval_helpers import *

def main():
	# define folders used
	input_folder_path = "input/ten_models"
	output_folder_path = "output/ten_models"
	output_tmp_folder_path = output_folder_path + "/tmp/"

	# comb tecniques
	comb_tecniques = [combMNZ, combSUM, combMAX, combMIN, combANZ, combMED]

	# check input/ten_models if there are folders "run" from 1 to 10 and get .res files 
	check_folders_exist(input_folder_path)
	res_files = get_res_files(input_folder_path)

	# clean tmp files
	clean_tmp_files(output_tmp_folder_path)
	
	# iterate the ten models
	tempfilepaths = []
	for filepath in res_files:
		topics_docs_scores = parse_res_file(filepath)

		for topic_id in topics_docs_scores:
			topics_docs_scores[topic_id] = normalize_scores(topics_docs_scores[topic_id], "min_max")

			# save
			tempfilepaths.append( append_entries_to_file_by_topic(topic_id, topics_docs_scores[topic_id], output_tmp_folder_path) )

	print("Done reading run entries of all 10 models and aggregating them by topic")

	for topic_file in tempfilepaths:
		docs_scores_aggregated = parse_aggregated_topic(topic_file)

		for comb_tecnique in comb_tecniques:
			new_run = apply_comb_to_aggregated_docs_scores(docs_scores_aggregated, comb_tecnique)

			print()
			print(comb_tecnique.__name__)
			print("new run len: ", len(new_run))
			print(new_run[1:20])

			# append new_run to file
		break # just to test

	# usa i vari metodi comb per generare delle nuove run fuse

	# output un file per ogni tipo di comb con i 50 topic
	# con i doc ordinati con i nuovi score calcolati


if __name__ == '__main__':
   main()