#!/usr/bin/env python

import subprocess
from optparse import OptionParser
import sys, os, random
import numpy as np
from scipy import stats
from collections import Counter,defaultdict
from operator import itemgetter 
from random import randint

parser = OptionParser("$prog [options]")
parser.add_option("-t", "--theta", dest="theta", help="Theta", default=20, type="float")
parser.add_option("-s", "--timesplit", dest="timesplit", help="Split time in 2N_0 generations", default=0.05, type="float")
parser.add_option("-f", "--destfolder", dest="destfolder", help="Destination folder", default=None, type="string")
parser.add_option("-n", "--numsim", dest="numsim", help="Number of simulations", default=100, type="int")
parser.add_option("-c", "--contrate", dest="contrate", help="Contamination rate", default=0.0, type="float")
parser.add_option("-e", "--errorrate", dest="errorrate", help="Error rate", default=0.0, type="float")
parser.add_option("-m", "--meancoverage", dest="meancoverage", help="Mean coverage", default=30.0, type="float")
parser.add_option("-o", "--outfile", dest="outfile", help="Output file", default=None, type="string")
parser.add_option("-a", "--admixrate", dest="admixrate",help="Admixture rate", default=0, type="float")
parser.add_option("-b", "--admixtime", dest="admixtime", help="Admixture time", default=0.0045, type="float")
parser.add_option("-u", "--numtotalhum", dest="numtotalhum",help="Number of total humans sampled", default=100, type="int")
(options,args) = parser.parse_args()

theta = options.theta
timesplit = options.timesplit
destfolder = options.destfolder
numsim = options.numsim
meancoverage = options.meancoverage
errorrate = options.errorrate
contrate = options.contrate
admixrate = options.admixrate
admixtime = options.admixtime
outfile = open(options.outfile,"w")


# Convert to units of 4N_0 generations
timesplitms = timesplit / 2.0

numsamphum = 6
numtotalhum = options.numtotalhum
numarch = 2

puredict = defaultdict(int)
i=1
try:
	while i < (numsim+1):

                # Create simulation file                                                                                                                                                                                                    
                infile_name = "/home/fernando_racimo/TwoPopCont/"+destfolder+"/simul_"+str(i)+"_"+str(randint(0,10000))+".txt"
                if admixrate > 0:
                        commname = "/home/fernando_racimo/bin/msms/bin/msms "+str(numtotalhum+numarch)+" 1 -t "+str(theta)+" -I 2 "+str(numtotalhum)+" "+str(numarch)
                        commname = commname +" -es "+str(admixtime)+" 1 "+str(1 - admixrate)+" -ej "+str(admixtime+0.00001)+" 3 2"+" -ej "+str(timesplitms)+" 1 2 | tail -n+7"
                else:
                        commname = "/home/fernando_racimo/bin/msms/bin/msms "+str(numtotalhum+numarch)+" 1 -t "+str(theta)+" -I 2 "+str(numtotalhum)+" "+str(numarch)+" -ej "+str(timesplitms)+" 1 2 | tail -n+7"
        #       print commname                                                                                                                                                                                                              
        #       i += 1                                                                                                                                                                                                                      
                commname = commname + " | sed 's/1/1,/g' | sed 's/0/0,/g' | sed 's/,$//'"
		
		commname = commname + " > "+infile_name
		v = subprocess.Popen(commname,shell=True)
		v.communicate()
		
		
		try:
			
			print "simul number "+str(i)
			
			# Load and sum matrices
			sitemat = np.loadtxt(infile_name,delimiter=",",dtype="int")

			# Store site data
			for column in sitemat.transpose():
				#modsamp = np.sum(column[0:numsamphum])
				modfreq = float(np.sum(column[0:numtotalhum])) / float(numtotalhum)
				arch = np.sum(column[numtotalhum:(numtotalhum+numarch)])

			
				# Require the site to be segregating
				if (modfreq > 0 and modfreq < 1):
		       	        #if True:
					puredict[(modfreq,arch)] += 1
			i += 1
					
		except:
			continue

		os.remove(infile_name)

except:
	print "Script interrupted"




countdict = defaultdict(int)
i = 1
totalsites = sum(puredict.values())
#totalsites = sum(puredict.keys())
print >>outfile, "Anc\tDer\tPanelFreq\tNum"
for key in puredict.keys():
	#panelsamp = int(key[1])
	panelfreq =  float(key[0])
	archgeno = int(key[1])
#	print "Key: "+str(key)
#	print "Number: "+str(puredict[key])
	coveragevec = np.random.poisson(meancoverage, puredict[key])

	for sitecoverage in coveragevec:
		if sitecoverage > 0:
			if(archgeno == 2):
				q = contrate*panelfreq*(1-errorrate) + contrate*(1-panelfreq)*errorrate + (1-contrate)*(1-errorrate)
			elif(archgeno == 1):
				q = contrate*panelfreq*(1-errorrate) + contrate*(1-panelfreq)*errorrate + (1-contrate)*(1-errorrate)/2.0 + (1-contrate)*errorrate/2.0
			elif(archgeno == 0):
				q = contrate*panelfreq*(1-errorrate)+contrate*(1-panelfreq)*errorrate + (1-contrate)*errorrate

       			numder = np.random.binomial(sitecoverage,q,1)[0]
	       		numanc = sitecoverage - numder

		       	idx = "\t".join([str(numanc),str(numder),str(panelfreq)])
			countdict[idx] += 1
			
			i += 1
		else:
			totalsites = totalsites - 1

sortedkeys = countdict.keys()
sortedkeys.sort()
for key in sortedkeys:
#	print key+"\t"+str(countdict[key])
	print >>outfile, key+"\t"+str(countdict[key])

print "Total sites with coverage > 0: "+str(totalsites)

