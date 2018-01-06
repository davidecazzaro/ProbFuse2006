#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.plotutils import *

def main():
	# options
	show_map_comb = False
	show_map_comb_trec5 = False
	show_probfuse = False
	show_comb_max_minmax = False
	show_11pt_rp_curve_probfuse = True

	map_comb_base_input_folder = "input/ten_models"
	map_comb_comb_input_folder = "output/ten_models/20171229_180835"

	# show_map_comb_trec5
	trec5_map_comb_base_input_folder = "input/trec5"
	trec5_map_comb_comb_input_folder = "output/trec5/20171229_115824"
	trec5_map_probfuseall_input_files = ["output/probfuse_trec51_1/ProbFuseAll_25_0.5.res",
										 "output/probfuse_trec51_2/ProbFuseAll_25_0.5.res",
										 "output/probfuse_trec51_3/ProbFuseAll_25_0.5.res",
										 "output/probfuse_trec51_4/ProbFuseAll_25_0.5.res",
										 "output/probfuse_trec51_5/ProbFuseAll_25_0.5.res" ]
	trec5_map_probfusejudged_input_files = ["output/probfuse_trec51_1/ProbFuseJudged_25_0.5.res",
										 "output/probfuse_trec51_2/ProbFuseJudged_25_0.5.res",
										 "output/probfuse_trec51_3/ProbFuseJudged_25_0.5.res",
										 "output/probfuse_trec51_4/ProbFuseJudged_25_0.5.res",
										 "output/probfuse_trec51_5/ProbFuseJudged_25_0.5.res" ]



	# change these as needed, used to plot probfuse
	probfuse_res_folders = ["output/probfuse/","output/probfuse_2/","output/probfuse_3/","output/probfuse_4/","output/probfuse_5/"]
	probfuse_plot_sort_by = "score" # you can sort by ["name", "x", "t", "score", "adjacent"] (x is number of segments)

	# plot side by side comb with max and minmax normalization
	comb_max_folder = "output/ten_models_max/20171230_171440"
	comb_minmax_folder = "output/ten_models/20171229_180835"

	# plot 11pt rp curve
	rp_curve_probfusejudged_files = [  "output/probfuse/ProbFuseJudged_25_0.5.res",
								"output/probfuse_2/ProbFuseJudged_25_0.5.res",
								"output/probfuse_3/ProbFuseJudged_25_0.5.res",
								"output/probfuse_4/ProbFuseJudged_25_0.5.res",
								"output/probfuse_5/ProbFuseJudged_25_0.5.res" ]
	rp_curve_probfuseall_files = [  "output/probfuse/ProbFuseAll_25_0.5.res",
								"output/probfuse_2/ProbFuseAll_25_0.5.res",
								"output/probfuse_3/ProbFuseAll_25_0.5.res",
								"output/probfuse_4/ProbFuseAll_25_0.5.res",
								"output/probfuse_5/ProbFuseAll_25_0.5.res" ]

	trec_eval_command = "./../materialeDelCorso/trec_eval.8.1/trec_eval"
	qrels3_file = "./input/qrels.trec3.txt"
	qrels5_file = "./input/qrels.trec5.txt"
	qrels7_file = "./input/qrels.trec7.txt"

	if show_map_comb_trec5:
		trec5_mean_pfa = get_mean_map(trec5_map_probfuseall_input_files, trec_eval_command, qrels5_file)
		trec5_mean_pfj = get_mean_map(trec5_map_probfusejudged_input_files, trec_eval_command, qrels5_file)

		print(trec5_mean_pfa, trec5_mean_pfj)

		plot_trec_map_comb(trec5_map_comb_base_input_folder, trec5_map_comb_comb_input_folder, trec_eval_command, qrels5_file,
							trec5_mean_pfa, trec5_mean_pfj,
							show=True, save=False)

	if show_map_comb:
		# plotting map_comb
		plot_map_comb(map_comb_base_input_folder, map_comb_comb_input_folder, trec_eval_command, qrels7_file, show=True, save=False)

	# plotting each probfuse model combination of t and x
	if(show_probfuse):
		print("Getting all the scores of probfuse")
		print("Final scores are mean of ",len(probfuse_res_folders)," runs")
		scores = []
		scores_dict = {}
		for folder_with_res_to_evaluate in probfuse_res_folders:
			run_scores = get_map_scores_for_probfuse(folder_with_res_to_evaluate, trec_eval_command, qrels7_file)
			print("Got scores for", folder_with_res_to_evaluate)
		
			# sum scores by key
			for tup in run_scores:
				key = str(tup[0])+"_"+str(tup[1])+"_"+str(tup[2])
				if key not in scores_dict:
					scores_dict[key] = 0.0
				scores_dict[key] += tup[3]
		# return to tuples form as expected by plot function
		for key in scores_dict:
			a = key.split("_")
			scores.append( (a[0], int(a[1]), float(a[2]), scores_dict[key] / float(len(probfuse_res_folders)) ) )
		
		plot_each_probfuse_map(scores, sort_by=probfuse_plot_sort_by) # you can sort by ["name", "x", "t", "score", "adjacent"]

	if show_comb_max_minmax:
		plot_comb_max_min(comb_max_folder, comb_minmax_folder, trec_eval_command, qrels7_file)

	if show_11pt_rp_curve_probfuse:
		rp_curve_points_pfall = get_mean_eleven_point_curve_scores(rp_curve_probfuseall_files, trec_eval_command, qrels7_file)
		rp_curve_points_pfjudged = get_mean_eleven_point_curve_scores(rp_curve_probfusejudged_files, trec_eval_command, qrels7_file)
		plot_probfuse_eleven_points_rp_curve(rp_curve_points_pfall, rp_curve_points_pfjudged)

if __name__ == '__main__':
   main()