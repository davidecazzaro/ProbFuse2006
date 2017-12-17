#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to combine runs are in this file

import os
import sys
import shutil
import statistics
import datetime


# check that the input folder exists
def check_folders_exist(path):
	if not os.path.isdir(path):
		raise Exception("We expect a folder "+path+" which contains the 10 folders with the runs.")

	for i in range(1,10+1):
		if not os.path.isdir(path+"/run"+str(i)):
			raise Exception("Missing folder: "+path+"/run"+str(i))


# return a list with the paths of the ten .res files
def get_res_files(path):
	res_files = []
	for i in range(1,10+1):
		file_list = [f for f in os.listdir(path+"/run"+str(i)) if f.endswith('.res')]
		if len(file_list) != 1:
			raise Exception('There should be only one .res file in each run directory')
		res_files.append( path+"/run"+str(i)+"/"+file_list[0] )
	return res_files


# return a dict with a key for each topic which contains a list with doc_id and scores
def parse_res_file(path_to_file):
	buckets = {} # a dict of lists
	with open(path_to_file) as fp:
		for line in fp:
			line = line.strip()
			# a line contains: topic_id Q0 doc_id rank score model
			elements = line.split(' ')
			topic_id 	= elements[0]
			q0 			= elements[1]
			doc_id 		= elements[2]
			rank 		= int(elements[3]) # note: rank starts from 0
			score 		= float(elements[4]) # python floats are double
			model 		= elements[5]

			extracted_tuple = (doc_id, score)

			if len(elements) != 6:
				raise Exception("Found a line in '"+path_to_file+"' with "+str(len(elements))+" elements, 6 expected: "+line )

			if topic_id in buckets:
				buckets[topic_id].append( extracted_tuple )
			else:
				buckets[topic_id] = [ extracted_tuple ]
	return buckets


# normalize given scores in 'topic_tuples' which is a list of tuples
# return the same tuples with the new normalized score
# normalization_method can be 'min_max' (default) or 'max'
def normalize_scores(topic_tuples, normalization_method = "min_max"):
	normalization_methods = ['max', 'min_max']
	new_tuples = []

	score_position_in_tuple = 1 # we expect the score to be in the second position in the tuple
	assert(len(topic_tuples) > 0)
	assert(normalization_method in normalization_methods)

	# init min and max with first score value
	score_min = topic_tuples[0][score_position_in_tuple]
	score_max = topic_tuples[0][score_position_in_tuple]

	# let's find the min and max score
	for tup in topic_tuples:
		# update max value found
		if tup[score_position_in_tuple] > score_max:
			score_max = tup[score_position_in_tuple]
		# update min value found
		if tup[score_position_in_tuple] < score_min:
			score_min = tup[score_position_in_tuple]

	assert(score_max >= score_min)

	# if the normalization method is max it means we assume the minimum score is zero
	# max normalization
	if normalization_method == normalization_methods[0]:
		score_min = 0.0
	# otherwise we use score_min and score_max as we did

	# to be sure we are not using integers
	score_max = float(score_max)
	score_min = float(score_min)

	# calculate the new scores
	for tup in topic_tuples:
		tup_current = list(tup) # maybe not the most efficient way
		tup_current[score_position_in_tuple] = normalize_score(tup_current[score_position_in_tuple], score_max, score_min)
		# print("new score: ", tup_current[score_position_in_tuple], " old_score: ", tup[score_position_in_tuple])
		new_tuples.append( tuple(tup_current) )

	return new_tuples


# normalize score given following the paper Lee95 formula for min_max normalization
# to achieve max normalization set score_min to zero
def normalize_score(score, score_max, score_min):
	return float(score - score_min) / float(score_max - score_min)


# save to temporary files the tuples
def append_entries_to_file_by_topic(topic_id, topic_tuples, path_to_tmp_folder):
	filenamepath =  path_to_tmp_folder + str(topic_id) + ".txt"

	with open(filenamepath, "a") as myfile:
		for tup in topic_tuples:
			line = " ".join(str(x) for x in tup)
			myfile.write(line.strip() + "\n")

	return filenamepath


# delete the tmp folder and recreates it
def clean_tmp_files(path_to_tmp_folder):
	# make sure tmp/topic_id.txt file are empty before appending, if they exist
	if os.path.isdir(path_to_tmp_folder):
		# delete all .txt files
		shutil.rmtree(path_to_tmp_folder)
		print("Cleaned all files in "+path_to_tmp_folder)

	# create tmp folder if it does not exists
	# assert(os.path.isdir(path))
	os.makedirs(os.path.dirname(path_to_tmp_folder), exist_ok=True)


# read the file in the tmp folder and return a dict with doc_id as keys and a list of scores
def parse_aggregated_topic(path_to_file):
	bucket = {} # dict
	with open(path_to_file) as fp:
		for line in fp:
			line = line.strip()
			# a line contains: doc_id score model
			tokens = line.split(' ')
			doc_id 	= tokens[0]
			score 	= float(tokens[1])

			extracted_tuple = (doc_id, score)

			if len(tokens) != 2:
				raise Exception("Found a line in '"+path_to_file+"' with "+str(len(tokens))+" tokens, 2 expected: "+line )

			if not doc_id in bucket:
				bucket[doc_id] = []
			bucket[doc_id].append(score)

	return bucket


# apply the passed function to the dict of doc_id => list of scores
def apply_comb_to_aggregated_docs_scores(docs_scores_aggregated, comb_tecnique):
	new_run = []
	new_score_position_in_tuple = 1
	for doc_id, scores in docs_scores_aggregated.items():
		new_score = float( comb_tecnique(scores) )
		new_tuple = ( doc_id, new_score, comb_tecnique.__name__  )
		new_run.append(new_tuple)

	new_run.sort( key=lambda x: float(x[new_score_position_in_tuple]), reverse=True)

	return new_run


# add needed fields to the tuples of doc_id and scores to be saved in a res file
def format_as_trec_run(run, topic_id):
	formatted_run = []
	
	# run is a list of tuples (doc_id, score, model_name) ordered by score (desc)
	# trec format: topic_id Q0 doc_id rank score model
	i = 0
	for row in run:
		formatted_row = (topic_id, "Q0", row[0], i, row[1], row[2])
		i += 1
		formatted_run.append(formatted_row)
	return formatted_run

# append run to res file
def append_run_to_res_file(output_folder, comb_tecnique, formatted_run):
	output_file = output_folder + comb_tecnique + ".res"

	# append to file
	with open(output_file, "a") as myfile:
		for tup in formatted_run:
			line = " ".join(str(x) for x in tup)
			myfile.write(line.strip() + "\n")


# create an ad hoc folder to store results without overwriting existing ones
def prepare_res_file_output_folder(output_folder_path):
	now = datetime.datetime.now()
	foldername = str(now.year) + '{:02d}'.format(now.month) + '{:02d}'.format(now.day) + "_" + '{:02d}'.format(now.hour) + '{:02d}'.format(now.minute) + '{:02d}'.format(now.second)
	output_folder = output_folder_path + "/" + foldername + "/"

	if os.path.isdir( output_folder ):
		raise Exception("Destination folder '"+output_folder+"' already exists.")

	# create folder
	os.makedirs(os.path.dirname(output_folder))

	return output_folder


def combMNZ(scores):
	score = float(sum(scores)) * float(len(scores))
	return score

def combSUM(scores):
	return sum(scores)

def combMAX(scores):
	return max(scores)

def combMIN(scores):
	return min(scores)

def combANZ(scores):
	score = float(sum(scores)) / float(len(scores))
	return score

def combMED(scores):
	return statistics.median(scores)