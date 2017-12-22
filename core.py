#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to keep code organized
from lib.prob_fuse_lib import *

def main():
	# define folders used
	input_folder_path = "input/relevances"
	output_folder_path = "output/pf2006"

	# quick check on folder existence and its content
	check_relevances_exist(input_folder_path)

	for x in range(1,100):
		for t in range(0.1,1,0.1):
			# calling the core function
			prob_fuse(input_folder_path, output_folder_path, x, t)
	print()
	print("ProbFuse2006 done! Output files are in '" + output_folder_path + "'")
	

if __name__ == '__main__':
   main()