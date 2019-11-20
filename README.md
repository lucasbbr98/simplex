# simplex
It all started with a Simplex implementation, which evolved into a basic Linear Solver

## Getting Started

0. Importing models

```
from models.variable import Variable, VariableConstraint
from models.function import ObjectiveFunction, Constraint
from models.linear_model import LinearModel
from models.solver import LinearSolver
```

1. Writing a LinearModel

```
x1 = Variable(name='x1')
x2 = Variable(name='x2')

fo = ObjectiveFunction('max', [(3, x1), (5, x2)])
c1 = Constraint([(2, x1), (4, x2)], '<=', 25)
c2 = Constraint([(1, x1)], '<=', 8)
c3 = Constraint([(2, x2)], '<=', 10)

model = LinearModel(objective_function=fo, constraints_list=[c1, c2, c3])
```


2. Solving the LP

```
solver = LinearSolver(linear_model=model)
print(solver.solution)
```

### Extra Information

- Variables

```
x1 = Variable(name='x1')                                              # x1 > 0
x1 = Variable(name='x1', constraint=VariableConstraint.Positive)      # x1 > 0
x1 = Variable(name='x1', integer=True)                                # x1 Integer
x1 = Variable(name='x1', constraint=VariableConstraint.Unrestricted)  # x1 unrestricted
x1 = Variable(name='x1', constraint=VariableConstraint.Negative)      # x1 < 0
```

- ObjectiveFunction

```
# Can only recieve 'min' or 'max' values.
fo = ObjectiveFunction('max', [(3, x1), (5, x2)])
fo = ObjectiveFunction('min', [(3, x1), (5, x2)])
```

- Constraint

```
# Can only recieve '<=' or '>=' or '=' values.
c1 = Constraint([(2, x1), (4, x2)], '<=', 25)
c1 = Constraint([(2, x1), (4, x2)], '>=', 25)
c1 = Constraint([(2, x1), (4, x2)], '=', 25)
```

- Solver Information

The solver uses the two phase matricial simplex method.
In case you select a decision Variable to be an integer, the solver uses the Branch and Bound method

### Prerequisites

Python 3, numpy, math

## Running the tests

You can simply run the file to see the given output. The example is by the end of the file, and it starts on the function

```
if __name__ == '__main__':
```

## Contributing

Any contribution is very welcome to the project (Code, suggestions and even errors/bug reports). If you do wish to help, please contact me at: lucasbbr98@gmail.com


## Authors

* **Lucas Arruda Bonservizzi** - *Initial work* - [lucasbbr98](https://github.com/lucasbbr98)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Inspiration 1: I enjoyed an Operations Research class from professor Cleber Rocco at UNICAMP - FCA.
* Inspiration 2: Maybe my code can help someone around the world. 
* Feel free to contact me if you need any help at lucasbbr98@gmail.com.

