import sympy as sp
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# fxn to input the truth table and corresponding truth values
def input_truth_table(input_num):
    truth_table_init = []
    for i in range(2**input_num):
        vals = list(map(int, input(f"Enter values for each variable separated by spaces for row {i + 1}: ").split()))
        result = int(input(f"Enter result for row {i + 1}: ")) # can change this in future to automate results based on operation
        truth_table_init.append((*vals, result))
    print("Truth table:", truth_table_init)
    return truth_table_init

# fxn to find the ESOP function
def find_ESOP_fxn(tt, vars):
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

# fxn to convert ESOP expression to quantum circuit using Qiskit
def esop_to_quantum_circuit(ESOP, vars):
    num_qubits = len(vars) + 1  # Add one extra qubit for the output
    qc = QuantumCircuit(num_qubits)
    
    # ESOP to a list of terms
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
            qc.cx(control_qubits[0], num_qubits - 1)  # CNOT for single control
        elif len(control_qubits) == 2:
            qc.ccx(control_qubits[0], control_qubits[1], num_qubits - 1)  # Toffoli for double control

        for literal in term.args if term.func == sp.And else [term]:
            if isinstance(literal, sp.Not):
                qc.x(vars.index(literal.args[0]))  # undo X gate

    return qc

def main():
    num_vars = int(input("Enter the number of variables: "))
    vars = sp.symbols(' '.join(f'x{i}' for i in range(num_vars)))
    truth_table = input_truth_table(num_vars)
    ESOP = find_ESOP_fxn(truth_table, vars)
    print("Exclusive Sum of Products (ESOP):", ESOP)

    qc = esop_to_quantum_circuit(ESOP, list(vars))
    print("Quantum Circuit:")
    print(qc)
    qc.draw(output='mpl')
    plt.show()

if __name__ == "__main__":
    main()
