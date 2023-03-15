import logging
from os import path
from sys import exit
from multiprocessing import freeze_support, Process, Manager
from threading import Thread
from screeninfo import get_monitors
from copy import deepcopy
from contextlib import redirect_stdout
with redirect_stdout(None):
    import pygame
    
import json

from Classes.SpriteButton import SpriteButton
from Classes.CheckBox import CheckBox
from Classes.InputBox import InputBox
from Classes.Grapher import Grapher
from Classes.Text import Text
from Scripts.GraphUtilities import generate_iterative_plots, generate_plot_points

if __name__ == "__main__":
    _TITLE: str = "GraphCalc"
    
    try:  # Load files in assets directory
        _ICON: pygame.Surface = pygame.image.load(path.join("Assets", "graphcalc.png"))
        func_normal: pygame.Surface = pygame.image.load(path.join("Assets", "func.tiff"))
        func_hover: pygame.Surface = pygame.image.load(path.join("Assets", "func_hover.tiff"))
        render_normal: pygame.Surface = pygame.image.load(path.join("Assets", "render.tiff"))
        render_hover: pygame.Surface = pygame.image.load(path.join("Assets", "render_hover.tiff"))
        zoom_plus: pygame.Surface = pygame.image.load(path.join("Assets", "btn_zoom_in.tiff"))
        zoom_minus: pygame.Surface = pygame.image.load(path.join("Assets", "btn_zoom_out.tiff"))
        left_arrow: pygame.Surface = pygame.image.load(path.join("Assets", "btn_left.tiff"))
        right_arrow: pygame.Surface = pygame.image.load(path.join("Assets", "btn_right.tiff"))
        down_arrow: pygame.Surface = pygame.image.load(path.join("Assets", "btn_down.tiff"))
        up_arrow: pygame.Surface = pygame.image.load(path.join("Assets", "btn_up.tiff"))
        centre_move: pygame.Surface = pygame.image.load(path.join("Assets", "btn_centre.tiff"))
        clicksel: pygame.Surface = pygame.image.load(path.join("Assets", "btn_clicksel.tiff"))
    except FileNotFoundError:
        print("This must be run with the Assets folder in its directory")
        exit(404)

func_dict: dict = {}  # Create a dictionary for eval to identify functions
for function in ["sin", "cos", "tan", "sec", "csc", "cot", "asin", "acos", "atan", "sqrt", "log", "log10", "gamma"]:
    func_dict[function] = locals().get(function)

WIN_RES: tuple[int, int] = (450, 650)

TICK: int = 6evalf;lsdkfsdjfslkdfjlsdf0  # Refresh rate

# Colors
BG_COLOR: tuple = (240, 240, 240)
GP_BORDER_COLOR: tuple = (2, 6, 8)
TEXT_COLOR: tuple = (0, 0, 0)
BRIGHT_COLOR: tuple = (255, 255, 255)
BOUND_COLOR: tuple = (150, 210, 255)
INV_BND_COLOR: tuple = (240, 0, 0)
INV_FUNC_COLOR: tuple = (0, 0, 0)

FUNC_TEXT_SIZE: int = 12
BOUND_TEXT_SIZE: int = 10

# Graph variables
GRAPH_RES: tuple[int, int] = 300, 300
GRAPH_POS: tuple[int, int] = int((WIN_RES[0] - GRAPH_RES[0]) * 0.5), 40
LINE_WIDTH: int = 1
LINE_COLORS: tuple = (255, 0, 0), (12, 168, 48), (12, 64, 255), (128, 48, 128)

# Placeholders for elements
grapher: Grapher
render_button: SpriteButton
res_error: Text
res_box_x: InputBox
res_box_y: InputBox
graph_buttons: tuple
clicksel_prompt: Text
bound_labels: tuple
bounds: tuple
left_bound: InputBox
right_bound: InputBox
lower_bound: InputBox
upper_bound: InputBox
bound_errors: tuple
func_labels: tuple
indicators: tuple
func_errors: tuple
enablers: tuple
funcs: tuple
inserts: tuple
insert_label1: Text
insert_label2: Text

# Store the text that will be drawn when changing resolution
dce_texts: tuple = ("-10", "10", "-10", "10", True, False, False, False, "y = -x^3", "y = x(x + 1)(x - 2)", "", "")


def iterative_points(equation: tuple[str, str], x_bounds, y_bounds, ranges, resolution, mang_dict, idx):
    """
    Auxiliary function to allow iterative graphs to be generated in a process rather than a thread
    """
    # Generate information for computation of plotted points
    # i.e. equation, coordinates to be iterated, tolerances
    info_packs: tuple[tuple] = generate_iterative_plots(equation, x_bounds, y_bounds, ranges, resolution)
    graph_points = generate_plot_points(info_packs)
    mang_dict[idx] = graph_points
    return


# noinspection PyUnboundLocalVariable
def graph_config_window() -> None:
    global GRAPH_RES, WIN_RES, GRAPH_POS, dce_texts
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.init()
    
    clock: pygame.time.Clock = pygame.time.Clock()
    pygame.display.set_caption(_TITLE)
    pygame.display.set_icon(_ICON)
    window: pygame.Surface = pygame.display.set_mode(WIN_RES, pygame.DOUBLEBUF)
    
    def draw_config_elements() -> None:
        global grapher, res_box_x, res_box_y, res_error, graph_buttons, clicksel_prompt, render_button, \
            bound_labels, bounds, left_bound, right_bound, lower_bound, upper_bound, bound_errors, \
            func_labels, indicators, func_errors, enablers, funcs, inserts, insert_label1, insert_label2
        """
        Draws all of the GUI elements, used when changing resolution
        """
        graph_border: pygame.Rect = pygame.Rect((0, 0), (WIN_RES[0], GRAPH_RES[1] + 105))
        grapher = Grapher(window=window, resolution=GRAPH_RES, pos=GRAPH_POS,
                          x_range=(-10, 10), y_range=(-10, 10))
        render_button = SpriteButton(window, (int(WIN_RES[0] * 0.5) - 50, WIN_RES[1] - 45), (100, 30), "enter",
                                     BRIGHT_COLOR, 18, render_normal, render_hover)
        
        res_text: Text = Text(window, "Graph Resolution:", 10, BRIGHT_COLOR, (3, 3))
        res_box_x = InputBox(window, (5, 20), 35, str(GRAPH_RES[0]), 12)
        res_box_y = InputBox(window, (45, 20), 35, str(GRAPH_RES[1]), 12)
        res_error = Text(window, "Invalid", FUNC_TEXT_SIZE, INV_BND_COLOR, (20, 45))
        
        zoom_in: SpriteButton = SpriteButton(window,
                                             (35, GRAPH_POS[1] + GRAPH_RES[1] + 5),
                                             (25, 25), "", BG_COLOR, 5, zoom_plus, zoom_plus)
        zoom_out: SpriteButton = SpriteButton(window,
                                              (5, GRAPH_POS[1] + GRAPH_RES[1] + 5),
                                              (25, 25), "", BG_COLOR, 5, zoom_minus, zoom_minus)
        left_pan: SpriteButton = SpriteButton(window,
                                              (WIN_RES[0] - 90, GRAPH_POS[1] + GRAPH_RES[1] + 5),
                                              (25, 25), "", BG_COLOR, 5, left_arrow, left_arrow)
        right_pan: SpriteButton = SpriteButton(window,
                                               (WIN_RES[0] - 30, GRAPH_POS[1] + GRAPH_RES[1] + 5),
                                               (25, 25), "", BG_COLOR, 5, right_arrow, right_arrow)
        down_pan: SpriteButton = SpriteButton(window,
                                              (WIN_RES[0] - 60, GRAPH_POS[1] + GRAPH_RES[1] + 35),
                                              (25, 25), "", BG_COLOR, 5, down_arrow, down_arrow)
        up_pan: SpriteButton = SpriteButton(window,
                                            (WIN_RES[0] - 60, GRAPH_POS[1] + GRAPH_RES[1] - 25),
                                            (25, 25), "", BG_COLOR, 5, up_arrow, up_arrow)
        centre_set: SpriteButton = SpriteButton(window,
                                                (WIN_RES[0] - 60, GRAPH_POS[1] + GRAPH_RES[1] + 5),
                                                (25, 25), "", BG_COLOR, 5, centre_move, centre_move)
        bound_set: SpriteButton = SpriteButton(window,
                                               (WIN_RES[0] - 30, GRAPH_POS[1] + GRAPH_RES[1] - 25),
                                               (25, 25), "", BG_COLOR, 5, clicksel, clicksel)
        graph_buttons = zoom_in, zoom_out, left_pan, right_pan, down_pan, up_pan, centre_set, bound_set
        clicksel_prompt = Text(window, "Select the next corner", 16, BRIGHT_COLOR,
                               (int(GRAPH_POS[0] + GRAPH_RES[0] * 0.5) - 110, GRAPH_POS[1] + GRAPH_RES[1] + 35))
        
        left_label: Text = Text(window, "LEFT X:", 12, BOUND_COLOR,
                                (GRAPH_POS[0] - 55, int(GRAPH_POS[1] + GRAPH_RES[1] * 0.5 - 24)))
        right_label: Text = Text(window, "RIGHT X:", 12, BOUND_COLOR,
                                 (GRAPH_POS[0] + GRAPH_RES[0] + 5, int(GRAPH_POS[1] + GRAPH_RES[1] * 0.5 - 24)))
        lower_label: Text = Text(window, "LOWER Y:", 12, BOUND_COLOR,
                                 (int(WIN_RES[0] * 0.5) - 90, GRAPH_POS[1] + GRAPH_RES[1] + 10))
        upper_label: Text = Text(window, "UPPER Y:", 12, BOUND_COLOR,
                                 (int(WIN_RES[0] * 0.5) - 90, GRAPH_POS[1] - 20))
        bound_labels = left_label, right_label, lower_label, upper_label
        
        left_bound = InputBox(window,
                              (GRAPH_POS[0] - 55, int(GRAPH_POS[1] + GRAPH_RES[1] * 0.5 - 6)),
                              50, dce_texts[0], 10)
        right_bound = InputBox(window,
                               (GRAPH_POS[0] + GRAPH_RES[0] + 5, int(GRAPH_POS[1] + GRAPH_RES[1] * 0.5 - 6)),
                               50, dce_texts[1], 10)
        lower_bound = InputBox(window,
                               (int(WIN_RES[0] * 0.5) - 25, GRAPH_POS[1] + GRAPH_RES[1] + 10),
                               50, dce_texts[2], 10)
        upper_bound = InputBox(window,
                               (int(WIN_RES[0] * 0.5) - 25, GRAPH_POS[1] - 20),
                               50, dce_texts[3], 10)
        bounds = left_bound, right_bound, lower_bound, upper_bound
        
        left_error: Text = Text(window, "Invalid", 12, INV_BND_COLOR,
                                (GRAPH_POS[0] - 55, int(GRAPH_POS[1] + GRAPH_RES[1] * 0.5 + 12)))
        right_error: Text = Text(window, "Invalid", 12, INV_BND_COLOR,
                                 (GRAPH_POS[0] + GRAPH_RES[0] + 5, int(GRAPH_POS[1] + GRAPH_RES[1] * 0.5) + 12))
        lower_error: Text = Text(window, "Invalid", 12, INV_BND_COLOR,
                                 (int(WIN_RES[0] * 0.5) + 35, GRAPH_POS[1] + GRAPH_RES[1] + 10))
        upper_error: Text = Text(window, "Invalid", 12, INV_BND_COLOR,
                                 (int(WIN_RES[0] * 0.5) + 35, GRAPH_POS[1] - 20))
        bound_errors = left_error, right_error, lower_error, upper_error
        
        func1_label: Text = Text(window, "Function 1:", FUNC_TEXT_SIZE, TEXT_COLOR,
                                 (int(WIN_RES[0] * 0.5) - 220, WIN_RES[1] - 240))
        func2_label: Text = Text(window, "Function 2:", FUNC_TEXT_SIZE, TEXT_COLOR,
                                 (int(WIN_RES[0] * 0.5) - 220, WIN_RES[1] - 190))
        func3_label: Text = Text(window, "Function 3:", FUNC_TEXT_SIZE, TEXT_COLOR,
                                 (int(WIN_RES[0] * 0.5) - 220, WIN_RES[1] - 140))
        func4_label: Text = Text(window, "Function 4:", FUNC_TEXT_SIZE, TEXT_COLOR,
                                 (int(WIN_RES[0] * 0.5) - 220, WIN_RES[1] - 90))
        func_labels = func1_label, func2_label, func3_label, func4_label
        
        indicator1: Text = Text(window, "Rendering...", FUNC_TEXT_SIZE, LINE_COLORS[0],
                                (int(WIN_RES[0] * 0.5) - 135, WIN_RES[1] - 240))
        indicator2: Text = Text(window, "Rendering...", FUNC_TEXT_SIZE, LINE_COLORS[1],
                                (int(WIN_RES[0] * 0.5) - 135, WIN_RES[1] - 190))
        indicator3: Text = Text(window, "Rendering...", FUNC_TEXT_SIZE, LINE_COLORS[2],
                                (int(WIN_RES[0] * 0.5) - 135, WIN_RES[1] - 140))
        indicator4: Text = Text(window, "Rendering...", FUNC_TEXT_SIZE, LINE_COLORS[3],
                                (int(WIN_RES[0] * 0.5) - 135, WIN_RES[1] - 90))
        indicators = indicator1, indicator2, indicator3, indicator4
        
        func_error1: Text = Text(window, "Error Not Found", FUNC_TEXT_SIZE, TEXT_COLOR,
                                 (int(WIN_RES[0] * 0.5) + 100, WIN_RES[1] - 240))
        func_error2: Text = Text(window, "Error Not Found", FUNC_TEXT_SIZE, TEXT_COLOR,
                                 (int(WIN_RES[0] * 0.5) + 100, WIN_RES[1] - 190))
        func_error3: Text = Text(window, "Error Not Found", FUNC_TEXT_SIZE, TEXT_COLOR,
                                 (int(WIN_RES[0] * 0.5) + 100, WIN_RES[1] - 140))
        func_error4: Text = Text(window, "Error Not Found", FUNC_TEXT_SIZE, TEXT_COLOR,
                                 (int(WIN_RES[0] * 0.5) + 100, WIN_RES[1] - 90))
        func_errors = func_error1, func_error2, func_error3, func_error4
        
        enabler1: CheckBox = CheckBox(window,
                                      (int(WIN_RES[0] * 0.5) - 220, WIN_RES[1] - 220),
                                      18, LINE_COLORS[0], dce_texts[4])
        enabler2: CheckBox = CheckBox(window,
                                      (int(WIN_RES[0] * 0.5) - 220, WIN_RES[1] - 170),
                                      18, LINE_COLORS[1], dce_texts[5])
        enabler3: CheckBox = CheckBox(window,
                                      (int(WIN_RES[0] * 0.5) - 220, WIN_RES[1] - 120),
                                      18, LINE_COLORS[2], dce_texts[6])
        enabler4: CheckBox = CheckBox(window,
                                      (int(WIN_RES[0] * 0.5) - 220, WIN_RES[1] - 70),
                                      18, LINE_COLORS[3], dce_texts[7])
        enablers = enabler1, enabler2, enabler3, enabler4
        
        func_input1: InputBox = InputBox(window,
                                         (int(WIN_RES[0] * 0.5) - 197, WIN_RES[1] - 220),
                                         298, dce_texts[8], FUNC_TEXT_SIZE)
        func_input2: InputBox = InputBox(window,
                                         (int(WIN_RES[0] * 0.5) - 197, WIN_RES[1] - 170),
                                         298, dce_texts[9], FUNC_TEXT_SIZE)
        func_input3: InputBox = InputBox(window,
                                         (int(WIN_RES[0] * 0.5) - 197, WIN_RES[1] - 120),
                                         298, dce_texts[10], FUNC_TEXT_SIZE)
        func_input4: InputBox = InputBox(window,
                                         (int(WIN_RES[0] * 0.5) - 197, WIN_RES[1] - 70),
                                         298, dce_texts[11], FUNC_TEXT_SIZE)
        funcs = func_input1, func_input2, func_input3, func_input4
        
        insert_label1 = Text(window, "Function", 16, TEXT_COLOR,
                             (int(WIN_RES[0] * 0.5) + 125, WIN_RES[1] - 240))
        insert_label2 = Text(window, "Inserts", 16, TEXT_COLOR,
                             (int(WIN_RES[0] * 0.5) + 130, WIN_RES[1] - 220))
        sin_insert: SpriteButton = SpriteButton(window,
                                                (int(WIN_RES[0] * 0.5) + 105, WIN_RES[1] - 200),
                                                (55, 25), "sin", TEXT_COLOR, 12, func_normal, func_hover)
        cos_insert: SpriteButton = SpriteButton(window,
                                                (int(WIN_RES[0] * 0.5) + 105, WIN_RES[1] - 170),
                                                (55, 25), "cos", TEXT_COLOR, 12, func_normal, func_hover)
        tan_insert: SpriteButton = SpriteButton(window,
                                                (int(WIN_RES[0] * 0.5) + 105, WIN_RES[1] - 140),
                                                (55, 25), "tan", TEXT_COLOR, 12, func_normal, func_hover)
        abs_insert: SpriteButton = SpriteButton(window,
                                                (int(WIN_RES[0] * 0.5) + 105, WIN_RES[1] - 110),
                                                (55, 25), "abs", TEXT_COLOR, 12, func_normal, func_hover)
        fact_insert: SpriteButton = SpriteButton(window,
                                                 (int(WIN_RES[0] * 0.5) + 105, WIN_RES[1] - 80),
                                                 (55, 25), "fact", TEXT_COLOR, 12, func_normal, func_hover)
        sec_insert: SpriteButton = SpriteButton(window,
                                                (int(WIN_RES[0] * 0.5) + 165, WIN_RES[1] - 200),
                                                (55, 25), "sec", TEXT_COLOR, 12, func_normal, func_hover)
        csc_insert: SpriteButton = SpriteButton(window,
                                                (int(WIN_RES[0] * 0.5) + 165, WIN_RES[1] - 170),
                                                (55, 25), "csc", TEXT_COLOR, 12, func_normal, func_hover)
        cot_insert: SpriteButton = SpriteButton(window,
                                                (int(WIN_RES[0] * 0.5) + 165, WIN_RES[1] - 140),
                                                (55, 25), "cot", TEXT_COLOR, 12, func_normal, func_hover)
        sqrt_insert: SpriteButton = SpriteButton(window,
                                                 (int(WIN_RES[0] * 0.5) + 165, WIN_RES[1] - 110),
                                                 (55, 25), "sqrt", TEXT_COLOR, 12, func_normal, func_hover)
        clear: SpriteButton = SpriteButton(window,
                                           (int(WIN_RES[0] * 0.5) + 165, WIN_RES[1] - 80),
                                           (55, 25), "clear", TEXT_COLOR, 12, func_normal, func_hover)
        inserts = (sin_insert, cos_insert, tan_insert, abs_insert, fact_insert, sec_insert, csc_insert, cot_insert,
                   sqrt_insert, clear)
        
        window.fill(BG_COLOR)
        pygame.draw.rect(surface=window, color=GP_BORDER_COLOR, rect=graph_border)
        render_button.draw()
        insert_label1.draw()
        insert_label2.draw()
        for element in (res_text, res_box_x, res_box_y) + graph_buttons + bound_labels + func_labels + enablers + \
                bounds + funcs + inserts:
            element.draw()
        grapher.clear_graph()
        return None
    
    # Draw all GUI elements for first time
    draw_config_elements()
    
    mouse_cool: bool = False  # Cooldown for mouse press, only running once per click
    old_bounds, new_bounds = tuple((0, 0) for _ in bounds), tuple((0, 0) for _ in bounds)
    old_funcs: list = [None for _ in funcs]
    res_changed: bool = False
    in_cool, out_cool, l_cool, r_cool, d_cool, u_cool = False, False, False, False, False, False  # For graph panning
    ren_cool: bool = False  # For render button shortcut
    tab_cool: bool = False  # For textbox switching
    reset_cool: bool = False  # For resetting graph boundary
    setting_bound: bool = False  # Waiting for another click for click boundary selection
    first_corner: tuple | None = None  # Holds the window_to_graph of first click position for click boundary selection
    did_poz: bool = False  # Change render_button text if user had adjusted boundaries by moving
    
    # Variables to hold threads, processes, and processing variables
    render_queue: list[Thread] = []
    proc_queue: list[None | Process] = [None for _ in funcs]
    manager = Manager()
    mang_dict = manager.dict()
    
    pygame.display.update()
    running: bool = True
    while running:  # Main loop
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.QUIT:  # Then prepare to quit program
                pygame.display.set_caption("Quitting: " + _TITLE)
                pygame.display.set_mode(WIN_RES)
                running = False
                break
        if not running:
            break
    
        # Update function enablers and render button
        for enabler in enablers:
            if enabler.update():
                enabler.draw()
        if render_button.update():
            render_button.draw()
    
        # Update function insert buttons
        shift_pressed: bool = keys_pressed[pygame.K_LSHIFT]
        for idx, insert in enumerate(inserts):
            # Change text to show 2nd functions
            functions: tuple = (("sin", "asin"), ("cos", "acos"), ("tan", "atan"), ("abs", "log"), ("fact", "gamma"),
                                ('x', "sec"), ('y', "csc"), ('=', "cot"), ("sqrt", "ln"))
            for i, func_insert in enumerate(functions):  # Iterate over each idx and function
                if idx == i:
                    insert.text = func_insert[shift_pressed]
                    break
            
            insert.update()
            insert.draw()
            if insert.is_click:
                for func_box in funcs:
                    if func_box.active or func_box.was_active:
                        func_box.update(events, True)
                        # Test for each insert button and insert corresponding text
                        if idx == 0:
                            func_box.insert_text("asin()" if shift_pressed else "sin()")
                        elif idx == 1:
                            func_box.insert_text("acos()" if shift_pressed else "cos()")
                        elif idx == 2:
                            func_box.insert_text("atan()" if shift_pressed else "tan()")
                        elif idx == 3:
                            func_box.insert_text("log()" if shift_pressed else "abs()")
                        elif idx == 4:
                            func_box.insert_text("gamma()" if shift_pressed else "fact()")
                        elif idx == 5:
                            if shift_pressed:
                                func_box.insert_text("sec()")
                            else:
                                func_box.insert_text('x', function=False)
                        elif idx == 6:
                            if shift_pressed:
                                func_box.insert_text("csc()")
                            else:
                                func_box.insert_text('y', function=False)
                        elif idx == 7:
                            if shift_pressed:
                                func_box.insert_text("cot()")
                            else:
                                func_box.insert_text('=', function=False)
                        elif idx == 8:
                            func_box.insert_text("ln()" if shift_pressed else "sqrt()")
                        elif idx == 9:
                            func_box.text = ""
                            func_box.index = 0
                            func_box.lindex = 0
                            func_box.view = 0
                        break
        
        is_typing: bool = False
        for func in funcs + bounds + (res_box_x, res_box_y):
            is_typing |= func.active
        
        # Update functions
        invalid_funcs: list[bool] = [False for _ in funcs]
        for idx, (func_box, func_error) in enumerate(zip(funcs, func_errors)):
            func_box.update(events)
            if func_box.active or func_box.was_active:
                if keys_pressed[pygame.K_TAB] and not tab_cool:  # Tab switching
                    funcs[idx].active = False
                    funcs[(idx - (1 if shift_pressed else -1)) % 4].active = True
                    tab_cool = True
                func_box.draw()
                func_error.hide(BG_COLOR, 300)
                if func_box.text:
                    valid_prompt = grapher.validate_equation(func_box.text)
                    if valid_prompt[1]:  # If there is an error code
                        invalid_funcs[idx] = True
                        
                        func_error.text = "Invalid Function/Relation"
                        if valid_prompt[1] == 1:
                            func_error.text = "Missing: = and/or (x or y)"
                        elif valid_prompt[1] == 2:
                            func_error.text = "Arithmetic Error"
                        elif valid_prompt[1] == 10:
                            func_error.text = f"Assigned value to: $m"
                            if grapher.old_m != grapher.m:
                                render_button.is_click = True
                        elif valid_prompt[1] == 11:
                            func_error.text = f"Assigned value to: $n"
                            if grapher.old_n != grapher.n:
                                render_button.is_click = True
                    
                        func_error.draw(from_right=True)
        
        # Update bounds
        invalid_bounds, bound_box_changed = False, False
        for idx, (bound_box, bound_error) in enumerate(zip(bounds, bound_errors)):
            if keys_pressed[pygame.K_F5] and not reset_cool:  # Run centre set,
                bound_box.text = str((idx % 2 - 0.5) * 20)  # Set the l, r, d, u bounds to -10, 10, -10, 10
                render_button.is_click = True
                bound_box.draw()
                if idx == 3:
                    reset_cool = True  # Triggers cooldown for keyboard button press, run this once per F5 key press
                continue  # The boundaries will be valid
            elif not keys_pressed[pygame.K_F5]:
                reset_cool = False
            bound_box.update(events)
            if bound_box.active and keys_pressed[pygame.K_TAB] and not tab_cool:  # Tab switching
                # Cycle in clockwise direction, counter-clockwise if shift_pressed
                bounds[idx].active = False
                if idx == 0:  # Left
                    bounds[3 if not shift_pressed else 2].active = True  # Top, S: Bottom
                elif idx == 1:  # Right
                    bounds[2 if not shift_pressed else 3].active = True  # Bottom, S: Top
                elif idx == 2:  # Bottom
                    bounds[0 if not shift_pressed else 1].active = True  # Left, S: Right
                elif idx == 3:  # Top
                    bounds[1 if not shift_pressed else 0].active = True  # Right, S: Left
                tab_cool = True
            bound_error.hide(GP_BORDER_COLOR)
            bound_box.draw()
            
            try:
                if 0 < abs(eval(bound_box.text)) < 1E-5:
                    bound_error.draw()
                    invalid_bounds = True
                # Compare if right_bound > left_bound and upper_bound > lower_bound
                pair_idx = idx + 1 if idx % 2 == 0 else idx - 1  # Pair up and down with left and right
                if pair_idx > idx:
                    if eval(bound_box.text, {}, func_dict) >= eval(bounds[pair_idx].text, {}, func_dict):
                        bound_error.draw()
                        invalid_bounds = True
                elif eval(bound_box.text, {}, func_dict) <= eval(bounds[pair_idx].text, {}, func_dict):
                    bound_error.draw()
                    invalid_bounds = True
            except (ArithmeticError, TypeError, SyntaxError, SyntaxWarning, NameError, ValueError):
                # If the boundary is invalid
                if invalid_bounds:
                    bound_error.hide(GP_BORDER_COLOR)
            
                try:
                    eval(bound_box.text, {}, func_dict)
                except (ArithmeticError, TypeError, SyntaxError, SyntaxWarning, NameError, ValueError):
                    # If error is within its own box instead of being higher or lower than its pair
                    bound_error.draw()
                invalid_bounds = True
        
        pan_or_zoom: bool = False  # Tells graph if to transform graph instead of render again
        # Buttons
        for idx, button in enumerate(graph_buttons):
            button.update()
            button.draw()
            if button.is_click:
                pan_or_zoom = True
                render_button.is_click = True
                if idx == 0:
                    left_bound.text, right_bound.text = grapher.new_bounds(x_axis=True, transformation="in")
                    lower_bound.text, upper_bound.text = grapher.new_bounds(x_axis=False, transformation="in")
                elif idx == 1:
                    left_bound.text, right_bound.text = grapher.new_bounds(x_axis=True, transformation="out")
                    lower_bound.text, upper_bound.text = grapher.new_bounds(x_axis=False, transformation="out")
                elif idx == 2:
                    left_bound.text, right_bound.text = grapher.new_bounds(x_axis=True, transformation="dec")
                elif idx == 3:
                    left_bound.text, right_bound.text = grapher.new_bounds(x_axis=True, transformation="inc")
                elif idx == 4:
                    lower_bound.text, upper_bound.text = grapher.new_bounds(x_axis=False, transformation="dec")
                elif idx == 5:
                    lower_bound.text, upper_bound.text = grapher.new_bounds(x_axis=False, transformation="inc")
                elif idx == 6:
                    for i, bound in enumerate(bounds):
                        bound.text = str((i % 2 - 0.5) * 20)
                elif idx == 7:
                    setting_bound = True
                    first_corner = None
                    mouse_cool = True
                    clicksel_prompt.hide(GP_BORDER_COLOR)
                    clicksel_prompt.text = "Select the first corner"
                    clicksel_prompt.draw()
        
        # Click boundary selection
        mb_pressed: bool = pygame.mouse.get_pressed()[0]
        if mb_pressed and not mouse_cool:
            if setting_bound:
                m_pos: tuple = pygame.mouse.get_pos()
                m_gp_coords: tuple = grapher.window_to_graph(m_pos[0], m_pos[1])
                if m_gp_coords:  # If mouse is within graph
                    if not first_corner:
                        # first_corner = tuple(d_round(c, -grapher.dec_places[i]) for i, c in enumerate(m_gp_coords))
                        first_corner = m_gp_coords
                        mouse_cool = True
                        clicksel_prompt.hide(GP_BORDER_COLOR)
                        clicksel_prompt.text = "Select the next corner"
                        clicksel_prompt.draw()
                    elif m_gp_coords != first_corner:
                        # s_corner: tuple = tuple(d_round(c, -grapher.dec_places[i]) for i, c in enumerate(m_gp_coords))
                        s_corner: tuple = m_gp_coords
                        setting_bound = False
                        clicksel_prompt.hide(GP_BORDER_COLOR)
                        left_bound.text = str(min(first_corner[0], s_corner[0]))
                        right_bound.text = str(max(first_corner[0], s_corner[0]))
                        lower_bound.text = str(min(first_corner[1], s_corner[1]))
                        upper_bound.text = str(max(first_corner[1], s_corner[1]))
                        render_button.is_click = True
                        first_corner = None
                        mouse_cool = True
                    else:
                        setting_bound = False
                        clicksel_prompt.hide(GP_BORDER_COLOR)
                        first_corner = None
                        mouse_cool = True
                else:
                    setting_bound = False
                    first_corner = None
                    clicksel_prompt.hide(GP_BORDER_COLOR)
        elif not mb_pressed:
            mouse_cool = False
        
        # Keyboard Shortcuts
        if not invalid_bounds and not is_typing:
            # Render button
            if keys_pressed[pygame.K_r] and not ren_cool:
                ren_cool = True
                render_button.is_click = True
            elif not keys_pressed[pygame.K_r]:
                ren_cool = False
            
            # Zoom function
            if keys_pressed[pygame.K_EQUALS] and not in_cool:
                in_cool = True
                render_button.is_click = True
                pan_or_zoom = True
                left_bound.text, right_bound.text = grapher.new_bounds(x_axis=True, transformation="in")
                lower_bound.text, upper_bound.text = grapher.new_bounds(x_axis=False, transformation="in")
            elif not keys_pressed[pygame.K_EQUALS]:
                in_cool = False
            
            if keys_pressed[pygame.K_MINUS] and not out_cool:
                out_cool = True
                render_button.is_click = True
                pan_or_zoom = True
                left_bound.text, right_bound.text = grapher.new_bounds(x_axis=True, transformation="out")
                lower_bound.text, upper_bound.text = grapher.new_bounds(x_axis=False, transformation="out")
            elif not keys_pressed[pygame.K_MINUS]:
                out_cool = False
            
            # Panning
            if keys_pressed[pygame.K_LEFT] and not l_cool:
                l_cool = True
                render_button.is_click = True
                pan_or_zoom = True
                left_bound.text, right_bound.text = grapher.new_bounds(x_axis=True, transformation="dec")
            elif not keys_pressed[pygame.K_LEFT]:
                l_cool = False
    
            if keys_pressed[pygame.K_RIGHT] and not r_cool:
                r_cool = True
                render_button.is_click = True
                pan_or_zoom = True
                left_bound.text, right_bound.text = grapher.new_bounds(x_axis=True, transformation="inc")
            elif not keys_pressed[pygame.K_RIGHT]:
                r_cool = False
    
            if keys_pressed[pygame.K_DOWN] and not d_cool:
                d_cool = True
                render_button.is_click = True
                pan_or_zoom = True
                lower_bound.text, upper_bound.text = grapher.new_bounds(x_axis=False, transformation="dec")
            elif not keys_pressed[pygame.K_DOWN]:
                d_cool = False
    
            if keys_pressed[pygame.K_UP] and not u_cool:
                u_cool = True
                render_button.is_click = True
                pan_or_zoom = True
                lower_bound.text, upper_bound.text = grapher.new_bounds(x_axis=False, transformation="inc")
            elif not keys_pressed[pygame.K_UP]:
                u_cool = False
        did_poz |= pan_or_zoom
        render_button.text = "refresh" if did_poz else "enter"
        render_button.draw()
        
        # Update resolutions
        invalid_res: bool = False
        something = res_box_x.update(events) or res_box_y.update(events)
        res_changed |= something
        if res_box_x.active:
            if keys_pressed[pygame.K_TAB] and not tab_cool:  # Tab switching
                res_box_x.active = False
                res_box_y.active = True
                tab_cool = True
            res_error.hide(GP_BORDER_COLOR)
            res_box_x.draw()
        if res_box_x.was_active:  # Then check if input is valid
            res_box_x.draw()
            for char in res_box_x.text:
                if char not in "0123456789":  # Since only integers are allowed
                    res_error.draw()
                    invalid_res = True
                    break
        
        if res_box_y.active:
            if keys_pressed[pygame.K_TAB] and not tab_cool:  # Tab switching
                res_box_x.active = True
                res_box_y.active = False
                tab_cool = True
            res_error.hide(GP_BORDER_COLOR)
            res_box_y.draw()
        if res_box_y.was_active:  # Then check if input is valid
            res_box_y.draw()
            for char in res_box_y.text:
                if char not in "0123456789":  # Since only integers are allowed
                    res_error.draw()
                    invalid_res = True
                    break
        if not invalid_res:
            try:
                if int(res_box_x.text) < 150 or int(res_box_y.text) < 150 \
                        or int(res_box_x.text) >= _res[0] - 150 or int(res_box_y.text) >= _res[1] - 400:
                    raise ValueError
            except ValueError:
                invalid_res = True
                res_error.draw()
        if not res_box_x.active and not res_box_y.active and not invalid_res and res_changed and not invalid_bounds:
            # Reset window with changed resolutions
            GRAPH_RES = int(res_box_x.text), int(res_box_y.text)
            WIN_RES = max(150 + GRAPH_RES[0], 450), 350 + GRAPH_RES[1]
            GRAPH_POS = int((WIN_RES[0] - GRAPH_RES[0]) * 0.5), 40
            pygame.display.set_mode(WIN_RES, pygame.DOUBLEBUF)
            grapher.reset(GRAPH_RES, GRAPH_POS, (float(eval(left_bound.text)), float(eval(right_bound.text))),
                          (float(eval(lower_bound.text)), float(eval(upper_bound.text))))
            # Allow for new window to have the same settings as previously
            dce_texts = (left_bound.text, right_bound.text, lower_bound.text, upper_bound.text,
                         enablers[0].on, enablers[1].on, enablers[2].on, enablers[3].on,
                         funcs[0].text, funcs[1].text, funcs[2].text, funcs[3].text)
            draw_config_elements()
            render_button.is_click = True
            res_changed = False
        
        # Check if function process is finished
        for i in range(len(funcs)):
            if proc_queue[i] is not None:
                if not proc_queue[i].is_alive():  # If plotting is finished
                    try:
                        grapher.graph_points[i] = mang_dict[i]
                        indicators[i].hide(BG_COLOR)
                        proc_queue[i] = None
                        del mang_dict[i]

                        # Cause function to be drawn
                        render_button.is_click = True
                        pan_or_zoom = True
                    except KeyError:
                        grapher.graph_points[i] = None

        if not keys_pressed[pygame.K_TAB]:
            tab_cool = False

        # Rendering graph
        if not invalid_bounds:
            if render_button.is_click:
                new_bounds: tuple = left_bound.text, right_bound.text, lower_bound.text, upper_bound.text
                new_funcs: tuple = tuple(func.text for func in funcs)
                
                if not pan_or_zoom:  # If new graph is requested
                    for process in proc_queue:  # Stop current graphing processes
                        if process is not None:
                            process.terminate()
                render_queue.clear()
                for idx, (indicator, enabler, func, color) in enumerate(zip(indicators, enablers, funcs, LINE_COLORS)):
                    if enabler.on:
                        if pan_or_zoom:  # Simple transform
                            valid_prompt: tuple[tuple, int] = grapher.validate_equation(func.text)
                            if valid_prompt[0]:
                                if valid_prompt[0][0] == "(y)" and 'y' not in valid_prompt[0][1] \
                                        or valid_prompt[0][0] == "(x)" and 'x' not in valid_prompt[0][1]:
                                    # x and y functions are fast enough to re-plot for each transform
                                    render_queue.append(Thread(target=grapher.function_graph,
                                                               args=(valid_prompt[0], indicator, color, LINE_WIDTH)))
                                else:  # Shifted iterative graphs will have missing points
                                    render_queue.append(Thread(target=grapher.draw_graph,
                                                               args=(idx, color, LINE_WIDTH)))
                        elif not grapher.graph_points[idx] or old_bounds != new_bounds or old_funcs != new_funcs:
                            # If the function different from before, render
                            # Runs if the render butter was pressed
                            did_poz = False
                            valid_prompt: tuple[tuple, int] = grapher.validate_equation(func.text)
                            if valid_prompt[0] and not invalid_funcs[idx]:
                                if valid_prompt[0][0] == "(y)" and 'y' not in valid_prompt[0][1] \
                                        or valid_prompt[0][0] == "(x)" and 'x' not in valid_prompt[0][1]:
                                    render_queue.append(Thread(target=grapher.function_graph,
                                                               args=(valid_prompt[0], indicator,
                                                                     color, LINE_WIDTH)))
                                    
                                else:
                                    if proc_queue[idx]:
                                        if proc_queue[idx].is_alive():  # Then stop current graphing process
                                            proc_queue[idx].terminate()
                                    proc_queue[idx] = Process(target=iterative_points,
                                                              args=(valid_prompt[0], grapher.x_bounds,
                                                                    grapher.y_bounds, grapher.range,
                                                                    grapher.resolution, mang_dict, idx))
                                    indicator.hide(BG_COLOR)
                                    indicator.draw()
                                    proc_queue[idx].start()
                                    # render_queue.append(Thread(target=grapher.iterative_graph,
                                    #                            args=(valid_prompt[0], indicator,
                                    #                                  color, LINE_WIDTH, idx)))
                                old_funcs[idx] = func.text
                            else:
                                print(f"func{idx} is an invalid function/relation")
                        
                grapher.reset(GRAPH_RES, GRAPH_POS, (float(eval(left_bound.text)), float(eval(right_bound.text))),
                              (float(eval(lower_bound.text)), float(eval(upper_bound.text))))
                grapher.clear_graph()
                for thread in render_queue:
                    thread.start()
                old_bounds = deepcopy(new_bounds)
        
        pygame.display.update()
        clock.tick(TICK)
    
    # Wait for all graphing processes to finish, then quit PyGame
    for thread in render_queue:
        thread.join()
    for process in proc_queue:
        if process is not None:
            process.terminate()
    pygame.quit()
    return None


if __name__ == "__main__":
    freeze_support()  # Fixes problems with multiprocessing module
    _res: tuple[int, int] = get_monitors()[0].width, get_monitors()[0].height  # Gets resolution of display
    
    graph_config_window()  # Open graph window
    exit(0)
