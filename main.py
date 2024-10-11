
def show_function_from_cs(cs):
    if not cs:
        return ""
    h, *t = cs
    return f"{h} * x1" + "".join(f"{' - ' if c < 0 else ' + '}{abs(c)} * x{i}"
                                 for i, c in enumerate(t, start=2))
class simplex:
    MODE_MAXIMIZE = "max"
    MODE_MINIMIZE = "min"

    def init(self, mode, c, a, b, eps):
        if mode not in {self.MODE_MAXIMIZE, self.MODE_MINIMIZE}:
            raise Exception(f"Unknown mode: {mode}")
        self.mode = mode
        self.c = c
        self.a = a
        self.b = b
        self.eps = eps
        self.base = []
        self.solution = 0
        self.z = [-i for i in c]
        self.isUnbounded = False

    def print_problem(self):
        print(f"{self.mode} z = {show_function_from_cs(self.c)}")
        print("subject to the constraints:")
        print("\n".join(f"{show_function_from_cs(cs)} <= {rhs}" for cs, rhs in zip(self.a, self.b)))

    def to_standard_form(self):
        for row in range(len(self.a)):
            if 1 not in self.a[row]:
                for row2 in range(len(self.a)):
                    self.a[row2].append(1 if row == row2 else 0)
                # slack variables are denoted by 0
                self.base.append(-1)
                self.z.append(0)
            else:
                self.base.append(self.a[row].index(1))

    def pivot_column(self):
        r = min(((i, self.z[i])
                 for i in range(len(self.z))
                 if self.z[i] < 0),
                default=None,
                key=lambda x: x[1])
        if r:
            return r[0]
        else:
            return r

    def pivot_row(self, col):
        r = min(((i, self.b[i] / self.a[i][col])
                 for i in range(len(self.a))
                 if self.b[i] / self.a[i][col] > 0),
                default=None,
                key=lambda x: x[1])
        if r:
            return r[0]
        else:
            return r
    def checkUnbounded(self, col):
        return all(self.a[i][col]  <= 0 for i in range (len(self.a)))

    def step(self):
        c = self.pivot_column()
        if c is None:
            return None
        if self.checkUnbounded(c):
            self.isUnbounded = True
            return None
        r = self.pivot_row(c)
        if r is None:
            return None
        k = self.a[r][c]
        self.base[r ] =c

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
            self.z[col ]-= m *self.a[r][col]
            self.z[col] = round(self.z[col], self.eps)

        self.solution -= m * self.b[r]
        return 1

    def solve(self):
        self.to_standard_form()
        while True:
            if self.step() is None:
                break

        # finding x* from base
        x = [0] * len(self.c)
        for i in range(len(self.base)):
            if self.base[i] != -1:
                x[self.base[i]] = self.b[i]
        if self.isUnbounded == False:
            print("Solution:", self.solution)
            print("x* =", x)
        else:
            print("Unbounded")
if __name__ == "__main__":
    pass

#ex1
solver = simplex()
objective_function = [9, 10, 16]  # целевая функция
constraints_matrix = [
    [18, 15, 12],
    [6, 4, 8],
    [5, 3, 3]
]

constraints_rhs = [360, 192, 180]
epsilon = 5
solver.init(solver.MODE_MAXIMIZE, objective_function, constraints_matrix, constraints_rhs, epsilon)
solver.print_problem()
print()
solver.solve()

print()
#ex2
solver = simplex()
objective_function = [5, 4]  # целевая функция
constraints_matrix = [
    [1,0],
    [1, -1]
]

constraints_rhs = [7, 8]
epsilon = 5
solver.init(solver.MODE_MAXIMIZE, objective_function, constraints_matrix, constraints_rhs, epsilon)
solver.print_problem()
print()
solver.solve()

print()
#ex3
solver = simplex()
objective_function = [5, 4]  # целевая функция
constraints_matrix = [
    [1,-1],
    [1, 0]
]

constraints_rhs = [8, 7]
epsilon = 5
solver.init(solver.MODE_MAXIMIZE, objective_function, constraints_matrix, constraints_rhs, epsilon)
solver.print_problem()
print()
solver.solve()

#ex4
solver = simplex()
objective_function = [1, 2, 3]  # целевая функция
constraints_matrix = [
    [1,1, 1],
    [2, 1, 1],
]

constraints_rhs = [10, 20]
epsilon = 5
solver.init(solver.MODE_MAXIMIZE, objective_function, constraints_matrix, constraints_rhs, epsilon)
solver.print_problem()
print()
solver.solve()

