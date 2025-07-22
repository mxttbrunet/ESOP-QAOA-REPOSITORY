#include "easy.hpp"
#include <vector> 
#include <iostream>
#include <fstream>       //library includes
#include <string>
using namespace std;
using namespace kitty;
using namespace easy;      //namespace for encapsulation
using namespace esop;


int main(){
string vars,mins;
ifstream input("ESOPsimple/between.txt"); //change back to ESOPsimple/between.txt

if(input.fail()){
	cout << "file's fricked mate... just quit...";
}
vector<cube> listOfMinterms; 
getline(input,vars);
//test
//cout << "bruh " << vars << '\n';
int numVars = stoi(vars, nullptr);        //get number of variables from file

getline(input,mins);
int numMinterms = stoi(mins.c_str(), nullptr);


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
