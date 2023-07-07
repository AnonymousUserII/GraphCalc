from multiprocessing import Pool
from math import *
from numpy import linspace

INVALID: tuple = None, None


def gamma_shift(x) -> float:
    """
    i.e. The factorial function
    Shifts the gamma function left by one because gamma function is factorial(x - 1)
    """
    return gamma(x + 1)


# Create a function dictionary to allow eval to work
funcs: tuple = ("sin", "cos", "tan", "sqrt", "asin", "acos", "atan", "fabs", "log", "log10", "gamma", "gamma_shift")
eval_dict: dict = {}
for func in funcs:
    eval_dict[func] = locals().get(func)


def format_equation(equation: str, m: float, n: float) -> tuple[str, str]:
    """
    Turns an equation from a string and formats its constants and functions to be Python-readable
    """
    # Replace constants
    temp: str = equation.replace('x', "(x)").replace('y', "(y)")
    temp = temp.replace("log", "log10").replace("ln", "log") \
                .replace("fact", "factorial").replace("factorial", "gamma_shift")\
                .replace("csc", "1/sin").replace("cosec", "1/sin") \
                .replace("sec", "1/cos").replace("cot", "1/tan") \
                .replace("arcsin", "asin").replace("arccos", "acos").replace("arctan", "atan") \
                .replace("abs", "fabs").replace('^', "**").replace(")(", ")*(") \
                .replace("$m", f"({m})").replace("$n", f"({n})").replace('e', f"({e})").replace("pi", f"({pi})")
    
    # Multiply coefficients in terms, including functions
    # e.g. 2x = 2 * x, 10sinx = 10*sin(x)
    for function in funcs + ('(', "sec", "csc", "cosec", "cot" + "ln"):
        for i in range(10):  # All digits 0..9
            temp = temp.replace(f"{i}{function}", f"{i}*{function}")
    
    # Replace the names of some functions with the names the graph uses
    # e.g. log -> log of base 10, ln -> log of base e
    return tuple(temp.split('='))


def test_for_intercept(info_pack: tuple[str, str, tuple[float, float], float, float]) -> tuple[float, float]:
    """
    Test if function passes through each pixel
    """
    lhs, rhs, coordinate, x_tol, y_tol = info_pack
    x_, y_ = coordinate

    std_form: str = f"{lhs} - ({rhs})"  # Turn into an equation equal to zero

    try:
        tl: float = eval(std_form.strip().replace('x', str(x_ - x_tol)).replace('y', str(y_ + y_tol)), {}, eval_dict)
        tr: float = eval(std_form.strip().replace('x', str(x_ + x_tol)).replace('y', str(y_ + y_tol)), {}, eval_dict)
        bl: float = eval(std_form.strip().replace('x', str(x_ - x_tol)).replace('y', str(y_ - y_tol)), {}, eval_dict)
        br: float = eval(std_form.strip().replace('x', str(x_ + x_tol)).replace('y', str(y_ - y_tol)), {}, eval_dict)
        pixel_corners: tuple = tl, tr, bl, br

        low, high = min(pixel_corners), max(pixel_corners)
        if high >= 0 and low <= 0:  # There is an intersection
            return coordinate
    except (ArithmeticError, ValueError, TypeError, OverflowError, SyntaxWarning):
        pass
    
    # If there is no intersect or point gives an error
    return INVALID


def generate_plot_points(info_packs: tuple[tuple]) -> list[tuple[float, float]]:
    with Pool(processes=4) as pool:
        plot_points: list[tuple[float, float]] = list(pool.map(test_for_intercept, info_packs))
    
    # Remove points not on graph (remove all INVALIDs from this list)
    for _ in range(plot_points.count(INVALID)):
        plot_points.remove(INVALID)
    return plot_points


def generate_iterative_plots(equation: tuple[str, str], x_bounds, y_bounds, ranges, resolution) -> tuple[tuple]:
    """
    Generates the
    """
    lhs, rhs = equation
    x_tol, y_tol = ranges[0] / resolution[0] * 0.5, ranges[1] / resolution[1] * 0.5

    # Generate information for computation of plotted points
    # i.e. equation, coordinates to be iterated, tolerances
    info_packs: list[tuple] = []
    for x in linspace(x_bounds[0], x_bounds[1], num=resolution[0]):
        for y in linspace(y_bounds[0], y_bounds[1], num=resolution[1]):
            info_packs.append((lhs, rhs, (x, y), x_tol, y_tol))
    
    if x_bounds[0] < 0 < x_bounds[1]:  # Then add points on x = 0
        for y in linspace(y_bounds[0], y_bounds[1], num=resolution[1]):
            info_packs.append((lhs, rhs, (0, y), x_tol, y_tol))
    if y_bounds[0] < 0 < y_bounds[1]:  # Then add points on y = 0
        for x in linspace(x_bounds[0], x_bounds[1], num=resolution[0]):
            info_packs.append((lhs, rhs, (x, 0), x_tol, y_tol))
    
    return tuple(info_packs)
