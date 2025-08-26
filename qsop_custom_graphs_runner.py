#used for graphs with nodes >=9
from oracle import GraphGenerator, BooleanInstance
import sympy as sp
from scipy.optimize import minimize
import numpy as np
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import Pauli
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from qiskit.visualization import plot_histogram
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import qiskit_aer as Aer
import networkx as nx
from oracle_and_bht_qaoa import *
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t
symbolsAvail = [a,b,c,d,e,f,g,h,sp.abc.i,sp.abc.j,k,l,m,n,o,p,q,r,s,t]
# random 10- 20 nodes

def bruteForceMIS(thisGraph):
   formatting = "0" + str(len(thisGraph.nodes)) + "b"
   numNodes = len(thisGraph.nodes())
   mostNeg = 10
   for l in range( (2**(numNodes))):
      currTry = str((format(l, formatting)))
      if(MISobj(currTry, thisGraph) < mostNeg):
          mostNeg = MISobj(currTry,thisGraph)
   return mostNeg

for numNodes in range(15,21): #can change node range for preference
   pent = 2 * numNodes
   usedGraphs = []
   for graphNum in range(0,50): # 200 graphs each 
      currGraph = nx.Graph()
      for node in range(0,numNodes - 1):
         currGraph.add_edge(node, node+1)
         #ensure connectedness
      numToAdd = np.random.randint(0, ( ((numNodes-1)**2) + (numNodes - 1)  / 2) - (numNodes - 1)) #since max graph has ~ n^2 edges 
      for numAdd in range(numToAdd):
         firstNode = np.random.randint(0,numNodes)
         secondNode = np.random.randint(0,numNodes)
         if(firstNode != secondNode and ([firstNode,secondNode] not in currGraph.edges()) ):
            currGraph.add_edge(firstNode,secondNode)
         else:
            numAdd-=1
            print("FAIL!")
      mostOpt = bruteForceMIS(graph)
      qsopFile.write(f"\n=== NODES: {numNodes}, GRAPH_NUM: {usedGraphs.index(graph)} ===\n\n")
      qsopFile.write(f"ADJACENCY MATRIX\n")
      qsopFile.write(f"{nx.adjacency_matrix(graph)}\n")
      inst = BooleanInstance("MIS", graph)
      esop = inst.getProbESOP()
      pent = 2 * len(currGraph
      for p in range(1,4):
         pars = np.random.rand(2*p)
         appxSum = 0
         for k in range(10):  #can change repetitions here 
            pars[:p] = np.pi / 4
            pars[p:] = np.pi / 8
            expectation = get_expect(graph, pars, p, esop, pent)
            res = minimize(expectation, pars, method = 'COBYLA')
            currCirc = createQAOACirc(res.x, p, graph, esop, pent)
            backendFinal = Aer.AerSimulator()
            currCounts = backendFinal.run(currCirc, shots = 1024).result().get_counts()
            appxSum+=(compExp(currCounts,graph) / mostOpt)

      
      nx.draw(currGraph, labels = True)
      plt.show()
