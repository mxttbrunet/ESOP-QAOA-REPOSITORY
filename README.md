QSOP 


credit to the easy c++ library; their license is in any code used. 
This is the github for the University of Tennesee Knoxville QAOA REU written by:  
- Matt Brunet
- Shilpi Shah
 
contributions by:
- Mostafa Atallah 
- Anthony Wilke 

under: Doctor Rebekah Herrman 

in: Summer 2024 
-------------------------------------------
Algorithms and examples for a graph to ESOP to Quantum Oracle for MIS and MVC.
Familiarity with sympy is encouraged
For best use, reserve a sole directory for this code, in order to preserve dependcies among files. 
examples are provided

Usage:     oracle.py  -> Contains classes for taking .g6 graphs (in /xgraphFiles/) and implementing the Boolean constraints, along with functions for getting the Truthtables and extractiing the minterms. 
                      -> Method to generate esops from Easy (license and fair use included in code) c++ library using a python wrapper 
           
           sympy_to_qcircuit.py -> contains classes for translatng esops to quantum oracles 
                                -> methods to run gm-qaoa as well 
                                
