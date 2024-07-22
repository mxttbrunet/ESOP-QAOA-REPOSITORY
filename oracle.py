##brunet, matt
##shah, shilpi,
##atallah, mostafa
##wilkie, anthony 
## herrman, rebekah, Doctor 
##classes for RM expansions as gm-qaoa oracles 
##these cover graph file to boolean instance to esop 
##any program using these classes must adjust xgraphFiles to their directory
"""
CLASSES: 

    -   GraphGenerator(self) -> generates .g6 graphs from byte file included in directory 
                       -> createKgraphs(k): takes k num of nodes, and retrives all included graphs  from .g6 files, RETURNS ARRAY OF nx READABLE GRAPHS 
                                -> *adds attribute .graphK to graphGenerator object*, array of k size graphs 
                        -> chooseGraph(int numGraph), from the generator objects .graphK, specify which graph to grab
    -   BooleanInstance(self, string problem, graph) -> creates a boolean oracle object for the given problem instance, and *nx* graph
                        -> getTT() -> calculates boolean expression describing the given problem and graph instance
                                        -> *adds attibute .tt to BooleanInstance, which is a boolean representation of the problem*, equivalent to the truth table 
                                        -> *adds attribute .minterms to BooleanInstance, which is all true bit-strings*
                        -> printTT()-> prints truth table TT in comma separated, line separated, list-quote input format 
"""
import tempfile as tf
import sympy as sp
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t
symbolsAvail = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t]
import networkx as nx
#import matplotlib.pyplot as plt
import subprocess
class GraphGenerator:
    def __init__(self):
        self.oneGraph = None
        self.graphKArray = []
    def createKgraphs(self, k):
        fileName = "xgraphFiles/graph" + str(k) + "c.g6"  ##destination may change depending on usage #construct name of file and directory
        graphs = []
        with open(fileName, "r") as f:
            for line in f:
                new = line.rstrip("\n")                            ##take file bytes from .g6 file and create list of them
                graphs.append(new)
        
        for graph in graphs:
            with tf.NamedTemporaryFile(delete=False) as f:      ##create Array of k-node connected Graph Objects, graphKArray
                l = ">>graph6<<" + graph + "\n"
                _ = f.write(l.encode())
                _ = f.seek(0)
                G = nx.read_graph6(f.name)
                self.graphKArray.append(G)
                #nx.draw(G)
                #plt.show()
        return self.graphKArray
    
    def chooseGraph(self,numGraph):   #can be used to iterate through entire graph files
         self.oneGraph = self.graphKArray[int(numGraph)]  ##select which graph from vertex k byte array
         return self.oneGraph
    def printGraph(self):
         if(self.oneGraph == None):
            print("No graph chosen, use chooseGraph() first...")
         #else:
            #nx.draw(self.oneGraph)
            #plt.show()
	 #   continue  ##for  displaying graphs
    
class BooleanInstance:
    def __init__(self, problem, graph):
        self.problem = str(problem)
        self.graph = graph 
        self.edges = graph.edges()         ###initialize object attributes from graph 
        self.nodes = graph.nodes()
        self.minterms = None 
        self.tt = None

    def getTT(self):   ## creates boolean expression for problem instance, MIS MVC MKC? 
        nodes = self.nodes()
        edges = self.edges()
        symUse = []
        for vertex in nodes:
            symUse.append(symbolsAvail[vertex])     #load available variables 
        if(self.problem == "MVC"):
            toBeAnded = []
            for edge in edges:
                toBeAnded.append((symUse[edge[0]]) | (symUse[edge[1]]))      # AND(x_i OR x_j), for x_i, x_j in E
            verifyMVC =sp.And(*toBeAnded)
            table = sp.logic.boolalg.truth_table(verifyMVC, symUse)
        elif(self.problem == "MIS"):
            toBeAnded = []
            for edge in edges:
                toBeAnded.append(  ~(((symUse[edge[0]])) & ((symUse[edge[1]]))) )   #AND( NOT(x_i AND x_j)) for x_i, x_j in E
            verifyMIS = sp.And(*toBeAnded)
            print(verifyMIS)
            table = sp.logic.boolalg.truth_table(verifyMIS, symUse)
            self.tt = table       ##create attribute to BooleanInstance of entire table
        else:
            print("problem?")
            return -1
        feasibleStates = []
        for t in table:
            strSol = ""            ##collect true terms, "minterms", add attribute 
            for bit in t[0]:
                strSol+= str(bit)
            if(t[1] == True):
                feasibleStates.append(strSol)
        self.minterms = feasibleStates
        return feasibleStates

    def printTT(self):
        for minterm in self.minterms:
            strSol = ""
            for bit in minterm:
                strSol+= str(bit)
            print("'" + strSol + "',")

    def getRM(self):
        numMinterms = len(self.minterms)
        input_data = f"{len(self.nodes())}\n{numMinterms}\n"          #format
        open("ESOPsimple/between.txt", "w").close() ##file location may change depending on where this ends up
        with open("ESOPsimple/between.txt", "a") as file:
            file.write(input_data)
            for i in range(numMinterms):
                file.write(str(self.minterms[i]))      ##write feasible states
                file.write("\n")
        file.close()
        compileCommand = "g++ ESOPsimple/esopTest.cpp -o esopTest"
        subprocess.run(compileCommand, shell = True, check = True)
    
        runCommand = "./esopTest"
        result = subprocess.run(runCommand, shell = True, capture_output = True, text = True)
        print(result.stderr)
        output = result.stdout
        print(output)
