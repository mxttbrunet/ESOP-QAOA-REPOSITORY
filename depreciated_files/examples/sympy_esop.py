import sympy as sp

# function to input the truth table and corresponding truth values
def input_truth_table(input_num):
    truth_table_init = []
    for i in range(2**input_num):
        vals = list(map(int, input(f"Enter values for each variable separated by spaces for row {i + 1}: ").split()))
        result = int(input(f"Enter result for row {i + 1}: ")) # can change this in future to automate results based on operation
        truth_table_init.append((*vals, result))
    print("Truth table:", truth_table_init)
    return truth_table_init

# function to find the ESOP function
def find_ESOP_fxn(tt, vars):
    terms = []
    for row in tt:
        vals, result = row[:-1], row[-1]
        if result == 1:
            terms_new = []
            for i, var in enumerate(vars):
                if vals[i] == 0:
                    terms_new.append(~var)
                else:
                    terms_new.append(var)
            terms.append(sp.And(*terms_new))
    return sp.Xor(*terms)

# function to optimize the ESOP expression
def optimize_ESOP(ESOP):
    return sp.simplify_logic(ESOP, form='dnf')

def main():
    num_vars = int(input("Enter the number of variables: "))
    vars = sp.symbols(' '.join(f'x{i}' for i in range(num_vars)))
    truth_table = input_truth_table(num_vars)
    ESOP = find_ESOP_fxn(truth_table, vars)
    print("Exclusive Sum of Products (ESOP):", ESOP)
    ESOP_optimized = optimize_ESOP(ESOP)
    print("Optimized Exclusive Sum of Products:", ESOP_optimized)

if __name__ == "__main__":
    main()
