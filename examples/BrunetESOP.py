import sympy as sp
from sympy.abc import a,b,c,d,e,f,g,h,i,j,k
##brunet,matt
##take in symbol table, and hopefully do some ESOP junk...

n = int(input("How many vars?: "))
symbolsAvail = [a,b,c,d,e,f,g,h,i,j,k]
symbols = []
minterms = []
for i in range(0,n):
    symbols.append(symbolsAvail[i])
feas = int(input("How many feasible states?: ") )  


print("ENTER EACH FEASIBLE BINARY STATE:\n")         ##get minterms
for i in range(feas):
    print("State", i, ":") 
    state = input()
    tempState = []
    for j in range(n):
        if (state[j] == "1"):   
            tempState.append(1)     #encode truth table
        else:
            tempState.append(0)
    minterms.append(tempState)
    #print(tempState)
#print(minterms)

sop = sp.SOPform(symbols, minterms)

print("****SOP FORM:  ", sop, " ****")              ##sop form

esop = sp.logic.boolalg.to_anf(sop, True) #converts to ANF form, which is of exclusive products

print("****ESOP FORM:", esop, "****") 


