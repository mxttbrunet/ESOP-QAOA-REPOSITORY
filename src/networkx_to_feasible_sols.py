import networkx as nx
import matplotlib.pyplot as plt 

def vertex_cover(graph, verts): # max k vertex cover problem
    covered_edges = set()
    for v in verts:
        for neighbor in graph.neighbors(v):
            covered_edges.add(frozenset((v, neighbor)))
    return len(covered_edges) == graph.number_of_edges()

def ind_set(graph, verts): # max independent sets
    for v in verts:
        for neighbor in graph.neighbors(v):
            if neighbor in verts:
                return False
    return True

def k_col(graph, k): # max k colorable
    nodes = list(graph.nodes())
    cols = []
    curr_cols = {}

    def back(node): # recursive
        nonlocal cols, curr_cols
        if node == len(nodes):
            cols.append(curr_cols.copy())
            return

        for col in range(k):
            if check_valid(graph, curr_cols, nodes[node], col):
                curr_cols[nodes[node]] = col
                back(node + 1)
                del curr_cols[nodes[node]]

    back(0)
    return cols

def check_valid(graph, coloring, node, col): # helper for max k colorable
    for neighbor in graph.neighbors(node):
        if neighbor in coloring and coloring[neighbor] == col:
            return False
    return True
    
def subsets(nodes, i=0, current_set=None, all_sets=None):
    if current_set is None:
        current_set = []
    if all_sets is None:
        all_sets = []
    if i == len(nodes):
        all_sets.append(current_set.copy())
        return all_sets

    current_set.append(nodes[i]) # include current node
    subsets(nodes, i + 1, current_set, all_sets)

    current_set.pop() # exclude current node
    subsets(nodes, i + 1, current_set, all_sets)

    return all_sets

def find_feasible_sols(graph, problem_type='vc', k=None):
    nodes = list(graph.nodes())
    subset = subsets(nodes)
    feasible_vc = []
    feasible_is = []
    feasible_kc = []

    if problem_type == 'vc': # find vertex cover
        for s in subset:
            if vertex_cover(graph, s):
                bin_sol = [1 if node in s else 0 for node in nodes]
                feasible_vc.append(bin_sol)
        return feasible_vc

    elif problem_type == 'is': # find mis
        for s in subset:
            if ind_set(graph, s):
                bin_sol = [1 if node in s else 0 for node in nodes]
                feasible_is.append(bin_sol)
        return feasible_is

    elif problem_type == 'kc' and k is not None:
        cols = k_col(graph, k)
        for c in cols:
            bin_sol = [c[node] for node in nodes]
            feasible_kc.append(bin_sol)
        return feasible_kc
    else:
        raise ValueError("Unsupported problem type. Use 'vc' for vertex cover, 'is' for max independent sets, or 'kc' for k-colorable.")
        
    # for s in subset:
    #     if vertex_cover(graph, s):
    #         bin_sol = [1 if node in s else 0 for node in nodes] # convert output in terms of num of vertices to its binary form
    #         feasible_sols.append(bin_sol)

    # return feasible_sols

if __name__ == '__main__':
    G = nx.Graph()
    G.add_edges_from([(1,2), (1,4), (2,3), (3,4)]) # example graph
    # nx.draw(G, with_labels=True)
   # plt.show()

    # example outputs
    feasible_vc = find_feasible_sols(G, problem_type='vc')
    feasible_is = find_feasible_sols(G, problem_type='is')
    feasible_kc = find_feasible_sols(G, problem_type='kc', k=3) # example value

    # print vertex cover
    print("Max K-Vertex Cover: ")
    for sol in feasible_vc:
        print(sol)

    # print MIS
    print("\nMax Independent Sets: ")
    for sol in feasible_is:
        print(sol)

    # print k colorable
    print("\nMax K-Colorable: ")
    for sol in feasible_kc:
        print(sol)
