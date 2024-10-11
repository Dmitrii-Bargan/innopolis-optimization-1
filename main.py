from enum import Enum
from typing import Union


def show_function_from_cs(cs):
    if not cs:
        return ""
    h, *t = cs
    return f"{h} * x1" + "".join(f"{' - ' if c < 0 else ' + '}{abs(c)} * x{i}"
                                 for i, c in enumerate(t, start=2))


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
        self.c = c
        self.a = a
        self.b = b
        self.eps = eps
        self.base = []
        self.solution = 0
        self.z = [-i for i in c]
        self.isUnbounded = False

    def print_problem(self) -> None:
        """
        Print the simplex problem of this solveer
        """
        print(f"{self.mode} z = {show_function_from_cs(self.c)}")
        print("subject to the constraints:")
        print("\n".join(f"{show_function_from_cs(cs)} <= {rhs}" for cs, rhs in zip(self.a, self.b)))

    def _to_standard_form(self):
        for row in range(len(self.a)):
            if 1 not in self.a[row]:
                for row2 in range(len(self.a)):
                    self.a[row2].append(1 if row == row2 else 0)
                # slack variables are denoted by 0
                self.base.append(-1)
                self.z.append(0)
            else:
                self.base.append(self.a[row].index(1))

    def _pivot_column(self):
        r = min(((i, self.z[i])
                 for i in range(len(self.z))
                 if self.z[i] < 0),
                default=None,
                key=lambda x: x[1])
        if r:
            return r[0]
        else:
            return r

    def _pivot_row(self, col):
        r = min(((i, self.b[i] / self.a[i][col])
                 for i in range(len(self.a))
                 if self.b[i] / self.a[i][col] > 0),
                default=None,
                key=lambda x: x[1])
        if r:
            return r[0]
        else:
            return r

    def _check_unbounded(self, col):
        return all(self.a[i][col] <= 0 for i in range(len(self.a)))

    def _step(self):
        c = self._pivot_column()
        if c is None:
            return None
        if self._check_unbounded(c):
            self.isUnbounded = True
            return None
        r = self._pivot_row(c)
        if r is None:
            return None
        k = self.a[r][c]
        self.base[r] = c

        # target row
        for col in range(len(self.a[r])):
            self.a[r][col] /= k
            self.a[r][col] = round(self.a[r][col], self.eps)
        self.b[r] /= k
        self.b[r] = round(self.b[r], self.eps)

        # set base variable
        self.base

        # subtract from all other values multiplication of two values(from pivot row and pivot column corresponding values)
        for row in range(len(self.a)):
            # skip the target row
            if row == r:
                continue
            m = self.a[row][c] / self.a[r][c]
            m = round(m, self.eps)
            for col in range(len(self.a[row])):
                self.a[row][col] -= m * self.a[r][col]
                self.a[row][col] = round(self.a[row][col], self.eps)
            self.b[row] -= m * self.b[r]
            self.b[row] = round(self.b[row], self.eps)

        # for obj function
        m = self.z[c]
        for col in range(len(self.z)):
            self.z[col] -= m * self.a[r][col]
            self.z[col] = round(self.z[col], self.eps)

        self.solution -= m * self.b[r]
        return 1

    def solve(self) -> Union[tuple[float, list[float]], None]:
        """
        Solve the problem in this solver and print the solution and X*,
        or "Unbounded" if the objective function is unbounded
        :return: a tuple (solution, X*) or [None] if the objective function is unbounded
        """
        self._to_standard_form()
        while True:
            if self._step() is None:
                break

        # finding x* from base
        x = [0] * len(self.c)
        for i in range(len(self.base)):
            if self.base[i] != -1:
                x[self.base[i]] = self.b[i]
        if not self.isUnbounded:
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

    if solutions is None:  # Unbounded function
        assert expected_solution is None
    else:
        assert solutions[0] == expected_solution

        answer = 0
        for i in range(len(objective_function)):
            answer += objective_function[i] * solutions[1][i]

        assert answer == expected_solution


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
        objective_function= [2, 3],
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
