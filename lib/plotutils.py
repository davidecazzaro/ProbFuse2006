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

def get_map_score(file_to_evaluate, trec_eval_command, qrels_file):
	# command line to evaluate is:
	# "./path/to/trec_eval  ./qrels.trec7.txt ./path/to/BM25b0.75_1.res"
	command = [trec_eval_command, qrels_file, file_to_evaluate]
	result = subprocess.run( command, stdout=subprocess.PIPE )
	output = result.stdout.decode('utf-8') # get result from trec_eval command
	map_score = get_score_from_trec_eval_output(output, score_name="map")
	return map_score

def get_map_scores(files_to_evaluate, trec_eval_command, qrels_file):
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

		if(len(tokens) != 3):
			print("Line without three tokens: ", tokens)
			continue

		score_metric_name = tokens[0].strip()
		# tokens[1] is 'all' here
		score_value = float(tokens[2].strip())

		if score_metric_name == score_name:
			return score_value

	raise Exception("No score metric named", score_name, "found in file: ", res_file)

def autolabel(rects, ax):
	for rect in rects:
		height = rect.get_height()
		ax.text(rect.get_x() + rect.get_width()/2., 1.01*height, ('%.3f' % height)[1:], ha='center', va='bottom')

def plot_trec_map_comb(base_input_folder, comb_input_folder, trec_eval_command, qrels_file, show=True, save=True):
	# set colors for the bars
	color_base = 'blue'
	color_comb = 'purple'
	colors = []

	# calculate map score for the basic runs, averaged over the run we have
	maps = {}
	#for i in [1,2,3,4,5]:
	for i in [1]:
		colors.append(color_base)
		file_base = get_eval_files(base_input_folder+"/"+str(i))
		five_scores = 0
		for f in file_base:
			five_scores += get_map_score(f, trec_eval_command, qrels_file)
		# calculate the mean
		label = str(i)
		if(i == 1):
			label="First run"
		maps[label] = five_scores / 5.0
	print("map score ", maps)

	file_list = get_eval_files(comb_input_folder)
	for res in file_list:
		key = res.split("/")
		key = key[-1] # get filename
		key = key[:-4] # remove extension
		if key == "combMNZ":
			colors.append(color_comb)
			maps[key] = get_map_score(res, trec_eval_command, qrels_file)

	colors.append("green")
	maps["10% combMNZ \n ProbFuse target"] = 0.25144 # from paper

	fig, ax = plt.subplots()
	ax.grid(True, color="#dddddd", zorder=0,axis='y')

	run_names = [k for k in maps]

	values = []
	for run_name in run_names:
		print(run_name, float(maps[run_name]))
		values.append(float(maps[run_name]))


	# set graph bound on y axis 
	lower_bound = min(values)
	upper_bound = max(values) 
	plt.ylim(.95*lower_bound, 1.05*upper_bound)

	bar_width=.8
	rects = ax.bar(np.arange(len(maps)), values, width=bar_width, label="Mean Average Precision", color=colors, tick_label=run_names, zorder=3)

	#ax.set_xlabel('IR Models')
	ax.set_ylabel('Mean Average Precision')
	ax.set_title('MAP of first run and comb techniques on Trec-5 topics')

	autolabel(rects, ax)

	# rotate labels
	#for tick in ax.get_xticklabels():
	#	tick.set_rotation(90)

	fig.tight_layout()

	if (save):
		print("Saved plot to ./output/plots/comb_maps.png")
		fig.savefig("./output/plots/comb_maps.png")
	if (show):
		plt.show()


def plot_map_comb(base_input_folder, comb_input_folder, trec_eval_command, qrels_file, show=True, save=True):
	# calculate map score for the basic runs, averaged over the run we have
	maps = {}
	for i in [1,2,3,4,5,6,7,8,9,10]: # ten models
		file_base = get_eval_files(base_input_folder+"/run"+str(i))
		my_file = ""
		for f in file_base:
			if(f[-4:] == ".res"):
				my_file = f
		file_base = my_file
		if(file_base == ""):
			raise Exception("File ending with res not found")
		maps["eval"+str(i)] = get_map_score(file_base, trec_eval_command, qrels_file)
	print("map score ", maps)

	file_list = get_eval_files(comb_input_folder)
	print(file_list)
	for res in file_list:
		key = res.split("/")
		key = key[-1] # get filename
		key = key[:-4] # remove extension
		maps[key] = get_map_score(res, trec_eval_command, qrels_file)

	fig, ax = plt.subplots()
	#ax.grid(True, color="#dddddd", zorder=0)

	# extracting the couple feature_name/feature_value
	# we force the order we want: models 1 to 10 and then the comb methods 
	run_names = ["eval1", "eval2", "eval3", "eval4", "eval5", "eval6", "eval7", "eval8", "eval9", "eval10",
	"combMIN", "combMAX", "combMED", "combSUM", "combANZ", "combMNZ"]
	labels = ["BM25 \n stoplist", "BM25", "InL2  \n stoplist", "InL2", "TF_IDF \n stoplist", "TF_IDF", "DirichletLM \n stoplist", "DirichletLM", "LGD \n stoplist", "LGD",
	"combMIN", "combMAX", "combMED", "combSUM", "combANZ", "combMNZ"]
	values = []
	for run_name in run_names:
		print(run_name, float(maps[run_name]))
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
	rects = ax.bar(np.arange(len(labels)), values, width=bar_width, label="Mean Average Precision", color=colors, tick_label=labels, zorder=3)

	ax.set_xlabel('IR Models')
	ax.set_ylabel('Mean Average Precision')
	ax.set_title('MAP of different models on Trec-7 topics')

	autolabel(rects, ax)
	
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
	ax.grid(True, color="#dddddd", zorder=0, axis='y')

	# set graph bound on y axis 
	lower_bound = min(values)
	upper_bound = max(values) 
	plt.ylim(.95*lower_bound, 1.05*upper_bound)

	bar_width=0.8
	ax.bar(np.arange(len(labels)), values, width=bar_width, label="Mean Average Precision", color=colors, tick_label=labels, zorder=3)

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

def get_file_name_from_path(path):
	f = path.split("/")
	f = f[-1] # get last filename
	f = f[:-4] # remove extension
	return str(f)

# plot side by side comparison of comb methods using max and minmax normalization
# each folder contains the six combXXX.txt files generated by combine.py with the two
# combining methods setted
def plot_comb_max_min(comb_max_folder, comb_minmax_folder, trec_eval_command, qrels_file):
	max_comb_files = get_eval_files(comb_max_folder)
	minmax_comb_files = get_eval_files(comb_minmax_folder)

	scores = []
	for f in max_comb_files:
		scores.append( (get_file_name_from_path(f) + "_max", get_map_score(f, trec_eval_command, qrels_file) ) )
		

	for f in minmax_comb_files:
		scores.append( (get_file_name_from_path(f) + "_min_max", get_map_score(f, trec_eval_command, qrels_file)) )

	scores.sort()

	print(scores)
	
	scores_max = []
	scores_minmax = []
	labels_max = []
	labels_minmax = []
	for i in range(int(len(scores)/2)):
		scores_max.append(scores[i*2][1])
		scores_minmax.append(scores[i*2+1][1])
		labels_max.append(scores[i*2][0])
		labels_minmax.append(scores[i*2+1][0][:-8])

	# lets plot it
	fig, ax = plt.subplots()
	ax.grid(True, color="#dddddd", zorder=0, axis='y')

	# set graph bound on y axis 
	lower_bound = 0.15
	upper_bound = 0.22
	plt.ylim(.95*lower_bound, 1.05*upper_bound)

	bar_width=0.4
	z = .02
	ind = np.arange(len(labels_max))
	rects_max = ax.bar(ind-z, scores_max, width=bar_width, label="Mean Average Precision", color="dodgerblue", tick_label=labels_max, zorder=3)
	rects_minmax = ax.bar(ind+bar_width, scores_minmax, width=bar_width, label="Mean Average Precision", color="purple", tick_label=labels_minmax, zorder=3)

	ax.legend( (rects_max[0], rects_minmax), ('max_norm', 'min_max_norm') )

	ax.set_xticks(ind+bar_width/2-z/2)

	ax.set_xlabel('Comb fusions')
	ax.set_ylabel('Mean Average Precision')
	ax.set_title('Comparing MAP of comb techniques with different normalizations')
	
	# rotate labels
	for tick in ax.get_xticklabels():
		tick.set_rotation(90)

	autolabel(rects_max, ax)
	autolabel(rects_minmax, ax)

	fig.tight_layout()

	plt.show()