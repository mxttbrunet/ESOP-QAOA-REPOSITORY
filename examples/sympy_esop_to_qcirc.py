import sympy as sp
from qiskit import QuantumCircuit, transpile, assemble
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# Function to input the truth table and corresponding truth values
def input_truth_table(input_num):
    truth_table_init = []
    for i in range(2**input_num):
        vals = list(map(int, input(f"Enter values for each variable separated by spaces for row {i + 1}: ").split()))
        result = int(input(f"Enter result for row {i + 1}: ")) # can change this in future to automate results based on operation
        truth_table_init.append((*vals, result))
    print("Truth table:", truth_table_init)
    return truth_table_init

# Function to find the ESOP function
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

# Function to optimize the ESOP expression
# def optimize_ESOP(ESOP):
#    return sp.simplify_logic(ESOP, form='dnf')

# Function to convert ESOP expression to quantum circuit using Qiskit
def esop_to_quantum_circuit(ESOP, vars):
    num_qubits = len(vars)
    qc = QuantumCircuit(num_qubits)
    
    # convert ESOP to a list of terms
    esop_terms = sp.sopform(vars, ESOP.args) if ESOP.func == sp.Xor else [ESOP]

    for term in esop_terms:
        control_qubits = []
        for literal in term.args:
            if isinstance(literal, sp.Symbol):
                control_qubits.append(vars.index(literal))
            elif isinstance(literal, sp.Not):
                qc.x(vars.index(literal.args[0]))  # X gate for negation
                control_qubits.append(vars.index(literal.args[0]))
        
        if len(control_qubits) == 1:
            qc.cx(control_qubits[0], num_qubits - 1)  # Apply CNOT for single control
        elif len(control_qubits) == 2:
            qc.ccx(control_qubits[0], control_qubits[1], num_qubits - 1)  # Apply Toffoli for double control

        for literal in term.args:
            if isinstance(literal, sp.Not):
                qc.x(vars.index(literal.args[0]))  # Undo X gate

    return qc

def main():
    num_vars = int(input("Enter the number of variables: "))
    vars = sp.symbols(' '.join(f'x{i}' for i in range(num_vars)))
    truth_table = input_truth_table(num_vars)
    ESOP = find_ESOP_fxn(truth_table, vars)
    print("Exclusive Sum of Products (ESOP):", ESOP)
    #ESOP_optimized = optimize_ESOP(ESOP)
    #print("Optimized Exclusive Sum of Products:", ESOP_optimized)

    qc = esop_to_quantum_circuit(ESOP, list(vars))
    print("Quantum Circuit:")
    print(qc)
    qc.draw(output='mpl')
    plt.show()

if __name__ == "__main__":
    main()
