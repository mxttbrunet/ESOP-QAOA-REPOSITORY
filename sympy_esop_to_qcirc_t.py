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
        print("Quantum Circuit:")
        self.qc.draw(output='mpl')
        self.depths.append(self.qc.depth())
        self.gates.append(sum(self.qc.count_ops().values()))
        print("Final Depths: " + str(self.depths))
        print("Final Gates: " + str(self.gates))
        self.transpile_circuit()

    def esop_to_quantum_circuit(self, ESOP, vars):
        num_qubits = len(vars) + 1  # one extra qubit for the output
        target = num_qubits
        #print(num_qubits)
        qc = QuantumCircuit(num_qubits)
        esopStr = str(ESOP)
        esopStr += "000" #for padding
        i = 0
        ##for occurence of possible initial ~node
        if ( (esopStr[0] == '~') & (esopStr[1].isalpha())):   #ex. ~a ^ (b & d) ^ ....
            qc.x(vars.index(esopStr[1]))
            qc.cx(vars.indez(esopStr[1]), target)     ##simply x-gate the quibit, cnot it with target, x-gate to undo
            qc.x(vars.index(esopStr[1]))
            while(esopStr[i] != '('):
                i+=1

        
        while(esopStr[i] != '0'):
            contr = []
            neg = []
            while(esopStr[i] != ')'):
                if( (esopStr[i] == '~') & (esopStr[i+1].isalpha())):
                    qc.x(vars.index(esopStr[i+1]))
                    contr.append(vars.index(esopStr[i+1]))
                    neg.append(vars.index(esopStr[i+1]))
                    i+=2
                elif(esopStr[i].isalpha()):
                    contr.append(vars.index(esopStr[i]))
                    i+=1
                else:
                    i+=1
            qc.mcx(contr, target)
            j = 0
            while(j < len(neg)):
                qc.x(neg[j])
                j+=1
        """
        for term in esop_terms:
            control_qubits = []
            
            # Extract literals
            if term.func == sp.Not:
                term = term.args[0]
                negated = True
            else:
                negated = False

            literals = term.args if term.func == sp.And else [term]
            for literal in literals:
                #print(literals) #matt for testing
                if isinstance(literal, sp.Symbol):
                    if negated:
                        qc.x(vars.index(literal))  # X gate if negated
                    control_qubits.append(vars.index(literal))
                elif isinstance(literal, sp.Not):
                    negated_var = literal.args[0]
                    if negated_var in vars:
                        qc.x(vars.index(negated_var))  # X gate for negation
                        control_qubits.append(vars.index(negated_var))
                    else:
                        print(f"Warning: {negated_var} is not in the list of variables.")
            
            # Define the target qubit
            target_qubit = num_qubits - 1 if num_qubits - 1 not in control_qubits else num_qubits - 2
            if len(control_qubits) == 1:
                qc.cx(control_qubits[0], target_qubit)  # CNOT for single control
            elif len(control_qubits) == 2:
                qc.ccx(control_qubits[0], control_qubits[1], target_qubit)  # Toffoli for double control
            elif len(control_qubits) > 2:
                qc.mcx(control_qubits, target_qubit)

            if negated:
                # undo X gate
                for literal in literals:
                    if isinstance(literal, sp.Symbol) or (isinstance(literal, sp.Not) and literal.args[0] in vars):
                        qc.x(vars.index(literal))
                        print(literal)
            """

        return qc
    
    def cancel_consecutive_cnot(self, qc):
        i = 0
        while i < len(qc.data()) - 1:
            if (qc.data()[i][0].name() == 'cx' and qc.data()[i+1][0].name() == 'cx' and qc.data()[i][1][0].index() == qc.data()[i+1][1][0].index()):
                qc.data().pop(i)
            else:
                i += 1
        
    def transpile_circuit(self):
        backend = Aer.AerSimulator()
        initial_layout = list(range(self.qc.num_qubits))
        pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=initial_layout)
        transpiled_qc = pass_manager.run(self.qc)
        print(f"Transpiled circuit depth: {transpiled_qc.depth(lambda x: len(x[1]) >= 2)}")
        print(f"Transpiled circuit gates: {sum(transpiled_qc.count_ops().values())}")
        print(transpiled_qc)

if __name__ == "__main__":
    x, y, z = sp.symbols('x y z')
    esop_expr = ((~(x & y) ^ x ^ (y & z)))
    esop_qc = ESOPQuantumCircuit(esop_expr, [x, y, z])

#
