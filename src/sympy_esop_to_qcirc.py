import sympy as sp
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
# import matplotlib.pyplot as plt --> no longer needed

class ESOPQuantumCircuit:
    def __init__(self):
        self.num_vars = int(input("Enter the number of variables: "))
        self.vars = sp.symbols(' '.join(f'x{i}' for i in range(self.num_vars)))
        self.truth_table = self.input_truth_table(self.num_vars)
        self.ESOP = self.find_ESOP_fxn(self.truth_table, self.vars)
        print("Exclusive Sum of Products (ESOP):", self.ESOP)

        self.qc = self.esop_to_quantum_circuit(self.ESOP, list(self.vars))
        print("Quantum Circuit:")
        print(self.qc)
        self.qc.draw(output='mpl')
        # plt.show() --> makes run time much greater, removed for simplicity sake

    def input_truth_table(self, input_num):
        truth_table_init = []
        for i in range(2**input_num):
            vals = list(map(int, input(f"Enter values for each variable separated by spaces for row {i + 1}: ").split()))
            result = int(input(f"Enter result for row {i + 1}: "))  # can change this in future to automate results based on operation
            truth_table_init.append((*vals, result))
        print("Truth table:", truth_table_init)
        return truth_table_init

    def find_ESOP_fxn(self, tt, vars):
        terms = []
        for row in tt:
            vals, result = row[:-1], row[-1]
            if result == 1:
                terms_new = []
                for i, var in enumerate(vars):
                    if vals[i] == 0:
                        terms_new.append(~var)
                    else:
                        terms_new.append(var)
                terms.append(sp.And(*terms_new))
        return sp.Xor(*terms)

    def esop_to_quantum_circuit(self, ESOP, vars):
        num_qubits = len(vars) + 1  # Add one extra qubit for the output
        qc = QuantumCircuit(num_qubits)
        
        # Convert ESOP to a list of terms
        esop_terms = [ESOP] if ESOP.func != sp.Xor else ESOP.args

        for term in esop_terms:
            control_qubits = []
            for literal in term.args if term.func == sp.And else [term]:
                if isinstance(literal, sp.Symbol):
                    control_qubits.append(vars.index(literal))
                elif isinstance(literal, sp.Not):
                    qc.x(vars.index(literal.args[0]))  # X gate for negation
                    control_qubits.append(vars.index(literal.args[0]))
            
            if len(control_qubits) == 1:
                qc.mcx(control_qubits[0], num_qubits - 1)  # CNOT for single control --> changed to multi-controlled x gate
            elif len(control_qubits) == 2:
                qc.mcx(control_qubits[0], control_qubits[1], num_qubits - 1)  # Toffoli for double control --> changed to multi-controlled x gate
                # for m vertices and n edges, this code's wcs runtime is n(m-1)

            for literal in term.args if term.func == sp.And else [term]:
                if isinstance(literal, sp.Not):
                    qc.x(vars.index(literal.args[0]))  # Undo X gate

        return qc

if __name__ == "__main__":
    esop_qc = ESOPQuantumCircuit()
