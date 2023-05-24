import pygame
import sys
import tkinter
import tkinter.filedialog
from math import floor

### Font size converstion: 4px = 3pt

COLOR_BLACK = 0, 0, 0
COLOR_WHITE = 255, 255, 255
COLOR_GREY = 200, 200, 200

GRID_SIZE_PERCENTAGE = 85
SEGMENT_COUNT = 9
DEFAULT_FONT = pygame.font.get_default_font()

def main():
    pygame.init()
    size = 900, 600
    
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    screen.fill(COLOR_WHITE)
    grid = siphonGrid(screen)
    sidebar = gridSidebar(grid, screen)
    buttons = [
        sidebar.button_load,
        sidebar.button_save
    ]
    update_screen = True
    while True:
        event =  pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            segment_clicked = grid.mapPosToGridSegment(event.pos)
            if segment_clicked:
                if event.button == 1:
                    segment_clicked.cycleResonator()
                    update_screen = True
                elif event.button == 3:
                    segment_clicked.resonator = None
                    update_screen = True
            else:
                for button in buttons:
                    if button.rect.collidepoint(event.pos):
                        button.click()
        elif event.type == pygame.MOUSEWHEEL:
            segment_wheeled = grid.mapPosToGridSegment(pygame.mouse.get_pos())
            if segment_wheeled and segment_wheeled.resonator:
                segment_wheeled.resonator.adjustIntensity(event.y)
                update_screen = True
        elif event.type == pygame.VIDEORESIZE:
            update_screen = True
        if update_screen:
            screen.fill(COLOR_WHITE)
            grid.render()
            sidebar.render()
            pygame.display.flip()
            update_screen = False
    

class siphonGrid():

    def __init__(self, screen, segments=SEGMENT_COUNT, size=GRID_SIZE_PERCENTAGE, font=DEFAULT_FONT) -> None:
        self.screen = screen
        self.segments = segments
        self.size = size
        self.font = pygame.font.Font(font, 24)
        self.init_grid()
    
    def init_grid(self):

        # Generate grid container
        self.grid_container = pygame.Rect(0, 0, 0, 0)

        # Generate grid squares
        grid_midpoint = floor(self.segments/2)
        grid = []
        for i in range(self.segments):
            if grid_midpoint == i:
                lateral_offset = 0
            else:
                lateral_polarity = (i - grid_midpoint) / abs((i - grid_midpoint))
                lateral_distance = abs(i - grid_midpoint)
                lateral_offset = lateral_polarity * (2 ** abs(grid_midpoint-lateral_distance))
            grid.append(list())
            for j in range(self.segments):
                if grid_midpoint == j:
                    vertical_offset = 0
                else:
                    vertical_polarity = (j - grid_midpoint) / abs((j - grid_midpoint))
                    vertical_distance = abs(j - grid_midpoint)
                    vertical_offset = vertical_polarity * (2 ** abs(grid_midpoint-vertical_distance))
                grid[i].append(siphonGridSegment((i, j), vertical_offset, lateral_offset))

        # Black out the harmonic resonator squares
        grid[floor(self.segments/2)][floor(self.segments/2)].blacked_out = True
        grid[floor(self.segments/2)][floor(self.segments/2)+1].blacked_out = True

        # Init labels
        self.labels_columns = []
        self.labels_rows = []
        for i in range(self.segments):
            self.labels_columns.append(self.font.render(encodeColumnNumber(i), True, COLOR_BLACK))
            self.labels_rows.append(self.font.render(str(self.segments-(i+1)), True, COLOR_BLACK))

        # Init resonance variables
        self.vertical_resonance = 0
        self.lateral_resonance = 0
        self.shear = 0
        self.eeu = 0

        # Set class attribute and return grid
        self.grid = grid
        return grid
    
    # Resize the grid according to the surface size
    def resize_grid(self):
        screen_height = self.screen.get_height()
        screen_width = self.screen.get_width()
        screen_smallest = screen_height if screen_height < screen_width else screen_width
        grid_size = int(screen_smallest * self.size / 100)
        grid_left = int(screen_smallest * (((100 - self.size) / 2) / 100))
        grid_top = int(screen_smallest * (((100 - self.size) / 2) / 100))
        self.grid_section_size = floor(grid_size / self.segments)
        grid_size = self.grid_section_size * self.segments
        self.grid_container.update(grid_left, grid_top, grid_size, grid_size)
        for i in range(self.segments):
            for j in range(self.segments):
                self.grid[i][j].rect.update(
                    grid_left + i * self.grid_section_size,
                    grid_top + grid_size - (j + 1) * self.grid_section_size,
                    self.grid_section_size,
                    self.grid_section_size
                )

    # Render the grid on the surface
    def render(self, screen: pygame.Surface = None):
        if screen:
            self.screen = screen
        
        self.resize_grid()

        pygame.draw.rect(self.screen, COLOR_BLACK, self.grid_container, 2)

        for i in range(self.segments):

            # Draw row labels
            label_top = (self.grid_container.top) + (self.grid_section_size - self.labels_rows[i].get_height()) / 2 + self.grid_section_size * i
            label_left = (self.grid_container.left) - (self.grid_section_size - self.labels_rows[i].get_width()) / 2
            self.screen.blit(self.labels_rows[i], (label_left, label_top))
            # Draw column labels
            label_top = (self.grid_container.top + self.grid_container.width) + (self.grid_section_size - self.labels_columns[i].get_height()) / 4
            label_left = self.grid_container.left + (self.grid_section_size - self.labels_columns[i].get_width()) / 2 + self.grid_section_size * i
            self.screen.blit(self.labels_columns[i], (label_left, label_top))

            for j in range(self.segments):
                self.grid[i][j].render(self.screen)
            
        self.calcGrid()

    # Calculate resonance variables
    def calcGrid(self):
        lateral_positive = 0
        lateral_negative = 0
        vertical_positive = 0
        vertical_negative = 0
        shear_mitigation = 0
        eeu = 0
        for i in range(self.segments):
            for j in range(self.segments):
                grid_square = self.grid[i][j]
                if grid_square.resonator:
                    if type(grid_square.resonator) == resonatorAX:
                        if grid_square.lateral_offset < 0:
                            lateral_negative -= grid_square.lateral_offset * grid_square.resonator.intensity
                        else:
                            lateral_positive += grid_square.lateral_offset * grid_square.resonator.intensity
                        if grid_square.vertical_offset < 0:
                            vertical_negative -= grid_square.vertical_offset * grid_square.resonator.intensity
                        else:
                            vertical_positive += grid_square.vertical_offset * grid_square.resonator.intensity
                    elif type(grid_square.resonator) == resonatorSM:
                        mitigation_offset = max(abs(grid_square.lateral_offset), abs(grid_square.vertical_offset))
                        shear_mitigation += mitigation_offset * grid_square.resonator.intensity
                    eeu += grid_square.resonator.intensity
        self.lateral_resonance = int(lateral_positive - lateral_negative)
        self.vertical_resonance = int(vertical_positive - vertical_negative)
        self.shear = int(min(lateral_positive, lateral_negative) + min(vertical_positive, vertical_negative)) * 2 - int(shear_mitigation)
        if self.shear < 0: self.shear = 0
        self.eeu = int(eeu)
    
    # Check if position lies within grid and returns the siphonGridSegment it's inside if it is, if it's not then returns None
    def mapPosToGridSegment(self, position):
        if self.grid_container.collidepoint(*position):
            for i in range(self.segments):
                for j in range(self.segments):
                    if self.grid[i][j].rect.collidepoint(*position):
                        return self.grid[i][j]
        return None

class siphonGridSegment():
    def __init__(self, position, vertical_offset, lateral_offset, rect: pygame.Rect = None, blacked_out = False) -> None:
        self.position = position
        self.vertical_offset = vertical_offset
        self.lateral_offset = lateral_offset
        if rect == None:
            rect = pygame.Rect(0, 0, 0, 0)
        self.rect = rect
        self.blacked_out = blacked_out
        self.resonator = None
    
    def cycleResonator(self):
        if self.blacked_out:
            self.resonator = None
        else:
            if self.resonator == None:
                self.resonator = resonatorAX()
            elif type(self.resonator) is resonatorAX:
                self.resonator = resonatorSM()
            elif type(self.resonator) is resonatorSM:
                self.resonator = None
    
    def getEncodedPosition(self):
        return (encodeColumnNumber(self.position[0]), self.position[1])
    
    def render(self, surface: pygame.Surface):
        width = 0 if self.blacked_out else 1
        grid_square = pygame.draw.rect(surface, COLOR_BLACK, self.rect, width)
        if self.resonator:
            self.resonator.renderOnGridSegment(surface, grid_square)

# Dummy parent class for resonators
class resonator():
    pygame.font.init()
    font_resonator = pygame.font.Font(DEFAULT_FONT, 16)
    font_intensity = pygame.font.Font(DEFAULT_FONT, 14)
    intensity_font_map = [
        font_intensity.render('1', True, COLOR_BLACK),
        font_intensity.render('2', True, COLOR_BLACK),
        font_intensity.render('3', True, COLOR_BLACK),
        font_intensity.render('4', True, COLOR_BLACK),
    ]
    intensity = 1

    def adjustIntensity(self, offset):
        self.intensity = self.intensity + offset
        if self.intensity > self.max_intensity: self.intensity = self.max_intensity
        if self.intensity < 1: self.intensity = 1
    
    def renderOnGridSegment(self, surface: pygame.Surface, grid_square:pygame.Rect):
        type_top = grid_square.top + ((grid_square.height - self.text_render.get_height()) / 3)
        type_left = grid_square.left + ((grid_square.width - self.text_render.get_width()) / 2)
        surface.blit(self.text_render, (type_left, type_top))
        intensity_render = resonator.intensity_font_map[self.intensity-1]
        intensity_top = grid_square.top + ((grid_square.height - intensity_render.get_height()) / 3 * 2)
        intensity_left = grid_square.left + ((grid_square.width - intensity_render.get_width()) / 2)
        surface.blit(intensity_render, (intensity_left, intensity_top))

# Class for AX type resonators
class resonatorAX(resonator):
    text_render = resonator.font_resonator.render('AX', True, COLOR_BLACK)
    max_intensity = 4

# Class for AX type resonators
class resonatorSM(resonator):
    text_render = resonator.font_resonator.render('SM', True, COLOR_BLACK)
    max_intensity = 3

class gridSidebar():

    def __init__(self, grid: siphonGrid, screen: pygame.Surface) -> None:
        self.grid = grid
        self.screen = screen
        self.initSidebar()
    
    def initSidebar(self):
        self.font = pygame.font.Font(DEFAULT_FONT, 20)
        self.container = pygame.Rect(0, 0, 0, 0)
        self.label_lateral_resonance = self.font.render('Lateral Resonance: ', True, COLOR_BLACK)
        self.label_vertical_resonance = self.font.render('Vertical Resonance: ', True, COLOR_BLACK)
        self.label_shear = self.font.render('Shear Value: ', True, COLOR_BLACK)
        self.label_eeu = self.font.render('EEU Per Cycle: ', True, COLOR_BLACK)
        self.button_save = button('SAVE', saveFile, self.grid, self.screen)
        self.button_load = button('LOAD', loadFile, self.grid, self.screen)
        

    def resizeSidebar(self):
        screen_width = self.screen.get_width()
        container_top = self.grid.grid_container.top
        container_left = self.grid.grid_container.left * 2 + self.grid.grid_container.width
        container_height = self.grid.grid_container.height
        container_width = screen_width - (self.grid.grid_container.left * 3 + self.grid.grid_container.width)
        self.container.update(
            container_left,
            container_top,
            container_width,
            container_height
        )
        button_height = 40
        button_width = 120
        self.button_save.rect.update(
            container_left, 
            container_top + container_height - button_height,
            button_width,
            button_height
        )
        self.button_load.rect.update(
            self.button_save.rect.left + button_width*1.25, 
            container_top + container_height - button_height,
            button_width,
            button_height
        )
    
    def render(self):
        self.resizeSidebar()
        #pygame.draw.rect(self.screen, COLOR_BLACK, self.container, 2)

        # Lateral resonance label
        lateral_resonance_rect = self.screen.blit(
            self.label_lateral_resonance, 
            (self.container.left, self.container.top + 20)
        )
        lateral_resonance_render = self.font.render(
            str(self.grid.lateral_resonance),
            True,
            COLOR_BLACK
        )
        self.screen.blit(
            lateral_resonance_render,
            (
                lateral_resonance_rect.left + lateral_resonance_rect.width,
                lateral_resonance_rect.top 
            )
        )

        # Vertical resonance label
        vertical_resonance_rect = self.screen.blit(
            self.label_vertical_resonance, 
            (self.container.left, self.container.top + 20 * 2)
        )
        vertical_resonance_render = self.font.render(
            str(self.grid.vertical_resonance),
            True,
            COLOR_BLACK
        )
        self.screen.blit(
            vertical_resonance_render,
            (
                vertical_resonance_rect.left + vertical_resonance_rect.width,
                vertical_resonance_rect.top 
            )
        )
        
        # Shear label
        shear_rect = self.screen.blit(
            self.label_shear, 
            (self.container.left, self.container.top + 20 * 3)
        )
        shear_render = self.font.render(
            str(self.grid.shear),
            True,
            COLOR_BLACK
        )
        self.screen.blit(
            shear_render,
            (
                shear_rect.left + shear_rect.width,
                shear_rect.top 
            )
        )

        # EEU label
        eeu_rect = self.screen.blit(
            self.label_eeu, 
            (self.container.left, self.container.top + 20 * 4)
        )
        eeu_render = self.font.render(
            str(self.grid.eeu),
            True,
            COLOR_BLACK
        )
        self.screen.blit(
            eeu_render,
            (
                eeu_rect.left + eeu_rect.width,
                eeu_rect.top 
            )
        )

        # Buttons
        self.button_load.render()
        self.button_save.render()

class button():

    font = pygame.font.Font(DEFAULT_FONT, 24)

    def __init__(self, text, callback, grid: siphonGrid, screen: pygame.Surface, rect: pygame.Rect = None) -> None:
        self.text = text
        self.callback = callback
        self.grid = grid
        self.screen = screen
        self.text_render = button.font.render(self.text, True, COLOR_BLACK)
        if rect == None:
            self.rect = pygame.Rect(0, 0, 0, 0)
        else:
            self.rect = rect
    
    def render(self):
        pygame.draw.rect(self.screen, COLOR_GREY, self.rect, 0)
        pygame.draw.rect(self.screen, COLOR_BLACK, self.rect, 3)
        text_top = self.rect.top + (self.rect.height - self.text_render.get_height()) / 2
        text_left = self.rect.left + (self.rect.width - self.text_render.get_width()) / 2
        self.screen.blit(self.text_render, (text_left, text_top))

    def click(self):
        self.callback(self.grid)

# Function to pick a file for saving/loading
def promptFile():
    top = tkinter.Tk()
    top.withdraw()
    file_name = tkinter.filedialog.askopenfilename(parent=top)
    top.destroy()
    return file_name

def saveFile(grid: siphonGrid):
    print('you saved :)')

def loadFile(grid: siphonGrid):
    print('you loaded :)')

# function for encoding column number to letter
def encodeColumnNumber(number):
    return chr(65 + number)

# function for encoding column number to letter
def decodeColumnLetter(letter):
    return ord(letter) - 65

if __name__ == '__main__':
    main()