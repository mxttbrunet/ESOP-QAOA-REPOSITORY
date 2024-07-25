import sympy as sp
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import qiskit_aer as Aer
#import matplotlib.pyplot as plt
# from networkx_to_feasible_sols import *

class ESOPQuantumCircuit:
    def __init__(self, esop_expr):
        depths = []
        gates = []
        #self.num_vars = int(input("Enter the number of variables: "))
        #self.vars = sp.symbols(' '.join(f'x{i}' for i in range(self.num_vars)))
        #self.truth_table = self.input_truth_table(self.num_vars)
        self.ESOP = esop_expr
        self.vars = sorted(esop_expr.free_symbols, key=lambda x: str(x))
        self.num_vars = len(self.vars)
        print("Exclusive Sum of Products (ESOP):", self.ESOP)

        self.qc = self.esop_to_quantum_circuit(self.ESOP, self.vars)
        print("Quantum Circuit:")
        print(self.qc)
        # self.transpile_circuit()
        self.qc.draw(output='mpl')
        # plt.show() --> makes run time much greater, removed for simplicity sake
        depths.append(self.qc.depth())
        gates.append(sum(self.qc.count_ops().values()))
        print("Final Depths" + "" + str(depths))
        print("Final Gates" + "" + str(gates))
        self.transpile_circuit()

    def esop_to_quantum_circuit(self, ESOP, vars):
        num_qubits = len(vars) + 1  # one extra qubit for the output
        qc = QuantumCircuit(num_qubits)
        
        # ESOP --> list
        esop_terms = [ESOP] if ESOP.func != sp.Xor else ESOP.args

        for term in esop_terms:
            control_qubits = []
            for literal in term.args if term.func == sp.And else [term]:
                if isinstance(literal, sp.Symbol):
                    control_qubits.append(vars.index(literal))
                elif isinstance(literal, sp.Not):
                    qc.x(vars.index(literal.args[0]))  # X gate for negation
                    control_qubits.append(vars.index(literal.args[0]))
            
            target_qubit = num_qubits - 1 if num_qubits - 1 not in control_qubits else num_qubits - 2
            if len(control_qubits) == 1:
                qc.cx(control_qubits[0], target_qubit)  # CNOT for single control
            elif len(control_qubits) == 2:
                qc.ccx(control_qubits[0], control_qubits[1], target_qubit)  # Toffoli for double control
            elif len(control_qubits) > 2:
                qc.mcx(control_qubits, target_qubit)
                # if two loose x's, cancel

            for literal in term.args if term.func == sp.And else [term]:
                if isinstance(literal, sp.Not):
                    qc.x(vars.index(literal.args[0]))  # undo X gate

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

#if __name__ == "__main__":
    # example esop -- (x0 & ~x1) ^ (x2 & x3)
#    a, b, c, d, e = sp.symbols('a b c d e')
#    esop_expr = (d ^ ~a ^ ~e ^ (d & e) ^ (c & ~a & ~b & ~d))
#    esop_qc = ESOPQuantumCircuit(esop_expr)
