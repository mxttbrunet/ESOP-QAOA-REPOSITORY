from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
import qiskit_aer as Aer
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from sympy_esop_to_qcirc_t import ESOPQuantumCircuit
from scipy.optimize import minimize


      
class StatePrep: # used to find equal superposition
    def __init__(self, esopQC, vars):
        self.esop_circuit = esopQC
        self.num_qubits = self.esop_circuit.qc.num_qubits

    def state_prep_circuit(self):
        return self.esop_circuit.qc

class GMQAOA:
    def __init__(self, state_prep, p, graph):
        self.state_prep = state_prep
        self.p = p
        self.graph = graph

    def build_circuit(self, params):
        n = self.state_prep.num_qubits
        circ = QuantumCircuit(n, n)

        # State preparation
        state_prep_circ = self.state_prep.state_prep_circuit()
        circ.compose(state_prep_circ, inplace=True)
        circ.h(n-1)
        i = 0
        while (i < self.p):

            # Problem unitary 
            for edge in self.graph.edges:
                circ.rz(2*params[i], edge[0])
                circ.rz(2*params[i], edge[1])
                circ.cx(edge[0],edge[1])             ## cost hamiltonian for MIS based on paper
                circ.rz(2*params[i],edge[1])
                circ.cx(edge[0],edge[1])
                circ.rz(2*params[i], n-1)

            #MIXER UNITARY 
            # State preparation inverse
            circ.append(state_prep_circ.to_gate().inverse(), range(n))
            circ.barrier()

            # Apply X gates
            for qubit in range(n):
                circ.x(qubit)
            circ.barrier()

            # Apply MCP gate
            circ.mcp(params[i+1] / np.pi, list(range(n - 1)), n - 1)
            circ.barrier()

            # Undo X gates
            for qubit in range(n):
                circ.x(qubit)
            circ.barrier()

            # State preparation
            circ.append(state_prep_circ.to_gate(), range(n))
            
            # mixer tester for now
            circ.rx(2*params[i+1], range(n))
            i+=2
            
            circ.measure(range(n), range(n))
        return circ


    def run_circuit(self, circ, shots=1024):
        backend = Aer.AerSimulator()
        tcirc = transpile(circ, backend) # transpile circuit
        counts = backend.run(tcirc, shots=shots).result().get_counts()
        return counts

    def get_sol(self, counts):
        # find most freq outcome        
        max_count = max(counts.values())
        sols = [key for key, val in counts.items() if val == max_count]
        return sols




if __name__ == '__main__':
    a, b, c, d, e, f = sp.symbols('a b c d e f')
    esop_expr = (~d ^ (d & ~f) ^ (a & d & ~c) ^ (a & f & ~c) ^ (b & e & ~f) ^ (c & f & ~d) ^ (a & b & c & d) ^ (a & b & c & f) ^ (a & b & f & ~d) ^ (b & f & ~c & ~d) ^ (a & b & d & e & ~f) ^ (a & c & d & ~b & ~f))
    vars = [a, b, c, d, e, f]

    state_prep = StatePrep(esop_expr, vars)  # instance for state prep

    gm_qaoa = GMQAOA(state_prep, p=1)
    gamma = [0.1, 0.2, 0.3, 0.4]  # cost function parameters
    beta = 0.5  # mixer function parameter
    gm_qaoa_circ = gm_qaoa.build_circuit(gamma, beta)

    print("GM QAOA Circuit:")
    print(gm_qaoa_circ)

    # display circuit
    gm_qaoa_circ.draw(output='mpl', scale=0.6)
    #plt.show()

    counts = gm_qaoa.run_circuit(gm_qaoa_circ)

    print("Measurement results: ")
    print(counts)

    sols = gm_qaoa.get_sol(counts)
    print("Most likely solution(s): ")
    print(sols)

    plot_histogram(counts)
    plt.show()
