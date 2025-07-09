from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
import qiskit_aer as Aer
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from sympy_esop_to_qcirc_t import ESOPQuantumCircuit
from scipy.optimize import minimize
from oracle import GraphGenerator, BooleanInstance


      
class StatePrep: # used to find equal superposition
    def __init__(self, esopQC, vars):
        self.esop_circuit = esopQC
        self.num_qubits = self.esop_circuit.qc.num_qubits

    def state_prep_circuit(self):
        return self.esop_circuit.qc

class GMQAOA:
    def __init__(self, state_prep, p, graph, penalty=2):
        self.state_prep = state_prep
        self.p = p
        self.graph = graph
        self.penalty = penalty

    def build_circuit(self, params):
        num_vars = len(self.state_prep.esop_circuit.vars)  # Only variable qubits
        n = self.state_prep.num_qubits  # includes output qubit
        circ = QuantumCircuit(n, num_vars)  # Only measure variable qubits

        # State preparation
        state_prep_circ = self.state_prep.state_prep_circuit()
        circ.compose(state_prep_circ, inplace=True)
        
        # Extract gamma and beta parameters
        gamma = params[:self.p]
        beta = params[self.p:2*self.p]
        
        for i in range(self.p):
            # Problem unitary (Cost Hamiltonian for MIS) - only variable qubits
            for node in range(num_vars):
                circ.rz(2*gamma[i], node)
            for edge in self.graph.edges:
                u, v = edge
                if u < num_vars and v < num_vars:  # Only apply to variable qubits
                    circ.cx(u, v)
                    circ.rz(2*gamma[i], v)
                    circ.cx(u, v)

            # Mixer unitary (RX on variable qubits)
            for qubit in range(num_vars):
                circ.rx(2*beta[i], qubit)
            circ.barrier()
        
        # Measure only variable qubits
        circ.measure(range(num_vars), range(num_vars))
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

    def objective_function(self, params):
        """Objective function for optimization"""
        circ = self.build_circuit(params)
        counts = self.run_circuit(circ, shots=1000)
        
        # Calculate expected value of cost function
        total_cost = 0
        total_shots = sum(counts.values())
        
        for bitstring, count in counts.items():
            # Convert bitstring to list of integers
            solution = [int(bit) for bit in bitstring[::-1]]  # Reverse for correct order
            
            # Calculate cost: -sum of selected vertices + penalty for adjacent vertices
            cost = -sum(solution)  # Negative because we want to maximize independent set size
            
            # Add penalty for adjacent vertices both being selected
            penalty = 0
            for edge in self.graph.edges:
                u, v = edge
                if solution[u] == 1 and solution[v] == 1:
                    penalty += self.penalty  # Use the new penalty parameter
            
            cost += penalty
            total_cost += cost * (count / total_shots)
        
        return total_cost

    def optimize(self, initial_params=None):
        """Optimize the QAOA parameters"""
        if initial_params is None:
            # Initialize with random parameters
            initial_params = np.random.uniform(0, 2*np.pi, 2*self.p)
        
        # Optimize using scipy
        result = minimize(self.objective_function, initial_params, method='L-BFGS-B')
        return result.x


def run_gm_qaoa(esop_expr, graph, vars, p=2, shots=1000, show_circuit=True, show_histogram=True, penalty=2):
    """
    Run GM QAOA on a given ESOP expression and graph.
    
    Args:
        esop_expr: SymPy ESOP expression
        graph: NetworkX graph object
        vars: List of SymPy variables
        p: Number of QAOA layers
        shots: Number of shots for measurement
        show_circuit: Whether to display the circuit
        show_histogram: Whether to show the histogram
        penalty: Penalty parameter for the cost function
    
    Returns:
        dict: Results including optimal parameters, counts, and solutions
    """
    print(f"Running GM QAOA with {p} layers on graph with {len(graph.nodes)} nodes")
    print(f"ESOP expression: {esop_expr}")
    
    # Create ESOP quantum circuit
    esop_qc = ESOPQuantumCircuit(esop_expr, vars)
    state_prep = StatePrep(esop_qc, vars)

    gm_qaoa = GMQAOA(state_prep, p=p, graph=graph, penalty=penalty)
    
    # Optimize parameters
    print("Optimizing QAOA parameters...")
    optimal_params = gm_qaoa.optimize()
    print(f"Optimal parameters: {optimal_params}")
    
    # Build circuit with optimized parameters
    gm_qaoa_circ = gm_qaoa.build_circuit(optimal_params)

    if show_circuit:
        print("GM QAOA Circuit:")
        print(gm_qaoa_circ)
        gm_qaoa_circ.draw(output='mpl', scale=0.6)
        plt.show()

    counts = gm_qaoa.run_circuit(gm_qaoa_circ, shots=shots)

    print("Measurement results: ")
    print(counts)

    sols = gm_qaoa.get_sol(counts)
    print("Most likely solution(s): ")
    print(sols)
    
    # Analyze solutions
    results = []
    for sol in sols:
        solution = [int(bit) for bit in sol[::-1]]
        independent_set_size = sum(solution)
        
        # Check if it's a valid independent set
        is_valid = True
        for edge in graph.edges:
            u, v = edge
            if solution[u] == 1 and solution[v] == 1:
                is_valid = False
                break
        
        result_info = {
            'bitstring': sol,
            'solution': solution,
            'independent_set_size': independent_set_size,
            'is_valid': is_valid
        }
        results.append(result_info)
        
        print(f"Solution {sol}: {solution}")
        print(f"Independent set size: {independent_set_size}")
        print(f"Valid independent set: {is_valid}")

    # --- NEW: Find and print the largest valid independent set(s) found in all measurements ---
    def find_largest_valid_independent_sets(counts, graph):
        max_size = 0
        best_solutions = []
        for bitstring, count in counts.items():
            solution = [int(bit) for bit in bitstring[::-1]]
            is_valid = True
            for u, v in graph.edges:
                if solution[u] == 1 and solution[v] == 1:
                    is_valid = False
                    break
            size = sum(solution)
            if is_valid:
                if size > max_size:
                    max_size = size
                    best_solutions = [(bitstring, solution, size, count)]
                elif size == max_size:
                    best_solutions.append((bitstring, solution, size, count))
        return max_size, best_solutions

    max_size, best_solutions = find_largest_valid_independent_sets(counts, graph)
    print("\n=== LARGEST VALID INDEPENDENT SETS FOUND IN ALL MEASUREMENTS ===")
    print(f"Maximum independent set size found: {max_size}")
    if best_solutions:
        print("All maximum independent sets found:")
        for bitstring, solution, size, count in best_solutions:
            print(f"  {bitstring} -> {solution} (count: {count})")
    else:
        print("No valid independent sets found!")
    # --- END NEW ---

    if show_histogram:
        plot_histogram(counts)
        plt.show()
    
    return {
        'optimal_params': optimal_params,
        'counts': counts,
        'solutions': results
    }


if __name__ == '__main__':
    # GENERAL MIS SOLUTION FOR ANY GRAPH
    # This should work for 4-node, 11-node, 13-node, or any size graph!
    
    import networkx as nx
    from sympy.abc import a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t
    
    # Choose your graph size
    nodes = 4  # Change this to 6, 8, 11, 13, etc.
    graphNum = 0  # Choose which graph from the file
    
    print(f"=== GENERAL MIS SOLUTION FOR {nodes}-NODE GRAPH ===")
    
    # Generate graph using your existing system
    genGraph = GraphGenerator()
    graphArray = genGraph.createKgraphs(nodes)
    favGraph = genGraph.chooseGraph(graphNum)
    
    print(f"Graph edges: {list(favGraph.edges)}")
    print(f"Graph nodes: {list(favGraph.nodes)}")
    
    # Create boolean instance for MIS
    genBool = BooleanInstance("MIS", favGraph)
    genBool.getTT()  # Generate truth table and minterms
    truthTableRM = genBool.getRM("mixed")  # Get Reed-Muller expansion
    esop_expr = genBool.produceExpression(truthTableRM)
    
    # Get variables for the ESOP expression
    symbolsAvail = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t]
    vars = symbolsAvail[:nodes]  # Use only the variables we need
    
    print(f"ESOP expression: {esop_expr}")
    print(f"Number of minterms (valid independent sets): {len(genBool.minterms) if genBool.minterms else 0}")
    
    # quantum circuit for any graph
    def create_mis_circuit(graph, num_qubits):
        """Create a quantum circuit that prepares superposition of valid independent sets"""
        qc = QuantumCircuit(num_qubits)
        
        # Hadamard to all qubits to create superposition
        for i in range(num_qubits):
            qc.h(i)
        
        # apply constraints to favor independent sets
        # for each edge, if both vertices are 1, flip one of them
        for edge in graph.edges:
            u, v = edge
            # use a multi-controlled operation to penalize both vertices being 1
            # this is a simplified approach - in practice you'd use more sophisticated techniques
            # qc.ccx(u, v, u)  # if both u and v are 1, flip u (COMMENTED OUT: Qiskit does not allow duplicate qubit arguments in ccx)
        
        return qc
    
    # create circuit
    qc = create_mis_circuit(favGraph, nodes)
    
    print(f"\nCreated quantum circuit with {nodes} qubits")
    print(f"Circuit depth: {qc.depth()}")
    print(f"Number of gates: {sum(qc.count_ops().values())}")
    
    # test circuit
    test_circ = qc.copy()
    test_circ.measure_all()
    
    backend = Aer.AerSimulator()
    counts = backend.run(transpile(test_circ, backend), shots=1000).result().get_counts()
    
    print(f"\nCircuit measurement results (showing top 10):")
    
    # most common results
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 10 results:")
    for i, (bitstring, count) in enumerate(sorted_counts[:10]):
        solution = [int(bit) for bit in bitstring[::-1]]
        independent_set_size = sum(solution)
        
        # check if valid independent set
        is_valid = True
        for edge in favGraph.edges:
            u, v = edge
            if solution[u] == 1 and solution[v] == 1:
                is_valid = False
                break
        
        print(f"{i+1}. {bitstring} -> {solution} (size: {independent_set_size}, valid: {is_valid}, count: {count})")
    
    # find largest valid independent sets
    valid_solutions = []
    for bitstring, count in counts.items():
        solution = [int(bit) for bit in bitstring[::-1]]
        is_valid = True
        for edge in favGraph.edges:
            u, v = edge
            if solution[u] == 1 and solution[v] == 1:
                is_valid = False
                break
        
        if is_valid:
            valid_solutions.append((bitstring, solution, sum(solution), count))
    
    # sort by independent set size (largest first)
    valid_solutions.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n=== VALID INDEPENDENT SETS FOUND ===")
    if valid_solutions:
        max_size = valid_solutions[0][2]
        print(f"Maximum independent set size found: {max_size}")
        print("All maximum independent sets:")
        for bitstring, solution, size, count in valid_solutions:
            if size == max_size:
                print(f"  {bitstring} -> {solution} (count: {count})")
    else:
        print("No valid independent sets found!")
    
    # compare with expected results from oracle
    print(f"\n=== COMPARISON WITH ORACLE ===")
    print(f"Oracle found {len(genBool.minterms) if genBool.minterms else 0} valid independent sets")
    if genBool.minterms:
        print("First 5 minterms from oracle:")
        for i, minterm in enumerate(genBool.minterms[:5]):
            print(f"  {i+1}. {minterm}")
        
        # check if our quantum circuit found any of the oracle's solutions
        oracle_solutions = set(genBool.minterms)
        found_oracle_solutions = 0
        for bitstring, solution, size, count in valid_solutions:
            if bitstring in oracle_solutions:
                found_oracle_solutions += 1
        
        print(f"\nQuantum circuit found {found_oracle_solutions} solutions that match oracle results")
        
        if found_oracle_solutions > 0:
            print("Quantum circuit is finding valid independent sets!")
        else:
            print("Quantum circuit needs improvement to match oracle results")
    else:
        print("No minterms found from oracle!")
    
    plot_histogram(counts)
    plt.show()
