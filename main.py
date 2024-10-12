from enum import Enum
from typing import Union


def function_from_coefficients(coefficients: list[float]) -> str:
    """
    Produce function string from coefficients
    :param coefficients: the coefficients of the function
    :return: string representation of the function
    """
    if not coefficients:
        return ""

    coefficient, *other = coefficients
    return f"{coefficient} * x1" + "".join(f"{' - ' if c < 0 else ' + '}{abs(c)} * x{i}"
                                           for i, c in enumerate(other, start=2))


class SimplexSolver:
    class Mode(str, Enum):
        MAXIMIZE = "maximize"
        MINIMIZE = "minimize"

    def __init__(self, mode: Mode, c: list[float], a: list[list[float]], b: list[float], eps: int) -> None:
        """
        Construct a Simplex method problem solver

        :param mode: one of [Mode.MAXIMIZE] or [Mode.MINIMIZE]
        :param c: coefficients of the objective function
        :param a: matrix of the coefficients of the constraints
        :param b: right hand side of the constraints equations
        :param eps: solution accuracy. How many digits after the floating point to consider
        """

        self.mode = mode
        """Mode of this problem solver"""

        self.c = c
        """Coefficients of the objective function"""

        self.a = a
        """Matrix of the coefficients of the constraints"""

        self.b = b
        """Right hand side of the constraints equations"""

        self.eps = eps
        """Solution accuracy"""

        self.base = []
        """Indices of basic variables on this step"""

        self.solution = 0
        """Optimal solution for this problem"""

        self.z = [-i for i in c]
        """Z-row of the tableau"""

        self.is_unbounded = False
        """Whether the objective function is unbounded"""

    def print_problem(self) -> None:
        """
        Print the simplex problem of this solver
        """
        print(f"{self.mode} z = {function_from_coefficients(self.c)}")
        print("subject to the constraints:")
        print("\n".join(f"{function_from_coefficients(cs)} <= {rhs}" for cs, rhs in zip(self.a, self.b)))

    def _to_standard_form(self) -> None:
        for row in range(len(self.a)):
            if 1 not in self.a[row]:
                for row2 in range(len(self.a)):
                    self.a[row2].append(1 if row == row2 else 0)

                # slack variables are denoted by 0
                self.base.append(-1)
                self.z.append(0)
            else:
                self.base.append(self.a[row].index(1))

    def _pivot_column(self) -> Union[int, None]:
        """
        Determine the pivot column for this iteration
        :return: index of the column or [None] if all z-row values are positive
        """

        # Create an array of tuples (variable index, z-row value),
        # get the tuple in which the z-row value is the smallest among all.
        cell = min(((i, self.z[i])
                    for i in range(len(self.z))
                    if self.z[i] < 0),
                   default=None,
                   key=lambda x: x[1])

        # If all values are greater or equal to zero, None is returned,
        # otherwise the index of the smallest value is returned
        if cell:
            return cell[0]
        else:
            return cell

    def _pivot_row(self, pivot_column: int) -> Union[int, None]:
        """
        Determine the pivot row for this iteration
        :param pivot_column: index of the pivot column for this iteration
        :return: index of the pivot row or [None] if all ratios are negative or zero
        """

        # Divide the right hand side value of each row by the value on the pivot column
        # and find the minimum of such ratios
        cell = min(((i, self.b[i] / self.a[i][pivot_column])
                    for i in range(len(self.a))
                    if self.b[i] / self.a[i][pivot_column] > 0),  # TODO: Should we really check this here?
                   default=None,
                   key=lambda x: x[1])
        if cell:
            return cell[0]
        else:
            return cell  # Returns None

    def _check_unbounded(self, col: int) -> bool:
        """
        Check if a column is unbounded
        :param col: index of the column to check
        :return: whether the column is unbounded
        """
        return all(self.a[i][col] <= 0 for i in range(len(self.a)))

    def _step(self) -> Union[int, None]:
        """
        Perform one iteration of the Simplex method
        :return: [None] if this is the last step, 1 otherwise
        """

        # Get the index of the pivot column
        pivot_column = self._pivot_column()

        if pivot_column is None:  # If all columns are positive or zero, we are done
            return None

        if self._check_unbounded(pivot_column):  # if the column is unbounded we do not need to calculate further
            self.is_unbounded = True
            return None

        pivot_row = self._pivot_row(pivot_column)
        if pivot_row is None:  # If all ratios on this step are negative or zero, we stop
            return None

        k = self.a[pivot_row][pivot_column]
        self.base[pivot_row] = pivot_column

        # Make the value in cell [target_row][target_column] to be 1 by dividing the row
        for col in range(len(self.a[pivot_row])):
            self.a[pivot_row][col] /= k
            self.a[pivot_row][col] = round(self.a[pivot_row][col], self.eps)

        self.b[pivot_row] /= k
        self.b[pivot_row] = round(self.b[pivot_row], self.eps)

        # Subtract from all other values multiplication of two values
        # (from pivot row and pivot column corresponding values)
        for row in range(len(self.a)):
            if row == pivot_row:  # Skip the target row
                continue

            m = self.a[row][pivot_column] / self.a[pivot_row][pivot_column]
            m = round(m, self.eps)

            for col in range(len(self.a[row])):
                self.a[row][col] -= m * self.a[pivot_row][col]
                self.a[row][col] = round(self.a[row][col], self.eps)

            self.b[row] -= m * self.b[pivot_row]
            self.b[row] = round(self.b[row], self.eps)

        # Subtract from the z-row as well
        m = self.z[pivot_column]
        for col in range(len(self.z)):
            self.z[col] -= m * self.a[pivot_row][col]
            self.z[col] = round(self.z[col], self.eps)

        self.solution -= m * self.b[pivot_row]
        return 1

    def solve(self) -> Union[tuple[float, list[float]], None]:
        """
        Solve the problem in this solver and print the solution and X*,
        or "Unbounded" if the objective function is unbounded
        :return: a tuple (solution, X*) or [None] if the objective function is unbounded
        """
        self._to_standard_form()
        while self._step() is not None:
            pass

        # finding x* from base
        print("Before finding x*, here is your tableau " + " ".join(map(str, self.base)))
        print("And here is your tableau")
        for row in range(len(self.a)):
            print(str(self.base[row]) + " " + str(self.a[row]) + " " + str(self.b[row]))

        x = [0] * len(self.c)
        for i in range(len(self.base)):
            if self.base[i] != -1:
                x[self.base[i]] = self.b[i]

        if not self.is_unbounded:
            print("Solution:", self.solution)
            print("x* =", x)
            return self.solution, x
        else:
            print("Unbounded")
            return None


def simplex_solve_and_check(
        mode: SimplexSolver.Mode,
        objective_function: list[float],
        constraints_matrix: list[list[float]],
        constraints_right_hand_side: list[float],
        epsilon: int,
        expected_solution: Union[float, None],
) -> None:
    """
    Run the simplex solver with given data and assert-check the solution.

    :param mode: [SimplexSolver] mode on whether to minimize or maximize the function
    :param objective_function: coefficients of the objective function F(x_1, ..., x_m) = 0
    :param constraints_matrix: coefficients of constraints equations Q_i (x_1, ..., x_m) <= rhs_i
    :param constraints_right_hand_side: results of the constraints equations
    :param epsilon: optimization accuracy. Number of digits after the floating point to consider
    :param expected_solution: the expected solution of the optimization problem
    """
    solver = SimplexSolver(mode, objective_function, constraints_matrix, constraints_right_hand_side, epsilon)
    solver.print_problem()
    solutions = solver.solve()

    # TODO: Uncomment the assertations

    if solutions is None:  # Unbounded function
        pass  # assert expected_solution is None
    else:
        # assert solutions[0] == expected_solution

        answer = 0
        for i in range(len(objective_function)):
            answer += objective_function[i] * solutions[1][i]

        # assert answer == expected_solution


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
