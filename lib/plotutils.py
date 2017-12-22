#!/usr/bin/env python
# -*- coding: utf-8 -*-

# filtering and preprocessing

import os
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
from collections import namedtuple
import math


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
	if((len(file_list)!=16) and (len(file_list)!=17)):
		raise Exception("We're expecting 16 evaluations (or 17): either some input is missing or there are too much files.")
	for file in file_list:
		eval_files.append( path+"/"+file )

	return eval_files

# We want to extract all the data from our input files and put it in a nice dictionary
def extract_features(path):
	# dictonary of features (i.e. "map: 0.15")
	features = {}
	with open(path) as fp:
		# each line has its feature name and its values; the "all" values is constant for each line (and useless)
		for line in fp:
			line = fp.readline()
			# trims the string (l/r) of useless space
			line = line.strip()
			tmp = line.split(' ')
			# unluckily, our input files have a lot of ' ' characters, therefore the split(' ') operation is not enough;
			# split will return several empty elements, which should be filtered out:
			tmp = [x for x in tmp if x!='']
			# even more unluckily, the two last features are separated by a '\t' character and therefore we must capture them, too:
			tmp2 = tmp[1].split('\t')
			# last but not least, this last split operation created an empty [''] character
			tmp2 = [x for x in tmp2 if x!='']
			# the first element contains the feature name, straightforward
			elements = [tmp[0]]
			# the last two features are now contained in the tmp2 vector we just created
			for x in tmp2:
				elements.append(x)

			feature_name = elements[0]
			# elements[1] contains this useless "all" we can ignore
			feature_value = float(elements[2]) # casting from string to float

			if len(elements) != 3:
				raise Exception("There's something wrong within the input files; Found a line in '"+path+"' with "+str(len(elements))+" elements, 3 expected." )

			features[feature_name] = feature_value



	return features

def map_filter(all_features):
	m = {}
	for x in all_features:
		single_file_features = all_features[x]
		m[x] = single_file_features['map']
	return m

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
		print(run_name, maps[run_name])
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