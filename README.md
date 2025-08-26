QSOP 
This is the github for the University of Tennesee Knoxville QAOA REU written by: 
- Matt Brunet
- Shilpi Shah
 
contributions by:
- Mostafa Atallah 
- Anthony Wilke 

under: Doctor Rebekah Herrman 

in: Summer 2024 

- Algorithms and examples for a graph to ESOP to Quantum Oracle for MIS.
- Familiarity with sympy is encouraged
- Algorithm explaination and theory in the associated paper and ESOP_ALT.py jupityer notebookss
- For best use, reserve a sole directory for this code, in order to preserve dependcies among files. 
- Examples are provided in the file's main functions and in ESOP_ALT.py

      oracle.py  -> Contains classes for taking .g6 graphs (in /xgraphFiles/) and formatting them for us
                 -> Also contains .getProbInstance(graph), which takes a formatted nx graph and outputs the MIS ESOP  
           
      oracle_and_bht_qaoa.py -> contains functions for converting classical ESOP to ESOP Hamiltonian, 
                                creating the QAOA circ, and running it. 
      
      qsop_custom_graphs_runner.py -> contains functions for creating and applying our ESOP QAOA to random, simply connected, graphs with nodes >=9,
      
      qsop_qaoa_nx_graphs.py -> contains functions for running MIS ESOP QAOA on the included networkx graphs
     
      regular_qaoa_MIS.py -> contains functions for running vanilla QAOA for MIS


