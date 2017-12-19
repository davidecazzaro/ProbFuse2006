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

def plot_map(maps, show=True, save=True):
	fig, ax = plt.subplots()

	indexes = np.arange(len(maps))

	# extracting the couple feature_name/feature_value
	labels = [x for x in maps]
	values = [float(maps[x]) for x in maps]
	bar_width=0.8

	lower_bound = min(values)
	upper_bound = max(values)

	ax.bar(indexes, values, width=bar_width, color='r', label="Maps")

	ax.set_xlabel('IR Systems')
	ax.set_ylabel('MAP')
	ax.set_title('IR Performances')
	ax.set_xticks(indexes + bar_width / 2)
	ax.set_xticklabels(labels)
	# better visualization

	for tick in ax.get_xticklabels():
		tick.set_rotation(90)

	fig.tight_layout()

	if (save):
		fig.savefig("./output/plots/maps.png")
	if (show):
		plt.show()
