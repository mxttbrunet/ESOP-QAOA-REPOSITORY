import sympy as sp
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import qiskit_aer as Aer
import matplotlib.pyplot as plt



class ESOPQuantumCircuit:
    def __init__(self, esop_expr, vars):
        self.depths = []
        self.gates = []
        self.ESOP = esop_expr
        self.vars = vars
        self.num_vars = len(self.vars)
        print("Exclusive Sum of Products (ESOP):", self.ESOP)

        self.qc = self.esop_to_quantum_circuit(self.ESOP, self.vars)
        print("Transpiled Quantum Circuit:")
        self.transpile_circuit()

    def esop_to_quantum_circuit(self, ESOP, vars):
        #vars is a list of a-k sympy symbols, so conversion to char must be done 
        charList = ['a','b','c','d','e','f','g','h','i','j','k'] 
        num_qubits = len(vars) + 1 # one extra qubit for the output
        target = num_qubits - 1
        qc = QuantumCircuit(num_qubits)
        esopStr = str(ESOP)                        #convert to string 
        esopStr += "000" #for padding


        i = 0
        ##for occurence of possible initial ~node
        if ( (esopStr[0] == '~') & (esopStr[1].isalpha())):   #ex. ~a ^ (b & d) ^ ....
            qc.x(charList.index(esopStr[1]))
            qc.cx(charList.index(esopStr[1]), target)     ##simply x-gate the quibit, cnot it with target, x-gate to undo
            qc.x(charList.index(esopStr[1]))
            while(esopStr[i] != '('):
                i+=1
        elif (( esopStr[0] == '~') & (esopStr[1] == '(')):
            l = num_qubits - 2
            while(l >= 0):
                qc.x(l)
                l-=1
            i = 2

        while(esopStr[i] != '0'):
            contr = [] #to be mcx'd with the target quibit 
            neg = []  # to be un-negated after the multi-control is set 
            while(esopStr[i] != ')'):   #parse term in parentheses
                if( (esopStr[i] == '~') & (esopStr[i+1].isalpha())):  #if variable is negated 
                    qc.x(charList.index(esopStr[i+1]))
                    contr.append(charList.index(esopStr[i+1]))
                    neg.append(charList.index(esopStr[i+1]))
                    i+=2
                elif(esopStr[i].isalpha()):
                    contr.append(charList.index(esopStr[i]))
                    i+=1
                else:
                    i+=1
            qc.mcx(contr, target)
            j = 0
            while(j < len(neg)):
                qc.x(neg[j])
                j+=1
            while(esopStr[i] != '('):
                i+=1
                if(esopStr[i] == '0'):
                   return qc


        
    def transpile_circuit(self):
        backend = Aer.AerSimulator()
        initial_layout = list(range(self.qc.num_qubits))
        pass_manager = generate_preset_pass_manager(optimization_level=3, backend= backend)
        transpiled_qc = pass_manager.run(self.qc)
        print(transpiled_qc.num_qubits)
        print(f"Transpiled circuit depth: {transpiled_qc.depth(lambda x: len(x[1]) >= 2)}")
        print(f"Transpiled circuit gates: {sum(transpiled_qc.count_ops().values())}")
        print(transpiled_qc)

