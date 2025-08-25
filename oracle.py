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
symbolsAvail = [a,b,c,d,e,f,g,h,sp.abc.i,sp.abc.j,k,l,m,n,o,p,q,r,s,t]
import networkx as nx
import matplotlib.pyplot as plt
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
                new = line.rstrip("\n")
                graphs.append(new)
        for graph in graphs:
            with tf.NamedTemporaryFile(delete=False) as f:      ##create Array of k-node connected Graph Objects, graphKArray
                l = ">>graph6<<" + graph + "\n"
                _ = f.write(l.encode())
                _ = f.seek(0)
                G = nx.read_graph6(f.name)
                self.graphKArray.append(G)
                #alphabetic_labels = {node: chr(65 + node) for node in G.nodes}
                #G = nx.relabel_nodes(G, alphabetic_labels)
                #nx.draw(G,with_labels=True, node_color="blue", font_weight="bold", font_size=10)
                #plt.show()
        return self.graphKArray
    
    def chooseGraph(self,numGraph):   #can be used to iterate through entire graph files
         self.oneGraph = self.graphKArray[int(numGraph)]  ##select which graph from vertex k byte array
         return self.oneGraph
    def printGraph(self):
         if(self.oneGraph == None):
            print("No graph chosen, use chooseGraph() first...")
         else:
            nx.draw(self.oneGraph,with_labels=True, node_color="blue", font_weight="bold", font_size=10)
            plt.show()
	    #continue  ##for  displaying graphs
    
class BooleanInstance:
    def __init__(self, problem, graph):
        self.problem = str(problem)
        self.graph = graph 
        self.edges = graph.edges()         ###initialize object attributes from graph 
        self.nodes = graph.nodes()
        self.k = len(graph.nodes)
        self.minterms = None 
        self.tt = None

        """replace all this junk w a function that takes graph and creates ESOP for given problem 
        - no need for all this bloat
        """
    def getProbESOP(self):
        symbolsAvail = [a,b,c,d,e,f,g,h,sp.abc.i,sp.abc.j,k,l,m,n,o,p,q,r,s]
        t_ = {'a': a, 'b': b, 'c': c, 'd': d, 'e': e, 'f': f,
             'g': g, 'h': h, 'i': sp.abc.i, 'j': sp.abc.j, 'k': k, 'l': l, 
             'm': m, 'n':n, 'o':o,'p':p,'q':q,'r':r,'s':s, 't':t}
        chosenGraph = self.graph
        numEdges = len(chosenGraph.edges())
        symbolUse = []
        edgeConj = []
        XorTerms = []                ##used for parsing
        replacements = {}
        originalMIS = []
        problem = self.problem
        for vertex in chosenGraph.nodes():        ## create symy symbol array 
            symbolUse.append(symbolsAvail[vertex])

        for edge in chosenGraph.edges():
            edgeConj.append((symbolUse[edge[0]] & symbolUse[edge[1]]))  # start with first positive edge (e_0)
            originalMIS.append(sp.Not((symbolUse[edge[0]]) & (symbolUse[edge[1]]))) # also establish the original eq
        originalMIS = sp.And(*originalMIS)

        ## create ( (e_0,1 & ~e_1,2 & ~e_2,3...) XOR (e_1,2 & ~e_2,3 & ...) XOR ... XOR (e_n,m)   (1)
        for i in range(len(edgeConj)):
            j = i + 1
            bigConj = edgeConj[i]
            while(j < len(edgeConj)):           #establish (1) as shown in above document
                neg = sp.Not(edgeConj[j])   
                bigConj = bigConj & neg
                j+=1
            bigConj = sp.logic.boolalg.simplify_logic(bigConj)  #reduce conjugations if possible
            
            
            ## now to deal with any lingering OR terms i.e a & ~b & (~e | ~f) ... 
            ##using conversion to string and parsing bc easier...
            
            prods = []
            numBinomials = 0
            polys = [] # for collecting OR terms after conversion 
            trigger = 0  #"trigger" used to flag when OR terms are reached in the string 
            initTerm = str(bigConj)
            if '|' in initTerm:  ##if lingering OR term(s)
                for i in range(len(initTerm)):
                    if(initTerm[i] == '('):
                        trigger = 1
                    if(trigger == 0):
                        if(initTerm[i].isalpha()):
                            if(initTerm[i-1] == '~'):
                                prods.append(sp.Not(t_[initTerm[i]]))   #if not up to the or terms, collect outside ANDS
                            else:
                                prods.append(t_[initTerm[i]])
                            
                    if (initTerm[i]) == '|': #when reaching an OR, apply a~b ^ b transformation again
                        numBinomials+=1
                        firstVar = initTerm[i-2]
                        secondVar = initTerm[i+3]
                        polys.append(( sp.Xor(sp.And(sp.Not(t_[firstVar]), (t_[secondVar])), sp.Not(t_[secondVar])))) #since we know all naands are negated nors
                trigger = 0
                
                #now,, the extra OR terms have been translated to XOR and AND. i.e:
                # a & ~b & (~e | ~f) & (~g | ~h) = a & ~b & ((~e & f) ^ f) & ((~g & h) ^ ~h)
    
                #multiply out the XOR terms using polynomial multiplication
                multOut = sp.logic.boolalg.distribute_xor_over_and(sp.And(*polys)) 
                polys = [] 
                
                finalXors = []
                finalProds = []
                
                #now to distribute those outside ANDs
                stringMultOut = str(multOut)
                ## deal with constant single first var for simplicity if present 
                #print(stringMultOut)
                j = 0
                if(stringMultOut[0] == '~'):
                    finalProds.append(sp.Not(t_[stringMultOut[1]]))
                    for var in prods:
                        finalProds.append(var) #distr. to first var
                    finalXors.append(sp.logic.boolalg.simplify_logic(sp.And(*finalProds)))
                    j+=4
                
                finalProds = []
                
                for i in range(j,len(stringMultOut)):
                    if(stringMultOut[i].isalpha()):
                        if(stringMultOut[i-1] == '~'):
                            finalProds.append(sp.Not(t_[stringMultOut[i]]))
                            i+=1
                        else:
                            finalProds.append(t_[stringMultOut[i]])
                            
                    elif( (stringMultOut[i] == '^') or (i == (len(stringMultOut) - 1)) ):
                        for vari in prods:
                            finalProds.append(vari)
                        finalXors.append(sp.logic.boolalg.simplify_logic(sp.And(*finalProds)))
                        #print(f"final prods: {finalProds}")
                        finalProds = []
                replacementTerm = str(sp.Xor(*finalXors))
                #print(f"replace {bigConj} -> {replacementTerm}")
                replacements["(" + str(bigConj) + ")"] = replacementTerm
                
            XorTerms.append(bigConj)
            #print(bigConj)
        finalEsop = sp.Xor(*XorTerms)
        finalFr = sp.Not(finalEsop)
        #finalFr = finalEsop
        #graphGetter.printGraph()
        if '|' in str(finalFr):  #resympyfy the final string for truth table
            finalFrS = str(finalFr)
            for rep in replacements:
                finalFrS = finalFrS.replace(rep, replacements[rep])
                
            conjTerms = []
            xorConj = [] 
            #print(finalFrS)
            for i in range(1,len(finalFrS)):
                if ((finalFrS[i] == '^') or ((i == len(finalFrS) - 1)  )):       ##convert string back into Sympy 
                    xorConj.append(sp.And(*conjTerms))
                    conjTerms = []
                elif(finalFrS[i].isalpha()):
                    if(finalFrS[i-1] == '~'):
                        conjTerms.append(sp.Not(t_[finalFrS[i]]))
                    else:
                        conjTerms.append((t_[finalFrS[i]]))
            distroEsop = sp.Xor(*xorConj)
            finalFr = sp.Not(distroEsop)
            #finalFr = distroEsop
        #get the ratio of xor terms per edge in this graph
        returnVal = str(finalFr)[2:(len(str(finalFr))-1)]
        print(returnVal)
        return(returnVal)
             
             
 
        
        
        
   
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
            #print(verifyMIS)
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

    def getRM(self, mode):                                 ######compilation function
        numMinterms = len(self.minterms)
        input_data = f"{len(self.nodes())}\n{numMinterms}\n"          #format
        open("ESOPsimple/between.txt", "w").close() ##file location may change depending on where this ends up
        with open("ESOPsimple/between.txt", "a") as file:
            file.write(input_data)
            for i in range(numMinterms):
                file.write(str(self.minterms[i]))      ##write feasible states
                file.write("\n")
        file.close()
        compileCommand = "g++ ESOPsimple/esopTest.cpp -o ESOPsimple/esopTest"   #compiles c++ code in other directory, may be changed
        subprocess.run(compileCommand, shell = True, check = True)
        runCommand = "ESOPsimple/esopTest"   #runs c++ esopFile.
        result = subprocess.run(runCommand, shell = True, capture_output = True, text = True)
        print(result.stderr)
        output = result.stdout  ###captures output,, 
        
        posEsop_tt, mixEsop_tt = output.split("D") ##formatting ...
        if(mode == "positive"):
            return posEsop_tt                 #returns polarity reed-muller 
        else:
            return mixEsop_tt

    def produceExpression(self, RM):    ##populate list with needed variables 
        varSymbols = []
        for i in range(self.k):
            varSymbols.append(symbolsAvail[i])

        toBeAnded = []
        toBeXord = []
        i = 0
        for char in RM:
            if (char == "1"):
                toBeAnded.append(symbolsAvail[i])
                i+=1
            elif (char == "0"):
                toBeAnded.append(~symbolsAvail[i])      ##convert to sympy expression
                i+=1
            elif (char == "-"):
                i+=1
            elif(char == "\n"):
                continue
            if(i == self.k):
                i = 0
                toBeXord.append(sp.And(*toBeAnded, evaluate = False, strict = True))
                toBeAnded = []
        return sp.Xor(*toBeXord, evaluate = False)
