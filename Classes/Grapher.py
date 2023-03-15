from os import path
from math import *
from numpy import linspace, arange
from time import sleep

import pygame

from Classes.Text import Text
from Scripts.GraphUtilities import generate_plot_points, gamma_shift, format_equation, generate_iterative_plots
from Scripts.NumberUtilities import d_round

BG_COLOR: tuple = (240, 240, 240)
BORDER_COLOR: tuple = (16, 16, 16)


# Create a function dictionary to allow eval to work
func_dict: dict = {}
for func in ["sin", "cos", "tan", "asin", "acos", "atan", "sqrt", "log", "log10", "gamma", "gamma_shift", "fabs"]:
    func_dict[func] = locals().get(func)


class Grapher:
    def __init__(self, window: pygame.Surface, resolution: tuple[int, int], pos: tuple[int, int],
                 x_range: tuple[float, float], y_range: tuple[float, float]):
        self.lhs, self.rhs, self.x_tol, self.y_tol = None, None, 0, 0
        self.window: pygame.Surface = window
        self.pos: tuple[int, int] = pos
        self.resolution: tuple[int, int] = resolution

        self.font: pygame.font = pygame.font.Font(path.join("Assets", "FiraCode.ttf"), min(resolution) // 60)
        
        self.x_bounds: tuple[float, float] = x_range
        self.y_bounds: tuple[float, float] = y_range
        self.range: tuple[float, float] = abs(x_range[1] - x_range[0]), abs(y_range[1] - y_range[0])
        
        # Helps with determining where points on a function lie on the drawn graph
        self.stretch: tuple = resolution[0] / self.range[0], resolution[1] / self.range[1]
        # Holds the negative of decimal places the graph should show
        self.dec_places: tuple = floor(log10(self.range[0] * 0.25)), floor(log10(self.range[1] * 0.25))
        
        self.graph_points: list[list] | None = [[], [], [], []]  # Holds each relation's coordinates for fast access
        self.m, self.old_m, self.n, self.old_n = 0, 0, 0, 0  # Holds some value
        
        # Graph background
        self.clear_graph()
    
    def reset(self, resolution: tuple[int, int], pos: tuple[int, int],
              x_range: tuple[float, float], y_range: tuple[float, float]) -> None:
        """
        Clears the graph and applies new resolution and boundary settings
        """
        self.resolution = resolution
        self.pos = pos
        self.font = pygame.font.Font(path.join("Assets", "FiraCode.ttf"), min(resolution) // 60)
        self.x_bounds = x_range
        self.y_bounds = y_range
        self.range = x_range[1] - x_range[0], y_range[1] - y_range[0]
        self.stretch: tuple = resolution[0] / self.range[0], resolution[1] / self.range[1]
        self.dec_places: tuple = floor(log10(self.range[0] * 0.25)), floor(log10(self.range[1] * 0.25))
        return None
    
    def new_bounds(self, x_axis: bool, transformation: str) -> tuple[str, str]:
        """
        Returns the new boundaries after a transformation, if the transformation valid
        """
        min_bnd_range: float = 4E-5
        l_bound: str = str(self.x_bounds[0] if x_axis else self.y_bounds[0])
        u_bound: str = str(self.x_bounds[1] if x_axis else self.y_bounds[1])
        if transformation == "in":  # Zoom in
            if x_axis and min_bnd_range < fabs(self.range[0] - 2 * 10**self.dec_places[0]):
                l_bound = d_round(self.x_bounds[0] + 10**self.dec_places[0], -self.dec_places[0])
                u_bound = d_round(self.x_bounds[1] - 10 ** self.dec_places[0], -self.dec_places[0])
            elif min_bnd_range < fabs(self.range[1] - 2 * 10**self.dec_places[1]):
                l_bound = d_round(self.y_bounds[0] + 10 ** self.dec_places[1], -self.dec_places[1])
                u_bound = d_round(self.y_bounds[1] - 10 ** self.dec_places[1], -self.dec_places[1])
        if transformation == "out":  # Zoom out
            if x_axis:
                l_bound = d_round(self.x_bounds[0] - 10 ** self.dec_places[0], -self.dec_places[0])
                u_bound = d_round(self.x_bounds[1] + 10 ** self.dec_places[0], -self.dec_places[0])
            else:
                l_bound = d_round(self.y_bounds[0] - 10 ** self.dec_places[1], -self.dec_places[1])
                u_bound = d_round(self.y_bounds[1] + 10 ** self.dec_places[1], -self.dec_places[1])
        if transformation == "inc":  # Increment both  (Pan right or up)
            if x_axis:
                l_bound = d_round(self.x_bounds[0] + 10**self.dec_places[0], -self.dec_places[0])
                u_bound = d_round(self.x_bounds[1] + 10**self.dec_places[0], -self.dec_places[0])
            else:
                l_bound = d_round(self.y_bounds[0] + 10**self.dec_places[1], -self.dec_places[1])
                u_bound = d_round(self.y_bounds[1] + 10**self.dec_places[1], -self.dec_places[1])
        if transformation == "dec":  # Decrement both  (Pan left or down)
            if x_axis:
                l_bound = d_round(self.x_bounds[0] - 10**self.dec_places[0], -self.dec_places[0])
                u_bound = d_round(self.x_bounds[1] - 10**self.dec_places[0], -self.dec_places[0])
            else:
                l_bound = d_round(self.y_bounds[0] - 10**self.dec_places[1], -self.dec_places[1])
                u_bound = d_round(self.y_bounds[1] - 10**self.dec_places[1], -self.dec_places[1])
        
        return l_bound, u_bound
    
    def validate_equation(self, equ_raw: str) -> tuple[None, int] | tuple[tuple[str, str], int]:
        """
        Assigns $m and $n variables or
        Returns the left and right hand sides of a valid equation.
        If the equation is invalid, it will return some error code between 1 and 5
        """
        # Check if the function is only assigning to variable m
        if equ_raw.startswith("m=") or equ_raw.startswith("m =") and 'x' not in equ_raw and 'y' not in equ_raw:
            try:
                self.old_m, self.m = self.m, eval(equ_raw.split('=')[1].strip())
            except (ArithmeticError, TypeError, SyntaxError, SyntaxWarning, NameError, ValueError, OverflowError):
                pass
            return None, 10
        # Check if the function is only assigning to variable n
        if equ_raw.startswith("n=") or equ_raw.startswith("n =") and 'x' not in equ_raw and 'y' not in equ_raw:
            if equ_raw.count('=') == 1 and len(equ_raw.split('=')) > 1:
                try:
                    self.old_n, self.n = self.n, eval(equ_raw.split('=')[1].strip())
                except (ArithmeticError, TypeError, SyntaxError, SyntaxWarning, NameError, ValueError, OverflowError):
                    pass
                return None, 11
        
        # Invalidate equations with guaranteed empty graphs
        if equ_raw.count('=') != 1 or ('x' not in equ_raw and 'y' not in equ_raw):  # If not a relation of x or y
            return None, 1
        if "/0" in equ_raw.replace(' ', ""):  # If division by zero is a literal
            return None, 2
        
        # Replace symbols with constants or python-readable version
        formatted_equation = format_equation(equ_raw, self.m, self.n)
        
        try:
            # Evaluate both sides to find inherent mistakes in input
            eval(formatted_equation[0].strip().replace('x', '1').replace('y', '1')),  # 1 is a testing value
            eval(formatted_equation[1].strip().replace('x', '1').replace('y', '1'))
        except ZeroDivisionError:  # e.g. 1/x when x = 0
            pass
        except ValueError:  # e.g. out of domain of arcsin (-1, 1)
            pass
        except ArithmeticError:
            return None, 2
        except NameError:
            return None, 3
        except (SyntaxError, SyntaxWarning):
            return None, 4
        except TypeError:
            return None, 5
        
        return (formatted_equation[0].strip(), formatted_equation[1].strip()), 0
    
    def clear_graph(self) -> None:
        """
        Places a blank graph on top of drawn graphs and draws grid lines
        """
        bg = pygame.draw.rect(surface=self.window, color=BG_COLOR, rect=pygame.Rect(self.pos, self.resolution))
        pygame.draw.line(surface=self.window, color=(0, 0, 0), start_pos=bg.midleft, end_pos=bg.midright, width=1)
        pygame.draw.line(surface=self.window, color=(0, 0, 0), start_pos=bg.midtop, end_pos=bg.midbottom, width=1)
        border_res = [r + 1 for r in self.resolution]
        
        # Drawing grid markers and number labels
        step: tuple = 10**self.dec_places[0], 10**self.dec_places[1]
        for x in arange(floor(self.x_bounds[0]), floor(self.x_bounds[1]) + 1, step[0]):
            if self.x_bounds[0] <= x <= self.x_bounds[1]:
                axis_coord: tuple = self.graph_to_window(x, 0.5 * (self.y_bounds[0] + self.y_bounds[1]))
                pygame.draw.line(surface=self.window, color=(0, 0, 0), start_pos=(axis_coord[0], axis_coord[1] + 3),
                                 end_pos=(axis_coord[0], axis_coord[1] - 3), width=1)
                if self.pos[0] < axis_coord[0] + 15 < self.pos[0] + self.resolution[0]:
                    num = self.font.render(d_round(x, -self.dec_places[0]), True, (120, 0, 0))
                    num_tilt = pygame.transform.rotate(num, 180)
                    num_rect: pygame.Rect = num_tilt.get_rect(topleft=(axis_coord[0] + 3, axis_coord[1] + 5))
                    self.window.blit(num, num_rect)
        
        for y in arange(floor(self.y_bounds[0]), floor(self.y_bounds[1]) + 1, step[1]):
            if self.y_bounds[0] <= y <= self.y_bounds[1]:
                axis_coord: tuple = self.graph_to_window(0.5 * (self.x_bounds[0] + self.x_bounds[1]), y)
                pygame.draw.line(surface=self.window, color=(0, 0, 0), start_pos=(axis_coord[0] + 3, axis_coord[1]),
                                 end_pos=(axis_coord[0] - 3, axis_coord[1]), width=1)
                if self.pos[1] < axis_coord[1] + 5 + self.font.get_linesize() < self.pos[1] + self.resolution[1]:
                    num = self.font.render(d_round(y, -self.dec_places[1]), True, (0, 0, 120))
                    num_rect: pygame.Rect = num.get_rect(topleft=(axis_coord[0] + 5, axis_coord[1] + 3))
                    self.window.blit(num, num_rect)
        
        pygame.draw.rect(surface=self.window, color=BORDER_COLOR,
                         rect=pygame.Rect((self.pos[0], self.pos[1]), border_res), width=1)
        return None
    
    def window_to_graph(self, x: float, y: float) -> tuple[float, float] | None:
        """
        If x and y are inside graph, return relative position on the graph from window coordinates
        """
        if self.pos[0] <= x <= self.pos[0] + self.resolution[0] and \
                self.pos[1] <= y <= self.pos[1] + self.resolution[1]:
            return self.x_bounds[0] + (x - self.pos[0]) / self.stretch[0], \
                self.y_bounds[1] - (y - self.pos[1]) / self.stretch[1]
        return None
    
    def graph_to_window(self, x: float, y: float, correction: bool = False) -> tuple[float, float]:
        """
        Applies transformations from a point on a function to a point in the PyGame window
        """
        return self.pos[0] + abs(self.x_bounds[0] - x) * self.stretch[0] + int(correction), \
            self.pos[1] + abs(self.y_bounds[1] - y) * self.stretch[1] + int(correction)
    
    def function_graph(self, equation: tuple[str, str], indicator: Text, color: tuple, width: int) -> None:
        """
        Generates graph my iterating over each x value of function, rather than every pixel
        Supports y and x functions. i.e. y = f(x) or x = f(y)
        """
        lhs, rhs = equation
        is_y_function: bool = lhs == "(y)"
        indicator.draw()  # Show on function input that graph is being calculated
        
        if is_y_function:  # Function is known to be a y function
            x_points, y_points = linspace(self.x_bounds[0], self.x_bounds[1], num=self.resolution[0]), []
            for x in x_points:
                try:
                    y_point = eval(rhs.replace('x', str(x)), {}, func_dict)
                    y_points.append(y_point)
                except (ArithmeticError, ValueError, TypeError, OverflowError):
                    y_points.append(None)
        else:  # Is x function
            x_points, y_points = [], linspace(self.y_bounds[0], self.y_bounds[1], num=self.resolution[1])
            for y in y_points:
                try:
                    x_point = eval(rhs.replace('y', str(y)), {}, func_dict)
                    x_points.append(x_point)
                except (ArithmeticError, ZeroDivisionError, ValueError, TypeError):
                    x_points.append(None)
        
        # Add zero to the graph if it is within boundaries
        if self.x_bounds[0] < 0 < self.x_bounds[1] and self.y_bounds[0] < 0 < self.y_bounds[1]:
            try:
                if is_y_function:
                    x_points = list(x_points)
                    points = list(zip(x_points, y_points))
                    points.append((0, eval(rhs.replace('x', '0'), {}, func_dict)))
                    points.sort()
                    x_points, y_points = points
                else:
                    y_points = list(y_points)
                    points = list(zip(x_points, y_points))
                    points.append((eval(rhs.replace('y', '0'), {}, func_dict), 0))
                    points.sort()
                    x_points, y_points = points
            except (ArithmeticError, ValueError, TypeError, OverflowError):
                pass
        
        stroke_points: list = []
        pen_down: bool = False
        prev_x, prev_y = None, None
        for idx, (x, y) in enumerate(zip(x_points, y_points)):
            try:
                if not (x is None or y is None):  # If there is a point to be drawn for this x_value
                    if is_y_function:
                        if self.y_bounds[0] <= y <= self.y_bounds[1]:  # If current point falls within y_bounds
                            if not len(stroke_points) and idx > 0 and prev_y:  # If the previous point outside of range
                                # Find y-range intercept
                                y_bound_hit = 1 if prev_y > self.y_bounds[1] else 0
                                tan_theta = (y - prev_y) / (x - prev_x)
                                casted_x = prev_x + (self.y_bounds[y_bound_hit] - prev_y) / tan_theta
                                casted_y = self.y_bounds[y_bound_hit]
                                
                                # Add a point just after function comes back into the graph
                                stroke_points.append(self.graph_to_window(casted_x, casted_y))
                            # Add point to graph
                            stroke_points.append(self.graph_to_window(x, y))
                            pen_down = True
                        
                        elif pen_down:  # Function continues outside of range
                            # Find y-range intercept
                            y_bound_hit = 1 if y > self.y_bounds[1] else 0
                            tan_theta = (y - prev_y) / (x - prev_x)
                            casted_x = prev_x + (self.y_bounds[y_bound_hit] - prev_y) / tan_theta
                            casted_y = self.y_bounds[y_bound_hit]
                            
                            # Add a point just before function leaves graph
                            stroke_points.append(self.graph_to_window(casted_x, casted_y))
                            pen_down = False  # Draw the current continuity
                    else:  # Graph for x function, reflected over y = x
                        if self.x_bounds[0] <= x <= self.x_bounds[1]:  # If current point falls within x_bounds
                            if not len(stroke_points) and idx > 0 and prev_x:  # If the previous point outside of range
                                # Find x-range intercept
                                x_bound_hit = 1 if prev_x > self.x_bounds[1] else 0
                                tan_theta = (x - prev_x) / (y - prev_y)
                                casted_x = self.x_bounds[x_bound_hit]
                                casted_y = prev_y + (self.x_bounds[x_bound_hit] - prev_x) / tan_theta
            
                                # Add a point just after function comes back into the graph
                                stroke_points.append(self.graph_to_window(casted_x, casted_y))
                            # Add point to graph
                            stroke_points.append(self.graph_to_window(x, y))
                            pen_down = True
    
                        elif pen_down:  # Function continues outside of range
                            # Find x-range intercept
                            x_bound_hit = 1 if x > self.x_bounds[1] else 0
                            tan_theta = (x - prev_x) / (y - prev_y)
                            casted_x = self.x_bounds[x_bound_hit]
                            casted_y = prev_y + (self.x_bounds[x_bound_hit] - prev_x) / tan_theta
        
                            # Add a point just before function leaves graph
                            stroke_points.append(self.graph_to_window(casted_x, casted_y))
                            pen_down = False
                else:  # Point will not be drawn
                    pen_down = False  # Draw the current continuity
                    
                prev_x, prev_y = x, y
            except TypeError:
                pass
            
            if not pen_down and len(stroke_points):  # If graph has gone out of range, draw current line
                pygame.draw.aalines(surface=self.window, color=color, closed=False, points=stroke_points, blend=width)
                stroke_points.clear()
        if len(stroke_points):  # If function reaches end of graph without break, draw everything
            pygame.draw.aalines(surface=self.window, color=color, closed=False, points=stroke_points, blend=width)
        
        indicator.hide(BG_COLOR)  # Remove "Rendering..." from function input
        return None
    
    def iterative_graph(self, equation: tuple[str, str], indicator: Text, color: tuple, width: int, idx: int) -> None:
        """
        DEPRECATED
        Function to generate and draw a graph by iterating over every pixel, uses multithreading
        """
        lhs, rhs = equation
        indicator.draw()
        
        # Helps determine if function lies within a 'pixel'; tolerance
        x_tol, y_tol = self.range[0] / self.resolution[0] * 0.5, self.range[1] / self.resolution[1] * 0.5
        
        # Generate information for computation of plotted points
        # i.e. equation, coordinates to be iterated, tolerances
        info_packs: list[tuple] = []
        for x in linspace(self.x_bounds[0], self.x_bounds[1], num=self.resolution[0]):
            for y in linspace(self.y_bounds[0], self.y_bounds[1], num=self.resolution[1]):
                info_packs.append((lhs, rhs, (x, y), x_tol, y_tol))
        if self.x_bounds[0] < 0 < self.x_bounds[1]:
            for y in linspace(self.y_bounds[0], self.y_bounds[1], num=self.resolution[1]):
                info_packs.append((lhs, rhs, (0, y), x_tol, y_tol))
        if self.y_bounds[0] < 0 < self.y_bounds[1]:
            for x in linspace(self.x_bounds[0], self.x_bounds[1], num=self.resolution[0]):
                info_packs.append((lhs, rhs, (x, 0), x_tol, y_tol))
        
        self.graph_points[idx] = generate_plot_points(info_packs)
        indicator.hide(BG_COLOR)
        if not self.graph_points[idx]:
            print("Function", idx + 1, "empty graph")
        else:
            # Draw graph on screen
            self.draw_graph(idx, color, width)
        
        return None
        
    def draw_graph(self, idx, color: tuple, width: int) -> None:
        """
        Draws points from the stored points of the function onto the graph
        """
        for point in self.graph_points[idx]:
            if self.x_bounds[0] <= point[0] <= self.x_bounds[1] and self.y_bounds[0] <= point[1] <= self.y_bounds[1]:
                # Point falls within the graph boundary
                adjusted_point: tuple[float, float] = self.graph_to_window(point[0], point[1], True)
                sleep(0.5 / len(self.graph_points[idx]))  # Animate drawing, takes 1 second to finish
                pygame.draw.rect(surface=self.window, color=color, rect=pygame.Rect(adjusted_point, (width, width)))
        
        border_res = [r + 2 * width for r in self.resolution]
        pygame.draw.rect(surface=self.window, color=BORDER_COLOR,
                         rect=pygame.Rect((self.pos[0], self.pos[1]), border_res), width=width)
        return None
