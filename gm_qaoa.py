from qiskit import QuantumCircuit
import numpy as np
import matplotlib.pyplot as plt
from sympy_esop_to_qcirc_t import ESOPQuantumCircuit
import sympy as sp

class StatePrep:
    def __init__(self, esop_expr, vars):
        self.esop_circuit = ESOPQuantumCircuit(esop_expr, vars)
        self.num_qubits = self.esop_circuit.qc.num_qubits

    def state_prep_circuit(self):
        return self.esop_circuit.qc

class GMQAOA:
    def __init__(self, state_prep, p=1):
        self.state_prep = state_prep
        self.p = p

    def build_circuit(self, gamma, beta):
        n = self.state_prep.num_qubits
        circ = QuantumCircuit(n)

        # State preparation
        state_prep_circ = self.state_prep.state_prep_circuit()
        circ.compose(state_prep_circ, inplace=True)

        for _ in range(self.p):
            # Cost function
            for qubit, angle in enumerate(gamma):
                circ.rz(angle, qubit)

            # Grover-like mixer
            circ.append(state_prep_circ.to_gate().inverse(), range(n))  # inverse of state prep
            circ.barrier()
            for qubit in range(n):
                circ.x(qubit)  # apply X gates on all qubits
            circ.barrier()
            circ.mcp(beta/np.pi, list(range(n-1)), n-1)  # angle of beta/pi
            circ.barrier()
            for qubit in range(n):
                circ.x(qubit)  # apply X gates on all qubits
            circ.barrier()
            circ.append(state_prep_circ.to_gate(), range(n))  # state prep

            # QAOA mixer
            # circ.rx(2 * beta, range(n))

        return circ

if __name__ == '__main__':
    x, y, z = sp.symbols('x y z')
    esop_expr = ((~(x & y) ^ x ^ (y & z)))
    vars = [x, y, z]

    state_prep = StatePrep(esop_expr, vars)  # instance for state prep

    gm_qaoa = GMQAOA(state_prep, p=1)
    gamma = [0.1, 0.2, 0.3, 0.4]  # cost function parameters
    beta = 0.5  # mixer function parameter
    gm_qaoa_circ = gm_qaoa.build_circuit(gamma, beta)

    print("GM QAOA Circuit:")
    print(gm_qaoa_circ)

    # display circuit
    gm_qaoa_circ.draw(output='mpl', scale=0.6)
    plt.show()
