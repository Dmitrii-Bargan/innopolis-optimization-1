from enum import Enum
from typing import Union
from math import isclose


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
        MAXIMIZE = "Maximize"
        MINIMIZE = "Minimize"

    def __init__(self, mode: Mode, c: list[float], a: list[list[float]], b: list[float], eps: int) -> None:
        """
        Construct a Simplex method problem solver

        :param mode: one of [Mode.MAXIMIZE] or [Mode.MINIMIZE]
        :param c: coefficients of the objective function
        :param a: matrix of the coefficients of the constraints
        :param b: right hand side of the constraints equations
        :param eps: solution accuracy. How many digits after the floating point to consider
        """

        self.mode: SimplexSolver.Mode = mode
        """Mode of this problem solver"""

        self.actual_coefficients: list[float] = c
        """Coefficients of the objective function regardless of whether we are maximizing or minimizing"""

        self.c: list[float] = c if mode == SimplexSolver.Mode.MAXIMIZE else [-j for j in c]
        """Coefficients of the objective function. Inverted if we are minimizing"""

        self.a: list[list[float]] = a
        """Matrix of the coefficients of the constraints"""

        self.b: list[float] = b
        """Right hand side of the constraints equations"""

        self.eps: int = eps
        """Solution accuracy"""

        self.base: list[int] = []
        """Indices of basic variables on this step"""

        self.solution = 0
        """Optimal solution for this problem"""

        self.z = [-i for i in self.c]
        """Z-row of the tableau"""

        self.is_unbounded = False
        """Whether the objective function is unbounded"""

    def print_problem(self) -> None:
        """
        Print the simplex problem of this solver
        """
        print(f"{self.mode} z = {function_from_coefficients(self.actual_coefficients)}")
        print("subject to the constraints:")
        print("\n".join(f"{function_from_coefficients(cs)} <= {rhs}" for cs, rhs in zip(self.a, self.b)))

    def _to_standard_form(self) -> None:
        """
        Builds the tableau adding 1's and 0's for every slack variable
        """
        for row in range(len(self.a)):
            for row2 in range(len(self.a)):
                self.a[row2].append(1 if row == row2 else 0)

            self.base.append(-1)  # Put -1 for slack variables in the basic variables column
            self.z.append(0)  # Slack variables have a "zero" coefficient in the objective function

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
                    if self.a[i][pivot_column] != 0 and self.b[i] / self.a[i][pivot_column] > 0),
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

    def _step(self) -> bool:
        """
        Perform one iteration of the Simplex method
        :return: whether to continue iterating. [False] if this was the last step
        """

        # Get the index of the pivot column
        pivot_column = self._pivot_column()

        if pivot_column is None:  # If all columns are positive or zero, we are done
            return False

        if self._check_unbounded(pivot_column):  # if the column is unbounded we do not need to calculate further
            self.is_unbounded = True
            return False

        pivot_row = self._pivot_row(pivot_column)
        if pivot_row is None:  # If all ratios on this step are negative or zero, we stop
            return False

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
        return True

    def solve(self) -> Union[tuple[float, list[float]], None]:
        """
        Solve the problem in this solver and print the solution and X*,
        or "Unbounded" if the objective function is unbounded
        :return: a tuple (solution, X*) or [None] if the objective function is unbounded
        """
        self._to_standard_form()
        while self._step():
            pass

        # Find X* from base
        x = [0] * len(self.c)
        for i in range(len(self.base)):
            if self.base[i] != -1:
                x[self.base[i]] = self.b[i]

        if not self.is_unbounded:
            if self.mode == SimplexSolver.Mode.MINIMIZE:  # Flip the solution in case we were minimizing
                self.solution *= -1

            print("Solution: ", self.solution)
            print("X* = ", x)
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

    if solutions is None:  # Unbounded function
        if expected_solution is not None:
            raise ArithmeticError("Expected an unbounded function")
    else:
        if solutions[0] != expected_solution:
            raise ArithmeticError(f"Expected solution {expected_solution}, got {solutions[0]}")

        answer = 0
        for i in range(len(objective_function)):
            answer += objective_function[i] * solutions[1][i]

        if not isclose(answer, expected_solution, rel_tol=10**(-epsilon)):
            raise ArithmeticError("X* coefficients do not produce expected solution")

        for i in range(len(constraints_right_hand_side)):
            calculated = sum([constraints_matrix[i][j] * solutions[1][j] for j in range(len(solutions[1]))])
            if calculated > constraints_right_hand_side[i]:
                raise ArithmeticError(f"Produced X* does not match {i}-th constraint")
