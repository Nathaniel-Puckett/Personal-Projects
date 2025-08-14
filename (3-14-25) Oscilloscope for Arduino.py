"""
Nathaniel Puckett
March 14, 2025
Oscilloscope for Arduino Type Devices
"""

import pygame as pg
import pyfirmata
import time
from collections import deque

class Button:
    def __init__(self, coords:tuple, text:str):
        """
        Initializer/constructor/__init__
        Parameters
        - coords : Coordinates formated as (x_initial, y_initial, width, height) in pixels
        - text : Overlaid text on button
        Returns
        - None
        """
        self.coords = coords
        self.text = text
    
    def draw(self, screen):
        """
        Draws the button on a given surface
        Parameters
        - screen : PyGame surface to apply the button to
        Returns
        - None
        """
        pg.draw.rect(screen, "black", self.coords)
        screen.blit(FONT.render(self.text, False, "white"), (self.coords[0] + self.coords[2]/4, self.coords[1] + self.coords[3]/4))

def is_clicked(x_1, y_1, x_2, y_2):
    """
    Takes in coordinates and returns if mouse was clicked between them
    Parameters
    - x_1, y_1 : initial x and y coordinates (top left) (pixels)
    - x_2, y_2 : width and height to check between (pixels)
    Returns
    - Boolean
    """
    return x_1 <= mouse[0] <= x_1 + x_2 and y_1 <= mouse[1] <= y_1 + y_2 

PORT = 'COM3'
BOARD = pyfirmata.Arduino(PORT)
BOARD_ITERATOR = pyfirmata.util.Iterator(BOARD)
BOARD_ITERATOR.start()

PIN_ONE = BOARD.get_pin('a:0:i')  #Analogue Input 0
PIN_TWO = BOARD.get_pin('a:1:i')  #Analogue Input 1
time.sleep(1)

WIDTH, HEIGHT = (1920, 1080)                                             #Screen dimensions
GRAPH_WIDTH, GRAPH_HEIGHT = (1280, 720)                                  #Graph dimensions
SHIFT_X, SHIFT_Y = ((WIDTH - GRAPH_WIDTH)/2, (HEIGHT - GRAPH_HEIGHT)/2)  #Pixels from edge of screen to edge of graph

DIVISIONS = 10                                                                            #Number of lines
TIME_DIVISION_PX, VOLTAGE_DIVISION_PX = (GRAPH_WIDTH/DIVISIONS, GRAPH_HEIGHT/DIVISIONS)   #Pixels per division
TIME_ZERO_PX, VOLTAGE_ZERO_PX = (GRAPH_WIDTH/2, GRAPH_HEIGHT/2)                           #Center coordinates (Origin)

BORDER_COORDS = [(SHIFT_X, SHIFT_Y), (WIDTH - SHIFT_X, SHIFT_Y), (WIDTH - SHIFT_X, HEIGHT - SHIFT_Y), (SHIFT_X, HEIGHT - SHIFT_Y)]

raw_time_data = deque([])     #List of times (s)
raw_voltage_data = deque([])  #List of voltages (V)
graphed_coords = deque([])    #Coordinates for time and voltage
dt = 0                        #Time between frames (s)
elapsed_time = 0              #Total elapsed time (s)
time_zoom = 1                 #Zoom factor (%)
voltage_zoom = 1              #Zoom factor (%)
time_offset = 0               #Time offset from zero (divisions)
voltage_offset = 0            #Voltage offset from zero (divisions)
trigger_value = 3             #Voltage value to pause at
num_triggered = 0             #Counter value, collects data past the trigger value
n = 0
m = 0

running = True
paused = False
trigger_check = False

#Refer to button class for formatting
TIME_ZOOM_IN_BUTTON = Button((70, 200, 50, 50), "T+")
TIME_ZOOM_OUT_BUTTON = Button((130, 200, 50, 50), "T-")
VOLTAGE_ZOOM_IN_BUTTON = Button((70, 300, 50, 50), "V+")
VOLTAGE_ZOOM_OUT_BUTTON = Button((130, 300, 50, 50), "V-")
TIME_SHIFT_UP_BUTTON = Button((70, 400, 50, 50), "←")
TIME_SHIFT_DOWN_BUTTON = Button((130, 400, 50, 50), "→")
VOLTAGE_SHIFT_UP_BUTTON = Button((70, 500, 50, 50), "↑")
VOLTAGE_SHIFT_DOWN_BUTTON = Button((130, 500, 50, 50), "↓")
PAUSE_BUTTON = Button((70, 600, 110, 50), "Pause")
TRIGGER_BUTTON = Button((70, 700, 110, 50), "Trigger")

BUTTONS = (TIME_ZOOM_IN_BUTTON, TIME_ZOOM_OUT_BUTTON, VOLTAGE_ZOOM_IN_BUTTON, VOLTAGE_ZOOM_OUT_BUTTON, 
           TIME_SHIFT_UP_BUTTON, TIME_SHIFT_DOWN_BUTTON, VOLTAGE_SHIFT_UP_BUTTON, VOLTAGE_SHIFT_DOWN_BUTTON, 
           PAUSE_BUTTON, TRIGGER_BUTTON
           )

pg.init()
SCREEN = pg.display.set_mode((WIDTH, HEIGHT))
GRAPH = pg.Surface((GRAPH_WIDTH, GRAPH_HEIGHT))
SCREEN.fill("grey")
GRAPH.fill("white")
FONT = pg.font.SysFont("Arial", 20)
CLOCK = pg.time.Clock()

while running:

    mouse = pg.mouse.get_pos()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            #Exits the program when clicking [x]
            running = False
            BOARD.exit()
        
        if event.type == pg.MOUSEBUTTONDOWN:
            #Checks to see if mouse clicked on a button
            #Zooms in or out by some factor
            if is_clicked(*TIME_ZOOM_IN_BUTTON.coords):
                time_zoom *= 2
            if is_clicked(*TIME_ZOOM_OUT_BUTTON.coords):
                time_zoom *= 0.5
            if is_clicked(*VOLTAGE_ZOOM_IN_BUTTON.coords):
                voltage_zoom *= 2
            if is_clicked(*VOLTAGE_ZOOM_OUT_BUTTON.coords):
                voltage_zoom *= 0.5

            #Offsets by one adjusted division
            if is_clicked(*TIME_SHIFT_UP_BUTTON.coords):
                time_offset += TIME_DIVISION_PX / time_zoom
            if is_clicked(*TIME_SHIFT_DOWN_BUTTON.coords):
                time_offset -= TIME_DIVISION_PX / time_zoom
            if is_clicked(*VOLTAGE_SHIFT_UP_BUTTON.coords):
                voltage_offset -= VOLTAGE_DIVISION_PX / voltage_zoom
            if is_clicked(*VOLTAGE_SHIFT_DOWN_BUTTON.coords):
                voltage_offset += VOLTAGE_DIVISION_PX / voltage_zoom
            
            if is_clicked(*PAUSE_BUTTON.coords):
                paused = not paused
            if is_clicked(*TRIGGER_BUTTON.coords):
                trigger_check = True

    for button in BUTTONS:
        button.draw(SCREEN)

    elapsed_time += dt
    raw_time_data.append(elapsed_time)

    #Gets the voltage (if available) and converts it to units of voltage
    is_float = isinstance(PIN_ONE.read(), float) and isinstance(PIN_TWO.read(), float)
    voltage_measured_difference = 5*(PIN_TWO.read() - PIN_ONE.read()) if is_float else 0 #Pins read voltage as a fraction of 5 volts, eg. 0.5 = 2.5V
    raw_voltage_data.append(voltage_measured_difference)

    #Adjusts each coordinate based on offset, zoom
    t_coords = [2*TIME_ZERO_PX + (((t - elapsed_time) * TIME_DIVISION_PX) - time_offset) * time_zoom for t in raw_time_data] 
    v_coords = [VOLTAGE_ZERO_PX - ((v * VOLTAGE_DIVISION_PX) - voltage_offset) * voltage_zoom for v in raw_voltage_data]

    #Combines t_coords and v_coords into (x, y) coords
    graphed_coords = deque(list(zip(t_coords, v_coords)))

    if len(graphed_coords) > 10000:
        graphed_coords.popleft()
        raw_time_data.popleft()
        raw_voltage_data.popleft()

    #Gives the graph a border on the screen
    pg.draw.lines(SCREEN, "black", True, BORDER_COORDS, 3)

    #Draws the division lines and corresponding values
    for i in range(DIVISIONS + 1):
        time_division_shift = i * TIME_DIVISION_PX
        pg.draw.line(GRAPH, "black", (GRAPH_WIDTH - time_division_shift, 0), (GRAPH_WIDTH - time_division_shift, GRAPH_HEIGHT), 3 if (GRAPH_WIDTH - time_division_shift) == TIME_ZERO_PX else 1)
    
        voltage_division_shift = i * VOLTAGE_DIVISION_PX
        pg.draw.line(GRAPH, "black", (0, GRAPH_HEIGHT - voltage_division_shift), (GRAPH_WIDTH, GRAPH_HEIGHT - voltage_division_shift), 3 if (GRAPH_HEIGHT - voltage_division_shift) == VOLTAGE_ZERO_PX else 1)
        voltage_number_location = HEIGHT - (voltage_division_shift + SHIFT_Y) - 10
        SCREEN.blit(FONT.render(f"{round((5 - DIVISIONS + i)/voltage_zoom + (voltage_offset/VOLTAGE_DIVISION_PX), 2)}", False, "black"), (SHIFT_X - 50, voltage_number_location))

    #Draws the time per division
    SCREEN.blit(FONT.render(f"Time Division : {round(1 * 1000 / time_zoom, 2)} ms" , False, "black"), (WIDTH/2 - 100, HEIGHT - SHIFT_Y + 10))
    SCREEN.blit(FONT.render(f"Voltage Division : {round(1 / voltage_zoom, 2)} V", False, "black"), (WIDTH/2 - 100, HEIGHT - SHIFT_Y + 30))
    SCREEN.blit(FONT.render(f"Elapsed Time : {round(elapsed_time, 2)} s", False, "black"), (WIDTH/2 - 100, HEIGHT - SHIFT_Y + 50))
    SCREEN.blit(FONT.render(f"FPS : {round(1 / dt if dt else 1, 10)} FPS", False, "black"), (WIDTH/2 - 100, HEIGHT - SHIFT_Y + 70))

    #Draws the time, voltage coordinates
    if len(graphed_coords) > 1:
        pg.draw.lines(GRAPH, "blue", False, graphed_coords, 3)

    if trigger_check:
        if voltage_measured_difference >= trigger_value:
            num_triggered += 1
            if num_triggered == 20:
                trigger_check = False
                num_triggered = 0
                paused = True

    #Refreshes the page
    pg.display.flip()

    while paused:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                #Exits the program when clicking [x]
                paused = False
                running = False
                BOARD.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                #Checks to see if mouse clicked on a button
                #Zooms in or out by some factor
                if is_clicked(*TIME_ZOOM_IN_BUTTON.coords):
                    time_zoom *= 2
                if is_clicked(*TIME_ZOOM_OUT_BUTTON.coords):
                    time_zoom *= 0.5
                if is_clicked(*VOLTAGE_ZOOM_IN_BUTTON.coords):
                    voltage_zoom *= 2
                if is_clicked(*VOLTAGE_ZOOM_OUT_BUTTON.coords):
                    voltage_zoom *= 0.5

                #Offsets by one adjusted division
                if is_clicked(*TIME_SHIFT_UP_BUTTON.coords):
                    time_offset += TIME_DIVISION_PX / time_zoom
                if is_clicked(*TIME_SHIFT_DOWN_BUTTON.coords):
                    time_offset -= TIME_DIVISION_PX / time_zoom
                if is_clicked(*VOLTAGE_SHIFT_UP_BUTTON.coords):
                    voltage_offset -= VOLTAGE_DIVISION_PX / voltage_zoom
                if is_clicked(*VOLTAGE_SHIFT_DOWN_BUTTON.coords):
                    voltage_offset += VOLTAGE_DIVISION_PX / voltage_zoom
                
                if is_clicked(*PAUSE_BUTTON.coords):
                    paused = not paused
                if is_clicked(*TRIGGER_BUTTON.coords):
                    trigger_check = True

        mouse = pg.mouse.get_pos()

        for button in BUTTONS:
            button.draw(SCREEN)

        t_coords = [2*TIME_ZERO_PX + (((t - elapsed_time) * TIME_DIVISION_PX) - time_offset) * time_zoom for t in raw_time_data] 
        v_coords = [VOLTAGE_ZERO_PX - ((v * VOLTAGE_DIVISION_PX) - voltage_offset) * voltage_zoom for v in raw_voltage_data]

        #Combines t_coords and v_coords into (x, y) coords
        graphed_coords = list(zip(t_coords, v_coords))

        pg.draw.lines(SCREEN, "black", True, BORDER_COORDS, 3)

        #Draws the division lines and corresponding values
        for i in range(DIVISIONS + 1):
            time_division_shift = i * TIME_DIVISION_PX
            pg.draw.line(GRAPH, "black", (GRAPH_WIDTH - time_division_shift, 0), (GRAPH_WIDTH - time_division_shift, GRAPH_HEIGHT), 3 if (GRAPH_WIDTH - time_division_shift) == TIME_ZERO_PX else 1)
        
            voltage_division_shift = i * VOLTAGE_DIVISION_PX
            pg.draw.line(GRAPH, "black", (0, GRAPH_HEIGHT - voltage_division_shift), (GRAPH_WIDTH, GRAPH_HEIGHT - voltage_division_shift), 3 if (GRAPH_HEIGHT - voltage_division_shift) == VOLTAGE_ZERO_PX else 1)
            voltage_number_location = HEIGHT - (voltage_division_shift + SHIFT_Y) - 10
            SCREEN.blit(FONT.render(f"{round((5 - DIVISIONS + i)/voltage_zoom + (voltage_offset/VOLTAGE_DIVISION_PX), 2)}", False, "black"), (SHIFT_X - 50, voltage_number_location))

        #Draws the time per division
        SCREEN.blit(FONT.render(f"Time Division : {round(1 * 1000 / time_zoom, 2)} ms" , False, "black"), (WIDTH/2 - 100, HEIGHT - SHIFT_Y + 10))
        SCREEN.blit(FONT.render(f"Voltage Division : {round(1 / voltage_zoom, 2)} V", False, "black"), (WIDTH/2 - 100, HEIGHT - SHIFT_Y + 30))
        SCREEN.blit(FONT.render(f"Elapsed Time : {round(elapsed_time, 2)} s", False, "black"), (WIDTH/2 - 100, HEIGHT - SHIFT_Y + 50))
        SCREEN.blit(FONT.render(f"FPS : {round(1 / dt if dt else 1, 10)} FPS", False, "black"), (WIDTH/2 - 100, HEIGHT - SHIFT_Y + 70))

        #Draws the time, voltage coordinates
        pg.draw.lines(GRAPH, "blue", False, graphed_coords, 3)

        #refreshes the page
        pg.display.flip()

        SCREEN.fill("grey")
        SCREEN.blit(GRAPH, (SHIFT_X, SHIFT_Y))
        GRAPH.fill("white")

    SCREEN.fill("grey")
    SCREEN.blit(GRAPH, (SHIFT_X, SHIFT_Y))
    GRAPH.fill("white")
    
    dt = CLOCK.tick(1000) / 1000 #s

pg.quit()