from oracle import GraphGenerator, BooleanInstance
import sympy as sp
import numpy as np
from qiskit.circuit.library import PauliEvolutionGate
import matplotlib.pyplot as plt
from qiskit.quantum_info import Pauli
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from qiskit.visualization import plot_histogram
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import qiskit_aer as Aer
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t
from scipy.optimize import minimize
symbolsAvail = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t]

def ESOPtoQAOA(params,pval,graph,esop, penal): #uses BHT method for converting ESOP to Hc...
    esop = str(esop) + "00000"   #pad dat thang 
    Hc = 0
    Hgs = []
    j = 0
    largest = 0
    for i in range(esop.count('^') + 1 ):
        currConj = []
        while(esop[j] != '^'):                             
            if(esop[j] == '~'):
                currConj.append(-sp.Symbol(esop[j+1]))     #process ESOP product by product, using them more like nums now
                j+=2                                       # ~a --> -a
            elif(esop[j].isalpha()):
                currConj.append(sp.Symbol(esop[j]))
                j+=1
            elif(esop[j] == '0'):
                break
                
            else:
                j+=1
        #print(currConj)
        j+=1
        
        
        conjLen = len(currConj)
        if(conjLen > largest):        #keep track of prod (conj...) length
            largest = conjLen
            
        if(conjLen >= 3):
                thisPoly = sp.Symbol("I") - currConj[0]               ## binomials for C^nZ
                k = 1
                while(k < conjLen):
                    if(k % 2 == 1):
                        thisPoly*= currConj[k] - sp.Symbol("I")      ## inversion for parity
                    else:
                        thisPoly*=sp.Symbol("I") - currConj[k]
                    k+=1
                thisPoly*= (1 / (2**conjLen))                         
                Hgs.append(thisPoly)
                #print(thisPoly)
        elif(conjLen == 2):
            thisPoly = (-1/4)*sp.Symbol("I") + (1/4)*(currConj[0] + currConj[1] - (currConj[0]*currConj[1]))
            Hgs.append(thisPoly)               #CZ
            #print(thisPoly)
        else:
            thisPoly = (-1/2)*sp.Symbol("I") + (1/2)*conj
            Hgs.append(thisPoly)      #Z
            #print(thisPoly)
    
    
    for term in Hgs:
        Hc+=term
        #Hc*= -1
    Hc*=-penal
    for node in graph.nodes():
        Hc-=(1/2)*(sp.Symbol("I")) - (1/2)*symbolsAvail[node]
    Hc = str(sp.expand(Hc))     ##add these components up to sum for Hc
    #print(Hc)
    
        
    
    cleanUpBins = []
    l = 0
    while(l <= largest):
        cleanUpBins.append([])
        l+=1
    
    #split by + or -  
    currInx = 0
    plus = 0
    minus = 0
    nextPt = 0
    spare = Hc
    while(1):
        if(spare[0] != '+' and spare[0] != '-'):
            thisSign = '+'
        else:
            thisSign = spare[0]
            spare = spare[1:]
        plus = spare.find("+")
        minus = spare.find("-")
        if(plus + minus == -2):
            cleanTerm = (thisSign + spare[1:])
            if(cleanTerm.find("*") != -1):
                tempor = ""
                for j in range(len(cleanTerm)):
                    if(cleanTerm[j] != '*'):
                        tempor+=cleanTerm[j]
                cleanTerm = tempor
            n = 0
            for char in cleanTerm:
                if char.isalpha():
                    n+=1
            
            cleanUpBins[n].append(cleanTerm)
            break
        elif((plus == -1) ^ (minus == -1 )):
            nextPt = max(plus,minus)
        else:
            nextPt = min(plus,minus)
        currTerm = thisSign + spare[1:nextPt]
        #print(currTerm)
        spare = spare[nextPt:]
        cleanTerm = ""
        j = len(currTerm) - 1
        coeffLen = currTerm.find("*")
        thisCoeff = currTerm[:coeffLen]
        cleanTerm += thisCoeff
        rev = ""
        numZs = 0
        while( ((not (currTerm[j].isdigit())) and (not (currTerm[j] == 'I') ))):
            if(currTerm[j].isalpha()):
                numZs+=1
                rev+=currTerm[j]
            j-=1
        #print(rev[::-1])
        cleanTerm += rev[::-1]
        
        if(cleanTerm.find("*") != -1):
            tempor = ""
            for j in range(len(cleanTerm)):
                if(cleanTerm[j] != '*'):
                    tempor+=cleanTerm[j]
            cleanTerm = tempor
                    
        #print(cleanTerm)
        cleanUpBins[numZs].append(cleanTerm)
              
              
        #currTerm+=Hc[min(plus,minus)]
    
    
    zeroSum = 0
    for num in cleanUpBins[0]:
        zeroSum+=float(num)
    cleanUpBins[0].clear()
    cleanUpBins[0].append(zeroSum)
    
    
    index = 0
    for abin in cleanUpBins:
        #print(abin)
        if(len(abin) <= 1):
            pass
        else:
            endingDict = {}
            for i in range(len(abin)):
                thisOp = abin[i]
                thisEnding = thisOp[-index:]
                #print(f"{thisOp[:-index]} is from {thisOp}")
                if(thisEnding in endingDict):
                    prev = float(endingDict[thisEnding])
                    curr = float(thisOp[:-index])
                    endingDict[thisEnding] = prev + curr
                else:
                    endingDict[thisEnding] = float(thisOp[:-index])
            abin.clear()
            for entry in endingDict:
                abin.append(str(endingDict[entry]) + str(entry))
        index+=1

    #print(cleanUpBins)
    return cleanUpBins
    

def rz_n(qCirc, angle, offset, qbits):
    if(len(qbits) == 1):
        qCirc.rz(offset*angle, qbits[0])
    elif(len(qbits) == 2):
        qCirc.rzz(offset*angle, qbits[0],qbits[1])
    else:
        target = qbits[-1]  
        for l in range(len(qbits) - 1):
            qCirc.cx(qbits[l], target)
        
        qCirc.rz(offset*angle, target)
    
        for m in reversed(range(len(qbits) - 1)):
            qCirc.cx(qbits[m], target)


def createQAOACirc(params, pval, graph, thisEsop,pent):
    fullQAOA = QuantumCircuit(len(graph.nodes()))
    fullQAOA.h(range(len(graph.nodes())))
    
    zH = ESOPtoQAOA(params, pval, graph, thisEsop,pent )
    for i in range(pval):
        for k in range(1,len(zH)):
            for l in range(len(zH[k])):
                thisZs = zH[k][l]
                rz_n(fullQAOA, params[i], 2 * float(thisZs[:-k]), [symbolsAvail.index(sp.Symbol(char)) for char in thisZs[-k:]])
        for qubit in range(len(graph.nodes())):
            fullQAOA.rx(2.0 * params[i + pval],qubit)
    fullQAOA.measure_all()
    return fullQAOA

def runCircuit(qcirc):
    backend = Aer.AerSimulator()
    counts = backend.run(qcirc, shots = 2048).result().get_counts()
    return counts

#sum over all verticies in graph
#get diag mtx
def MISobj(strSol, graph):
    strSol = strSol[::-1]
    obj = 0
    for char in strSol:
        obj-=int(char)
    q = 0
    for edge in graph.edges():
        if(int(strSol[edge[0]]) and int(strSol[edge[1]])):
            q = strSol.count('1')
    return obj+q

def compExp(counts, graph):
    avg = 0
    countSum = 0
    for stringy,count in counts.items():
        objective = MISobj(stringy, graph)
        avg += objective * count
        countSum+= count
    return (avg / countSum)
    
def get_expect(graph, pList, pvalue, ESOP, pent):
    lmao = pList
    lmaoEsop = ESOP
    def execute_it(lmao):
        thisCirc = createQAOACirc(lmao, pvalue, graph, lmaoEsop,pent)
        #print(thisCirc)
        thisCounts = runCircuit(thisCirc)
        
        return compExp(thisCounts, graph)
    
    return execute_it
if __name__ == "__main__": #example on 3 vertex
    numNodes = 3
    generator = GraphGenerator()
    graphingArray = generator.createKgraphs(numNodes)

    graphNum = 0  #arbitrary graph chosen 
    testGraph =graphingArray[graphNum]
    generator.chooseGraph(graphNum)
    generator.printGraph()
    testInst = BooleanInstance("MIS", testGraph)
    testESOP = testInst.getProbESOP()
    penal = 2 * len(testGraph.nodes())
    p = 1
    pars = np.random.rand(2*p)
    expectation = get_expect(testGraph, pars, p,testESOP, penal )
    res = minimize(expectation, pars, method = 'COBYLA')
    penalty = len(testGraph.nodes()) * 2
    finalCirc = createQAOACirc(res.x,p, testGraph, testESOP, penal )
    #print(finalCirc)
    backendFinal = Aer.AerSimulator()
    countsFinal = backendFinal.run(finalCirc,shots = 1028).result().get_counts()
    #print(countsFinal)
    plot_histogram(countsFinal)
    plt.show()
