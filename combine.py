#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to keep code organized
from lib.basic_retrieval_helpers import *

def main():
	# define folders used
	input_folder_path = "input/ten_models"
	output_folder_path = "output/ten_models"
	output_tmp_folder_path = output_folder_path + "/tmp/"

	# comb techniques
	comb_techniques = [combMNZ, combSUM, combMAX, combMIN, combANZ, combMED]

	# check input/ten_models if there are folders "run" from 1 to 10 and get .res files 
	check_folders_exist(input_folder_path)
	res_files = get_res_files(input_folder_path)

	# clean tmp files
	clean_tmp_files(output_tmp_folder_path)

	print("Reading res files...")
	
	# iterate the ten models
	tempfilepaths = []
	for filepath in res_files:
		topics_docs_scores = parse_res_file(filepath)

		for topic_id in topics_docs_scores:
			topics_docs_scores[topic_id] = normalize_scores(topics_docs_scores[topic_id], "min_max")

			# save
			tempfilepaths.append( append_entries_to_file_by_topic(topic_id, topics_docs_scores[topic_id], output_tmp_folder_path) )

	tempfilepaths = list(set(tempfilepaths)) # remove duplicates from list
	tempfilepaths.sort() # not needed but nicer

	print("Done reading run entries of all 10 models and aggregating them by topic")

	# prepare output folder to avoid overwriting or mixing results
	output_res_folder = prepare_res_file_output_folder(output_folder_path)

	for topic_file in tempfilepaths:
		docs_scores_aggregated = parse_aggregated_topic(topic_file)

		# extract topic_id from file name
		topic_id = topic_file.split("/")
		topic_id = topic_id[-1].split(".")
		topic_id = topic_id[0]

		for comb_technique in comb_techniques:
			# apply the desired comb technique to the aggregated scores
			new_run = apply_comb_to_aggregated_docs_scores(docs_scores_aggregated, comb_technique)
			
			# prepare tuple with trec format
			formatted_run = format_as_trec_run(new_run, topic_id)

			# append new_run to file
			append_run_to_res_file(output_res_folder, comb_technique.__name__, formatted_run)

		print("Done topic: " + str(topic_id) + "\r", end=" ")

	print()
	print("Fusion ranking done! Output files are in '" + output_folder_path + "'")
	

if __name__ == '__main__':
   main()