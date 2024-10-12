from simplex_solver import SimplexSolver


def main() -> None:
    print("Apply simplex method to your own problem! 💫")

    while True:
        print("Minimization or maximization problem?")
        mode_string = input("[min|max]: ").strip().lower()
        if mode_string == 'min':
            mode = SimplexSolver.Mode.MINIMIZE
            break
        elif mode_string == 'max':
            mode = SimplexSolver.Mode.MAXIMIZE
            break
        else:
            print("Wrong input...")

    coefficients = [float(x) for x in input("Enter objective function coefficients (space-separated): ").strip().split(' ')]

    print("Constraints are given in the form: a * x_a + b * x_b + ... <= rhs_i")
    n = int(input("Enter number of constraints: "))
    print("Enter coefficients of constraints (space-separated):")
    constraints = [[float(x) for x in input(f"Constraint {i}: ").strip().split(' ')] for i in range(n)]

    print("Enter constraints rights hand side, space-separated: ")
    rhs = [float(x) for x in input().split(' ')]

    epsilon_string = input("Enter optimization accuracy (default is 5): ")
    epsilon = float(epsilon_string) if epsilon_string != '' else 5

    print()
    solver = SimplexSolver(mode, coefficients, constraints, rhs, epsilon)
    solver.print_problem()
    solver.solve()


if __name__ == '__main__':
    main()
