from simplex_solver import SimplexSolver, simplex_solve_and_check


def main() -> None:
    print("Example 1")
    simplex_solve_and_check(
        mode=SimplexSolver.Mode.MAXIMIZE,
        objective_function=[9, 10, 16],
        constraints_matrix=[
            [18, 15, 12],
            [6, 4, 8],
            [5, 3, 3]
        ],
        constraints_right_hand_side=[360, 192, 180],
        epsilon=5,
        expected_solution=400
    )

    print()
    print("--> Example 2. An unbounded objective function")
    simplex_solve_and_check(
        mode=SimplexSolver.Mode.MAXIMIZE,
        objective_function=[5, 4],
        constraints_matrix=[
            [1, 0],
            [1, -1]
        ],
        constraints_right_hand_side=[7, 8],
        epsilon=5,
        expected_solution=None
    )

    print()
    print("--> Example 3. Another unbounded function")
    simplex_solve_and_check(
        mode=SimplexSolver.Mode.MAXIMIZE,
        objective_function=[5, 4],
        constraints_matrix=[
            [1, -1],
            [1, 0]
        ],
        constraints_right_hand_side=[8, 7],
        epsilon=5,
        expected_solution=None
    )

    print()
    print("--> Example 4")
    simplex_solve_and_check(
        mode=SimplexSolver.Mode.MAXIMIZE,
        objective_function=[1, 2, 3],
        constraints_matrix=[
            [1, 1, 1],
            [2, 1, 1],
        ],
        constraints_right_hand_side=[10, 20],
        epsilon=5,
        expected_solution=30
    )

    print()
    print("--> Example 5 - An unbounded function. Taken from lab 5.1, task 2")
    simplex_solve_and_check(
        mode=SimplexSolver.Mode.MAXIMIZE,
        objective_function=[2, 3],
        constraints_matrix=[
            [4, -2],
            [-1, -1]
        ],
        constraints_right_hand_side=[-4, -6],
        epsilon=5,
        expected_solution=None
    )

    print("--> Example 6 - More variables. Taken from lab 2, task 1")
    simplex_solve_and_check(
        mode=SimplexSolver.Mode.MAXIMIZE,
        objective_function=[100, 140, 120],
        constraints_matrix=[
            [3, 6, 7],
            [2, 1, 8],
            [1, 1, 1],
            [5, 3, 3]
        ],
        constraints_right_hand_side=[135, 260, 220, 360],
        epsilon=5,
        expected_solution=4500
    )


if __name__ == "__main__":
    main()
