#oracle classes
##hermann, rebekha, doctor 
##atallah, mostafa
##brunet, matt
##shah, shilpi
"""
CLASSES: booleanExpressionGenerator
    	- creates instance of booleanExpressionGenerator based on number of variables and("feasible states")
    	- has functions to generate sop or pos
	ESOPConverter 
        - creates instance of ESOPConverter based on given expression and form
        - has function to_esop() that converts to unoptimized ANF esop form 

"""

import sympy as sp
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p
symbolsAvail = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p]


class BooleanExpressionGenerator:          
    def __init__(self, numVars,feasibleStates):         ##initial class parameters 
        self.numVars = numVars                          ##number of variables 
        self.feasibleStates = feasibleStates        

        allOnesState = []
        theseSymbols = []                               ##dummy lists

        for i in range(numVars):                        ##this populates  a list of symbols from sympy that will be in the expression
            theseSymbols.append(symbolsAvail[i])        ## also populates the "feasible" all ones state to be removed possibly
            allOnesState.append(1)

        if((allOnesState in self.feasibleStates)):      ##removes all one's state if included
            self.feasibleStates.remove(allOnesState)    ##removing all one's will be useful with esop
                                                    
        self.symbols = theseSymbols                     ##symbols for this expression

    def generateExpression(self, form):                 ##pos or sop expression
        form.upper()
        if (form == "SOP"):
            return sp.logic.boolalg.SOPform(self.symbols, self.feasibleStates, None)   
        elif (form == "POS"):
            return sp.logic.boolalg.POSform(self.symbols, self.feasibleStates, None)
        else:
            print("ERROR\n")

class ESOPConverter:
    def __init__(self,boolExpression, form):  #form variation may be more useful depending on optimization...
        self.boolExpression = boolExpression
        self.form = form.upper()
    def to_esop(self):
        return sp.logic.boolalg.to_anf(self.boolExpression , True)  #unoptimized...
