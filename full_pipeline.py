##brunet, matt 07/24 
##shilpi shah
##this shall act as a working file for characterizing the RM expansions,  
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("oracle.py"))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("sympy_esop_to_qcirc.py"))))
import tempfile as tf
import sympy as sp
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k
import networkx as nx
import matplotlib.pyplot as plt
from oracle import GraphGenerator, BooleanInstance
from sympy_esop_to_qcirc_t import ESOPQuantumCircuit
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import qiskit_aer as Aer
#from networkx_to_feasible_sols import *
from oracle_and_gm_qaoa import *

graphList = []

def collectProbEsops(prob, polarity, lowerNodes, upperNodes, lowerEntry, upperEntry):
    nodesVSesop = {}
    for i in range(lowerNodes, upperNodes + 1):
        generator = GraphGenerator()                    ##initialize genrator object
        graphArray = generator.createKgraphs(i)     ##create array of nx graphs from .g6 file
        if(upperEntry == "all"): 
            upperEntry = len(graphArray)
            lowerEntry = 0
        for j in range(lowerEntry, upperEntry + 1):
            currGraph = graphArray[j]
            graphList.append(currGraph)
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

def MIS_obj(bitStr, graph): #objective function to minimize...
    obj = 0
    for edge in graph.edges:
        obj+= (int(bitStr[edge[0]]) + int(bitStr[edge[1]]) + int(bitStr[edge[0]])*int(bitStr[edge[1]]) - int(bitStr[len(bitStr) - 1])) 
    return obj

def compute_expectation(counts, G):
    average = 0
    count_sum = 0
    for str, count in counts.items():                 #finds average expectation 
        obj = MIS_obj(str, G)
        average+= obj*count
        count_sum += count
    return (average / count_sum)


def get_exp(G, params):             #runs gmqaoa in a loop to optimize gamma beta 

    def funcToOpt(params):
        gm_qaoa_circ = gm_qaoa.build_circuit(params)
        counts = gm_qaoa.run_circuit(gm_qaoa_circ)
        return compute_expectation(counts, G)
    
    return funcToOpt



if __name__ == "__main__":
    esopDict = collectProbEsops(prob = "MIS", polarity = "mixed", lowerNodes = 4, upperNodes = 4, lowerEntry= 1, upperEntry = 2)
    #print(esopDict)
    k = 0
    for node in esopDict:
        theseSymbols = [a,b,c,d]  ## CHANGE BASED ON NODES
        nodes = node.split(",")
        qc = ESOPQuantumCircuit(esopDict[node], theseSymbols)
        state_prepio = StatePrep(qc, theseSymbols)

        p  = 3
        gm_qaoa = GMQAOA(state_prepio, p, graphList[k])

        gamma = np.random.rand(p)   #for layer in QAOA, generate list of initial gammas and betas 
        beta = np.random.rand(p) 

        paramList = []
        l = 0
        while(l < p):
            paramList.append(gamma[l])    #make parameter list [gamma0, beta0, gamma1, beta1... gamma_p, beta_p]
            paramList.append(beta[l])
            l+=1

        exp = get_exp(graphList[k], paramList)
        optParams = minimize(exp, paramList, method = 'COBYLA').x   #optimize gammas and betas subject to obj func
        print(optParams)
        
        gm_qaoa_circ = gm_qaoa.build_circuit(optParams)     ##run GM-QAOA with optimized parameters 
        counts = gm_qaoa.run_circuit(gm_qaoa_circ)
        print("Measurement results: ")

        sols = gm_qaoa.get_sol(counts)
        print("Most likely solution(s): ")
        print(sols)


        plot_histogram(counts)
        plt.show()
        nx.draw(graphList[k],with_labels=True, node_color='blue')
        plt.show()
        k+=1
