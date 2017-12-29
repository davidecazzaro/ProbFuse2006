-  Put here a folder called ten_models which contains the 10 folders called run1, run2, ..., run10
   \forall X \in [1, 10], the runX folder contains the terrier generated files .res, .res.settings and querycounter.
   Keep in mind that we just need the .res files (mandatory: they're the RUNS!).

-  Put here a "qrels.trec7.txt" file, containing the ground truth for the trec_eval tests.

-  Put here a Xtparams.txt file, containing the following:
   x   =   [2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 100, 150, 200, 250, 300, 400, 500, 1000]
   t   =   [1, .9, .8, .7, .6, .5, .4, .3, .2, .1]

   Feel free to modify that file if you want to try other (X,t) parameters, BUT please stick to our notation.
   (do not remove the '\t' characters and use the python-list-like notation)
