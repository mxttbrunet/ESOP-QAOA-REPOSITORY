#oracle classes


##hermann, rebekha, doctor 
##atallah, mostafa
##brunet, matt
##shah, shilpi
"""
CLASSES: booleanExpressionGenerator
    	- creates instance of booleanExpressionGenerator based on number of variables and minterms ("feasible states")
    	- has functions to generate sop or pos
"""

import sympy as sp
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p
symbolsAvail = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p]


class booleanExpressionGenerator:          
    def __init__(self, numVars,listOfMinterms):         ##initial class parameters 
        self.numVars = numVars                          ##number of variables 
        self.listOfMinterms = listOfMinterms         

        allOnesState = []
        theseSymbols = []                               ##dummy lists

        for i in range(numVars):                        ##this populates  a list of symbols from sympy that will be in the expression
            theseSymbols.append(symbolsAvail[i])        ## also populates the "feasible" all ones state to be removed possibly
            allOnesState.append(1)

        if((allOnesState in self.listOfMinterms)):      ##removes all one's state if included
            self.listOfMinterms.remove(allOnesState)    ##removing all one's will be useful with esop
                                                    

        self.symbols = theseSymbols                     ##symbols for this expression

    def generateExpression(self, form):                 ##pos or sop expression
        form.upper()
        if (form == "SOP"):
            return sp.logic.boolalg.SOPform(self.symbols, self.listOfMinterms, None)   
        elif (form == "POS"):
            return sp.logic.boolalg.POSform(self.symbols, self.listOfMinterms, None)
        else:
            print("ERROR\n")
