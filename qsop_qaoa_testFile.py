from oracle import GraphGenerator, BooleanInstance
import sympy as sp
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import Pauli
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from qiskit.visualization import plot_histogram
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import qiskit_aer as Aer
import networkx as nx
from oracle_and_bht_qaoa import *
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s
symbolsAvail = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s]

def bruteForceMIS(thisGraph):
   formatting = "0" + str(len(thisGraph.nodes)) + "b"
   numNodes = len(thisGraph.nodes())
   mostNeg = 10
   for l in range( (2**(numNodes))):
      currTry = str((format(l, formatting)))
      if(MISobj(currTry, thisGraph) < mostNeg):
          mostNeg = MISobj(currTry,thisGraph)
   return mostNeg



if __name__ == "__main__":
   #f = open("APX_QSOP_RESULTS_3_TO_7.txt", "w")
   #f = open('APPX_QSOP_4_WITH_PENALTY_V_SQUARED.txt', 'w')
   #f = open('APPX_QSOP_RESULTS_8.txt', 'w')
   reps = 100
   for i in range (3,8): #graphs w / nodes 3-8
      gen = GraphGenerator()
      graphList = gen.createKgraphs(i)
      for j in range(0, len(graphList)):
         currGraph = graphList[j]
         pent = 2 * i
         gen.chooseGraph(j)
         mostOpt = bruteForceMIS(currGraph)
         f.write(f"\n=== NODES: {i}, GRAPH_NUM: {j} ===\n\n")
         f.write("ADJACENCY MATRIX:\n")
         f.write(f"{nx.adjacency_matrix(currGraph)}\n")
         currInst = BooleanInstance("MIS", currGraph)
         currESOP = currInst.getProbESOP()
         f.write(f"ESOP: {currESOP}\n")
         for p in range(1,4):  #test for p = 1,2,3
             pars = np.random.rand(2*p)
             greatestAppx = 0
             for k in range(reps): #run reps # of times  
                pars[:p]  = np.pi / 4 
                pars[p:] = np.pi / 8
                expectation = get_expect(currGraph, pars, p, currESOP, pent)
                res = minimize(expectation, pars, method = 'COBYLA')
                currCirc = createQAOACirc(res.x, p, currGraph, currESOP, pent)
                backendFinal = Aer.AerSimulator()
                currCounts = backendFinal.run(currCirc, shots = 1024).result().get_counts()
                appxSum =(compExp(currCounts,currGraph) / mostOpt)
                if(appxSum > greatestAppx):
                   greatestAppx = appxSum
             f.write(f"APPX RATIO WHERE p = {p} : {greatestAppx}\n") 
