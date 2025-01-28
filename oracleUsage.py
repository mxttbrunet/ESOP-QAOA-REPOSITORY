###brunet, matt 07/2024
##example usage of the Reed Muller PipeLine for given graphs and problems 
##example usage of the classes
##imports of required libraries may be distrubuted to main, or the library itself 
##uncomment print statements
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("oracle.py"))))
import tempfile as tf
import sympy as sp
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t
import networkx as nx
import matplotlib.pyplot as plt
symbolsAvail = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t]
from oracle import GraphGenerator, BooleanInstance

if __name__ == "__main__":
    nodes = 8     ##set number of nodes for set of graphs 
    graphNum = 1   ##specify graph by number, 0 through len(kGraphs)

    genGraph = GraphGenerator()                    ##initialize genrator object
    graphArray = genGraph.createKgraphs(nodes)     ##create array of nx graphs from .g6 file 

    favGraph = genGraph.chooseGraph(graphNum)
    genBool = BooleanInstance("MIS",favGraph) 	#create boolean generator for MIS of this particular graph
    genBool.getTT()   			##give the object it's truth table, as well as minterms 
    genBool.printTT()               #prints feasible states, i.e minterms
    truthTableRM = genBool.getRM("mixed") 	##can be of "positive" polarity --> no negations, or "mixed" --> negations allowed;
    esop = genBool.produceExpression(truthTableRM)

    print("ESOP***: ", esop)
    genGraph.printGraph()  #use w matlib & windows
