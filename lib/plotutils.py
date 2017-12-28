#!/usr/bin/env python
# -*- coding: utf-8 -*-

# filtering and preprocessing

import os
from matplotlib import pyplot as plt
import numpy as np
import subprocess

def get_map_scores_for_probfuse(folder_with_res_to_evaluate, trec_eval_command, qrels_file):

	files_to_evaluate = [f for f in os.listdir(folder_with_res_to_evaluate) if f.endswith('.res')]

	scores = []

	for res in files_to_evaluate:
		# command line to evaluate is:
		# "./path/to/trec_eval  ./qrels.trec7.txt ./path/to/BM25b0.75_1.res"
		command = [trec_eval_command, qrels_file, folder_with_res_to_evaluate+res ]
		result = subprocess.run( command, stdout=subprocess.PIPE )
		output = result.stdout.decode('utf-8') # get result from trec_eval command

		map_score = get_score_from_trec_eval_output(output, score_name="map")

		# remove extension from file name
		model_name = res[:-4]
		model_name = model_name.split("_")
		model_probfuse = model_name[0] # probfuse judged or probfuse all
		model_x = int(model_name[1]) # number of segments
		model_t = float(model_name[2]) # percentage of queries used as training data

		scores.append( (model_probfuse, model_x, model_t, map_score) )
	return scores

# We need a proper folder to make the script work.
def folder_check(path, io=True):
	if not os.path.isdir(path):
		if(io==True):
			raise Exception(path+" doesn't exist. Please create a ./input/evaluations folder containing the input files")
		else:
			raise Exception(path+" doesn't exist. Please create a ./output/plots folder")


# We expect 10+6 evaluations (or 10+6+1, when ProbFuse is done)
# Returns the list of files inside our input/evaluations folder
def get_eval_files(path):
	eval_files = []
	file_list = os.listdir(path)
	for file in file_list:
		eval_files.append( path+"/"+file )

	return eval_files

# We want to extract all the data from our input files and put it in a nice dictionary
# {feature: value}
def extract_features(path):
	# dictonary of features (i.e. "map: 0.15")
	features = {}
	with open("./"+path) as fp:
		# each line has its feature name and its values; the "all" values is constant for each line (and useless)
		for line in fp:
			# trims the string (l/r) of useless space
			line = line.strip()
			# skip empty lines
			if len(line) <= 0:
				continue

			# values are separated by some spaces and one tab
			tmp = line.split("\t")
			
			if len(tmp) != 3:
				raise Exception("There's something wrong within the input files; Found a line in '"+path+"' with "+str(len(elements))+" elements, 3 expected." )

			feature_name = tmp[0].strip()
			# tmp[1] contains this useless "all" we can ignore
			feature_value = tmp[2].strip() # casting from string to float

			features[feature_name] = feature_value

	return features

def map_filter(all_files_features):
	m = {}
	for x in all_files_features:
		this_file_features = all_files_features[x]
		m[x] = float(this_file_features['map'])
	return m

# takes in input a file generated with trec_eval.
# returns the desired score metric
def get_score_from_trec_eval_output(res_file, score_name="map"):
	lines = res_file.split("\n")

	for line in lines:
		# each line has 3 fields separated by a tab
		tokens = line.split("\t")

		score_metric_name = tokens[0].strip()
		# tokens[1] is 'all' here
		score_value = float(tokens[2].strip())

		if score_metric_name == score_name:
			return score_value

	raise Exception("No score metric named", score_name, "found in file: ", res_file)


def plot_map_comb(maps, show=True, save=True):
	fig, ax = plt.subplots()

	# extracting the couple feature_name/feature_value
	# we force the order we want: models 1 to 10 and then the comb methods 
	run_names = ["eval1", "eval2", "eval3", "eval4", "eval5", "eval6", "eval7", "eval8", "eval9", "eval10",
	"combMIN", "combMAX", "combMED", "combSUM", "combANZ", "combMNZ"]
	labels = ["BM25 \n stoplist", "BM25", "InL2  \n stoplist", "InL2", "TF_IDF \n stoplist", "TF_IDF", "DirichletLM \n stoplist", "DirichletLM", "LGD \n stoplist", "LGD",
	"combMIN", "combMAX", "combMED", "combSUM", "combANZ", "combMNZ"]
	values = []
	for run_name in run_names:
		values.append(float(maps[run_name]))
	
	# set colors for the bars
	color_with_stoplist = 'blue'
	color_no_stoplist = 'dodgerblue'
	color_comb = 'purple'
	colors = (color_with_stoplist, color_no_stoplist, color_with_stoplist, color_no_stoplist, color_with_stoplist, color_no_stoplist, color_with_stoplist, color_no_stoplist, color_with_stoplist, color_no_stoplist,
	color_comb, color_comb, color_comb, color_comb, color_comb, color_comb)

	# set graph bound on y axis 
	lower_bound = min(values)
	upper_bound = max(values) 
	plt.ylim(.95*lower_bound, 1.05*upper_bound)

	bar_width=0.8
	ax.bar(np.arange(len(labels)), values, width=bar_width, label="Mean Average Precision", color=colors, tick_label=labels)

	ax.set_xlabel('IR Models')
	ax.set_ylabel('Mean Average Precision')
	ax.set_title('MAP of different models on Trec-7 topics')
	
	# rotate labels
	for tick in ax.get_xticklabels():
		tick.set_rotation(90)

	fig.tight_layout()

	if (save):
		print("Saved plot to ./output/plots/comb_maps.png")
		fig.savefig("./output/plots/comb_maps.png")
	if (show):
		plt.show()

# plot all the probfuse map scores
def plot_each_probfuse_map(scores, sort_by="name"):
	# scores is a list of tuple ( probfuse_name, x, t, score )
	#scores = get_map_scores_for_probfuse()

	# clean plt
	plt.clf()
	plt.cla()
	plt.close()

	# sort them by 
	sort_by_options = ["name", "x", "t", "score"]
	if not (sort_by in sort_by_options):
		raise Exception("Unknown probfuse sorting "+sort_by+". Sort options are: "+" ".join(sort_by_options))

	if sort_by == sort_by_options[0]:
		scores.sort(key=lambda x: x[0]+" "+str(x[1])+" "+str(x[2]))
	if sort_by == sort_by_options[1]:
		scores.sort(key=lambda x: x[1])
	if sort_by == sort_by_options[2]:
		scores.sort(key=lambda x: x[2])
	if sort_by == sort_by_options[3]:
		scores.sort(key=lambda x: x[3])

	labels = []
	values = []
	colors = []
	for tup in scores:
		
		# cutoff plot
		#if(tup[3] < 0.15):
		#	continue
		
		# name + x + t
		print(tup)
		labels.append( tup[0]+" "+str(tup[1])+" "+str(tup[2]))
		# score
		values.append(tup[3])

		# for a nice graph we set the bars color
		if tup[0] == "ProbFuseAll":
			colors.append("blue")
		else:
			colors.append("dodgerblue")

	save = False
	show = True

	fig, ax = plt.subplots()
	

	# set graph bound on y axis 
	lower_bound = min(values)
	upper_bound = max(values) 
	plt.ylim(.95*lower_bound, 1.05*upper_bound)

	bar_width=0.8
	ax.bar(np.arange(len(labels)), values, width=bar_width, label="Mean Average Precision", color=colors, tick_label=labels)

	ax.set_xlabel('Probfuse Models')
	ax.set_ylabel('Mean Average Precision')
	ax.set_title('MAP of different models on Trec-7 topics, varying x and t')
	
	# rotate labels
	for tick in ax.get_xticklabels():
		tick.set_rotation(90)

	fig.tight_layout()

	if (save):
		print("Saved plot to ./output/plots/comb_maps.png")
		#fig.savefig("./output/plots/comb_maps.png")
	if (show):
		plt.show()