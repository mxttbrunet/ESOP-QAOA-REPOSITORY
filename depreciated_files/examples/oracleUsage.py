###brunet, matt 07/2024
##example usage of the Reed Muller PipeLine for given graphs and problems 
##example usage of the classes
##imports of required libraries may be distrubuted to main, or the library itself 
import sys
sys.path.insert(0,"..")

import tempfile as tf
import sympy as sp
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t
import networkx as nx
import matplotlib.pyplot as plt
symbolsAvail = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t]
from src.oracle import GraphGenerator, BooleanInstance

if __name__ == "__main__":
    nodes = 7     ##set number of nodes for set of graphs 
    graphNum = 5   ##specify graph by number, 0 through len(kGraphs)

    genGraph = GraphGenerator()                    ##initialize genrator object
    graphArray = genGraph.createKgraphs(nodes)     ##create array of nx graphs from .g6 file 
    #print(graphArray)
