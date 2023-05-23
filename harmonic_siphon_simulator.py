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
                        print(f"Left mouse button pressed on {segment_clicked.getPosition()}")
                    elif event.button == 3:
                        print(f"Right mouse button pressed on {segment_clicked.getPosition()}")
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

        pygame.draw.rect(self.screen, COLOR_BLACK, self.grid_container, 1)

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
                if self.grid[i][j].blacked_out:
                    width = 0
                else:
                    width = 1
                pygame.draw.rect(self.screen, COLOR_BLACK, self.grid[i][j].rect, width)

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
    
    def getPosition(self):
        return (encodeColumnNumber(self.position[0]), self.position[1])
    

# function for encoding column number to letter
def encodeColumnNumber(number):
    return chr(65 + number)

# function for encoding column number to letter
def decodeColumnLetter(letter):
    return ord(letter) - 65

if __name__ == '__main__':
    main()