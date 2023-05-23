import pygame
import sys
from math import floor

### Font size converstion: 4px = 3pt

COLOR_BLACK = 0, 0, 0
COLOR_WHITE = 255, 255, 255

GRID_SIZE_PERCENTAGE = 85
SEGMENT_COUNT = 9
DEFAULT_FONT = pygame.font.get_default_font()

def main():
    pygame.init()
    size = 800, 600
    
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    screen.fill(COLOR_WHITE)
    grid = siphonGrid(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                segment_clicked = grid.mapPosToGridSegment(event.pos)
                if segment_clicked:
                    if event.button == 1:
                        segment_clicked.cycleResonator()
                    elif event.button == 3:
                        segment_clicked.resonator = None
            elif event.type == pygame.MOUSEWHEEL:
                segment_wheeled = grid.mapPosToGridSegment(pygame.mouse.get_pos())
                if segment_wheeled and segment_wheeled.resonator:
                    segment_wheeled.resonator.adjustIntensity(event.y)
        screen.fill(COLOR_WHITE)
        grid.render()
        pygame.display.flip()
    

class siphonGrid():

    def __init__(self, screen, segments=SEGMENT_COUNT, size=GRID_SIZE_PERCENTAGE, font=DEFAULT_FONT) -> None:
        self.screen = screen
        self.segments = segments
        self.size = size
        self.font = pygame.font.Font(font)
        self.init_grid() 
    
    def init_grid(self):

        # Generate grid container
        self.grid_container = pygame.Rect(0, 0, 0, 0)

        # Generate grid squares
        grid = []
        for i in range(self.segments):
            grid.append(list())
            for j in range(self.segments):
                grid[i].append(siphonGridSegment((i, j)))

        # Black out the harmonic resonator squares
        grid[floor(self.segments/2)][floor(self.segments/2)].blacked_out = True
        grid[floor(self.segments/2)][floor(self.segments/2)+1].blacked_out = True

        # Init labels
        self.labels_columns = []
        self.labels_rows = []
        for i in range(self.segments):
            self.labels_columns.append(self.font.render(encodeColumnNumber(i), True, COLOR_BLACK))
            self.labels_rows.append(self.font.render(str(self.segments-(i+1)), True, COLOR_BLACK))

        # Set class attribute and return grid
        self.grid = grid
        return grid
    
    # Resize the grid according to the surface size
    def resize_grid(self):
        self.calcGrid()
        self.grid_container.update(self.grid_left, self.grid_top, self.grid_size, self.grid_size)
        for i in range(self.segments):
            for j in range(self.segments):
                self.grid[i][j].rect.update(
                    self.grid_left + i * self.grid_section_size,
                    self.grid_top + self.grid_size - (j + 1) * self.grid_section_size,
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
            label_top = (self.grid_top) + (self.grid_section_size - self.labels_rows[i].get_height()) / 2 + self.grid_section_size * i
            label_left = (self.grid_left) - (self.grid_section_size - self.labels_rows[i].get_width()) / 2
            self.screen.blit(self.labels_rows[i], (label_left, label_top))
            # Draw column labels
            label_top = (self.grid_top + self.grid_size) + (self.grid_section_size - self.labels_columns[i].get_height()) / 4
            label_left = self.grid_left + (self.grid_section_size - self.labels_columns[i].get_width()) / 2 + self.grid_section_size * i
            self.screen.blit(self.labels_columns[i], (label_left, label_top))


            for j in range(self.segments):
                self.grid[i][j].render(self.screen)

    # Calculate dimensions for grid based on surface
    def calcGrid(self):
        screen_height = self.screen.get_height()
        screen_width = self.screen.get_width()
        screen_smallest = screen_height if screen_height < screen_width else screen_width
        self.grid_size = int(screen_smallest * self.size / 100)
        self.grid_left = int(screen_smallest * (((100 - self.size) / 2) / 100))
        self.grid_top = int(screen_smallest * (((100 - self.size) / 2) / 100))
        self.grid_section_size = floor(self.grid_size / self.segments)
        self.grid_size = self.grid_section_size * self.segments
    
    # Check if position lies within grid and returns the siphonGridSegment it's inside if it is, if it's not then returns None
    def mapPosToGridSegment(self, position):
        if self.grid_container.collidepoint(*position):
            for i in range(self.segments):
                for j in range(self.segments):
                    if self.grid[i][j].rect.collidepoint(*position):
                        return self.grid[i][j]
        return None

class siphonGridSegment():
    def __init__(self, position, rect: pygame.Rect = None, blacked_out = False) -> None:
        self.position = position
        if rect == None:
            rect = pygame.Rect(0, 0, 0, 0)
        self.rect = rect
        self.blacked_out = blacked_out
        self.resonator = None
    
    def cycleResonator(self):
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
    font_resonator = pygame.font.Font(DEFAULT_FONT)
    font_intensity = pygame.font.Font(DEFAULT_FONT, 10)
    intensity_font_map = [
        font_intensity.render('0', True, COLOR_BLACK),
        font_intensity.render('1', True, COLOR_BLACK),
        font_intensity.render('2', True, COLOR_BLACK),
        font_intensity.render('3', True, COLOR_BLACK),
        font_intensity.render('4', True, COLOR_BLACK),
    ]
    intensity = 1

    def __init__(self) -> None:
        pass

    def adjustIntensity(self, offset):
        self.intensity = (self.intensity + offset) % 5
    
    def renderOnGridSegment(self, surface: pygame.Surface, grid_square:pygame.Rect):
        type_top = grid_square.top + ((grid_square.height - self.text_render.get_height()) / 3)
        type_left = grid_square.left + ((grid_square.width - self.text_render.get_width()) / 2)
        surface.blit(self.text_render, (type_left, type_top))
        intensity_render = resonator.intensity_font_map[self.intensity]
        intensity_top = grid_square.top + ((grid_square.height - intensity_render.get_height()) / 3 * 2)
        intensity_left = grid_square.left + ((grid_square.width - intensity_render.get_width()) / 2)
        surface.blit(intensity_render, (intensity_left, intensity_top))

# Class for AX type resonators
class resonatorAX(resonator):
    text_render = resonator.font_resonator.render('AX', True, COLOR_BLACK) 
    def __init__(self) -> None:
        pass

# Class for AX type resonators
class resonatorSM(resonator):
    text_render = resonator.font_resonator.render('SM', True, COLOR_BLACK) 
    def __init__(self) -> None:
        pass

# function for encoding column number to letter
def encodeColumnNumber(number):
    return chr(65 + number)

# function for encoding column number to letter
def decodeColumnLetter(letter):
    return ord(letter) - 65

if __name__ == '__main__':
    main()