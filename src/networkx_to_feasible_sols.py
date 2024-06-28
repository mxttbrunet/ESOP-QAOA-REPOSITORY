import networkx as nx

def vertex_cover(graph, verts):
    covered_edges = set()
    for v in verts:
        for neighbor in graph.neighbors(v):
            covered_edges.add(frozenset((v, neighbor)))
    return len(covered_edges) == graph.number_of_edges()

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

def find_feasible_sols(graph):
    nodes = list(graph.nodes())
    subset = subsets(nodes)
    feasible_sols = []
    for s in subset:
        if vertex_cover(graph, s):
            bin_sol = [1 if node in s else 0 for node in nodes] # convert output in terms of num of vertices to its binary form
            feasible_sols.append(bin_sol)

    return feasible_sols

if __name__ == '__main__':
    G = nx.Graph()
    G.add_edges_from([(1,2),(2,3),(2,4),(3,5),(4,5),(2,5)]) # example graph
    feasible_cover = find_feasible_sols(G)

    for sol in feasible_cover:
        print(sol)
