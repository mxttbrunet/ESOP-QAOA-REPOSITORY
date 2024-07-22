#include "easy.hpp"
#include <vector> 
#include <iostream>
#include <fstream>       //library includes
#include<string>
using namespace std;
using namespace kitty;
using namespace easy;      //namespace for encapsulation
using namespace esop;


int main(){
string vars,mins;
ifstream input;

input.open("between.txt");              //open data file 


vector<cube> listOfMinterms; 

input >> vars;
int numVars = stoi(vars);        //get number of variables from file

input >> mins;
int numMinterms = stoi(mins);


string minterm;

for(int i = 0; i < numMinterms; i++){
	input >> minterm;
	cube cuber = *(new cube(minterm));    //collect minterms in kitty::cube vector for truth table
	listOfMinterms.push_back(cuber);      


}

input.close();

dynamic_truth_table tTbl = dynamic_truth_table(numVars);  

create_from_cubes(tTbl, listOfMinterms, true);       //create truth table with n number of variables


vector<cube> posEsop;
vector<cube> mixEsop; 
posEsop = esop_from_pprm(tTbl);                       //positive polarity ESOP
print_cubes(posEsop, numVars, cout); 

cout << "D\n";

mixEsop = esop_from_optimum_pkrm(tTbl);                  //mixed polarity ESOP
print_cubes(mixEsop, numVars, cout);


return 0;

}
