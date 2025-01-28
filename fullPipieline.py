##brunet, matt 07/24 
##shilpi shah

##this shall act as a working file for characterizing the RM expansions,  
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("oracle.py"))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("sympy_esop_to_qcirc.py"))))
import tempfile as tf
import sympy as sp
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t
symbolsAvail = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t]
import networkx as nx
import matplotlib.pyplot as plt
from oracle import GraphGenerator, BooleanInstance
from sympy_esop_to_qcirc import ESOPQuantumCircuit
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import qiskit_aer as Aer
#from networkx_to_feasible_sols import *

def collectProbEsops(prob, polarity, lowerNodes, upperNodes, lowerEntry, upperEntry):
    nodesVSesop = {}

    for i in range(lowerNodes, upperNodes + 1):
        generator = GraphGenerator()                    ##initialize genrator object
        graphArray = generator.createKgraphs(i)     ##create array of nx graphs from .g6 file
        if(upperEntry == "all"): 
            upperEntry = len(graphArray)
            lowerEntry = 0
        for j in range(lowerEntry, upperEntry):
            currGraph = graphArray[j]
            generator.chooseGraph(j)
            currBool = BooleanInstance(prob, currGraph)
            currBool.getTT()
            currRM = currBool.getRM("mixed")
            currESOP = currBool.produceExpression(currRM)
            dicEncoding = str(i) + "," + str(j)
            print(dicEncoding + ": ", currESOP,"\n")
            nodesVSesop[dicEncoding] = currESOP
            generator.printGraph()
        if(upperEntry == len(graphArray)):
            upperEntry = "all"
    return nodesVSesop    




if __name__ == "__main__":
    
    esopDict = collectProbEsops(prob = "MIS", polarity = "mixed", lowerNodes = 4, upperNodes = 4, lowerEntry= 4, upperEntry = 5)
    #print(esopDict)

    for node in esopDict:
        print(node)
        theseSymbols = []
        nodes = node.split(",")
        for i in range(0, int(nodes[0])):
            theseSymbols.append(symbolsAvail[i])
        qc = ESOPQuantumCircuit(esopDict[node], theseSymbols)
