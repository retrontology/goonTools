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
    size = 900, 600
    
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    screen.fill(COLOR_WHITE)
    grid = siphonGrid(screen)
    sidebar = gridSidebar(grid, screen)
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
        sidebar.render()
        pygame.display.flip()
    

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
        self.lateral_resonance = 0
        self.vertical_resonance = 0
        self.shear = 0
        for i in range(self.segments):
            for j in range(self.segments):
                if self.grid[i][j].resonator:
                    self.lateral_resonance += (self.grid[i][j].lateral_offset * self.grid[i][j].resonator.intensity)
                    self.vertical_resonance += (self.grid[i][j].vertical_offset * self.grid[i][j].resonator.intensity)
    
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
        font_intensity.render('0', True, COLOR_BLACK),
        font_intensity.render('1', True, COLOR_BLACK),
        font_intensity.render('2', True, COLOR_BLACK),
        font_intensity.render('3', True, COLOR_BLACK),
        font_intensity.render('4', True, COLOR_BLACK),
    ]
    intensity = 1

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

# Class for AX type resonators
class resonatorSM(resonator):
    text_render = resonator.font_resonator.render('SM', True, COLOR_BLACK) 

class gridSidebar():

    def __init__(self, grid: siphonGrid, screen: pygame.Surface) -> None:
        self.grid = grid
        self.screen = screen
        self.initSidebar()
    
    def initSidebar(self):
        self.font = pygame.font.Font(DEFAULT_FONT, 20)
        self.container = pygame.Rect(0, 0, 0, 0)
        self.label_vertical_resonance = self.font.render('Vertical Resonance: ', True, COLOR_BLACK)
        self.label_lateral_resonance = self.font.render('Lateral Resonance: ', True, COLOR_BLACK)
        self.label_shear = self.font.render('Shear: ', True, COLOR_BLACK)

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
    
    def render(self):
        self.resizeSidebar()
        #pygame.draw.rect(self.screen, COLOR_BLACK, self.container, 2)

        # Vertical resonance label
        vertical_resonance_rect = self.screen.blit(
            self.label_vertical_resonance, 
            (self.container.left, self.container.top + 20)
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
        
        # Lateral resonance label
        lateral_resonance_rect = self.screen.blit(
            self.label_lateral_resonance, 
            (self.container.left, self.container.top + 20 * 2)
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


# function for encoding column number to letter
def encodeColumnNumber(number):
    return chr(65 + number)

# function for encoding column number to letter
def decodeColumnLetter(letter):
    return ord(letter) - 65

if __name__ == '__main__':
    main()