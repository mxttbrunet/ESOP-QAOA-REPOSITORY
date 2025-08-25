import numpy as np
import networkx as nx
import matplotlib.pyplot as plt 
from scipy.optimize import minimize
from qiskit import *
import qiskit_aer as Aer
from oracle import GraphGenerator
from qiskit.visualization import plot_histogram
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s
import sympy as sp
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s
symbolsAvail = [a,b,c,d,e,f,g,h,sp.abc.i,sp.abc.j,k,l,m,n,o,p,q,r,s]
lam = 8
# MOST OF THIS IS FROM https://qiskit-rigetti.readthedocs.io/en/latest/examples/QAOA.html
#except makeQAOACirc... I made that for MIS Hc construction simplicity 

def bruteForceMIS(thisGraph):
   formatting = "0" + str(len(thisGraph.nodes)) + "b"
   numNodes = len(thisGraph.nodes())
   mostNeg = 10
   for l in range( (2**(numNodes))):
      currTry = str((format(l, formatting)))
      if(objFunc(currTry, thisGraph) < mostNeg):
          mostNeg = objFunc(currTry,thisGraph)
   return mostNeg



def makeQAOACirc(params, pval, graph):
   qNumNodes = len(graph.nodes())
   qCirc = QuantumCircuit(qNumNodes)
   qCirc.h(range((qNumNodes)))
   Hc = {}
   for j in range(qNumNodes):
      currSym = str(symbolsAvail[j])
      Hc[currSym] = 1/2
   for edge in graph.edges():
      edgeNode1 = str(symbolsAvail[edge[0]])
      edgeNode2 = str(symbolsAvail[edge[1]])
      Hc[edgeNode1]-= (lam / 4)
      Hc[edgeNode2]-= (lam / 4)
      combinedEdge = str(edgeNode1) + str(edgeNode2)
      if  (combinedEdge) not in Hc:
         Hc[combinedEdge] = (lam / 4)
      else:
         Hc[combinedEdge]+= (lam / 4)
   print(Hc)
   nx.draw(graph, with_labels = True)
   plt.show()   
   for i in range(pval):
      for item in Hc.items():
         if(item[1] == 0.0):
            pass
         elif(len(str(item[0])) == 1):
            qCirc.rz(item[1] * 2 * params[i], symbolsAvail.index(sp.Symbol(item[0])))
         else:
            qCirc.rzz(item[1] * 2 * params[i], symbolsAvail.index(sp.Symbol(item[0][0])), symbolsAvail.index(sp.Symbol(item[0][1])))
      for k in range(len(graph.nodes())):
         qCirc.rx(2 * params[i + pval], k)
   qCirc.measure_all()
   #print(qCirc)
   return qCirc

def objFunc(strSol, graph):
   strSol = strSol[::-1]
   obj = 0
   pen = 0
   for bit in strSol:
      obj-=int(bit)
   for edge in graph.edges():
      if(int(strSol[edge[0]]) and int(strSol[edge[1]])):
         pen = lam
   return obj+pen

def computeExpectation(counts, G):
   avg = 0
   countSum = 0
   for stringy, count in counts.items():
      obj = objFunc(stringy, G)
      avg += obj * count 
      countSum += count 

   return (avg / countSum)

def getExpect(g, p, params):
   backend = Aer.AerSimulator()
   theseParams = params
   def executeCircuit(theseParams):
      thisCirc = makeQAOACirc(params, p, g)
      thisCounts = backend.run(thisCirc, shots = 1024).result().get_counts()
      return computeExpectation(thisCounts, g)
   return executeCircuit
   
if __name__ == "__main__":
   #f = open('WREGULAR_RESULTS_15_TO_20.txt', 'w')
   gen = GraphGenerator()
   
   for numNodes in range(3,8): #change to what want 
      pent = 2 * numNodes
      graphArray = gen.createKgraphs(numNodes)
      p = 1
      
      """for graphNum in range(0,1): # 200 graphs each
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
        
         if( (currGraph in usedGraphs) ):
            graphNum-=1
            #if repeat, do it again
         else:"""
      
      for aGraph in graphArray:
         #aGraph = gen.chooseGraph(entryNum)
         #if(entryNum == 10):
         #    sys.exit(0)
         #f.write("\n")
         #f.write(f"== NODES: {numNodes} | ENTRY ==\n")
         #f.write(f"ADJACENCY MATRIX:\n{nx.adjacency_matrix(aGraph)}\n")
         for p in range(1,4):
            best = 0
            perExp = bruteForceMIS(aGraph)
            for i in range(1):
               pars = np.random.rand(2*p)
               exp = getExpect(aGraph,p,pars)
               res = minimize(exp, pars, method = 'COBYLA')
               finalCirc = makeQAOACirc(res.x, p, aGraph)
               backendFinal = Aer.AerSimulator()
               countsFinal = backendFinal.run(finalCirc, shots = 1024).result().get_counts()
               finalExp = computeExpectation(countsFinal, aGraph)
               best = (finalExp / perExp)
            f.write(f"APPRX RATIO: {best} for p = {p}\n")
          
 

