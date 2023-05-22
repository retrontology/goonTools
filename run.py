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
    size = width, height = 800, 600
    
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    screen.fill(COLOR_WHITE)
    grid = siphonGrid(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
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

        self.calcGrid()

        grid = []
        for i in range(self.segments):
            grid.append(list())
            for j in range(self.segments):
                grid[i].append(siphonGridSegment(pygame.Rect(
                    self.grid_left + i * self.grid_section_size,
                    self.grid_top + j * self.grid_section_size,
                    self.grid_section_size,
                    self.grid_section_size
                )))

        grid[floor(self.segments/2)][floor(self.segments/2)].blacked_out = True
        grid[floor(self.segments/2)][floor(self.segments/2)-1].blacked_out = True

        self.labels_columns = []
        self.labels_rows = []
        for i in range(self.segments):
            self.labels_columns.append(self.font.render(chr(65+i), True, COLOR_BLACK))
            self.labels_rows.append(self.font.render(str(i), True, COLOR_BLACK))

        self.grid = grid
        return grid
    
    def resize_grid(self):
        self.calcGrid()
        for i in range(self.segments):
            for j in range(self.segments):
                self.grid[i][j].rect.update(
                    self.grid_left + i * self.grid_section_size,
                    self.grid_top + j * self.grid_section_size,
                    self.grid_section_size,
                    self.grid_section_size
                )

    def render(self, screen: pygame.Surface = None):
        if screen:
            self.screen = screen
        
        self.resize_grid()

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

    
    def calcGrid(self):
        screen_height = self.screen.get_height()
        screen_width = self.screen.get_width()
        screen_smallest = screen_height if screen_height < screen_width else screen_width
        self.grid_size = int(screen_smallest * self.size / 100)
        self.grid_left = int(screen_smallest * (((100 - self.size) / 2) / 100))
        self.grid_top = int(screen_smallest * (((100 - self.size) / 2) / 100))
        self.grid_section_size = floor(self.grid_size / self.segments)
        

class siphonGridSegment():
    def __init__(self, rect: pygame.Rect, blacked_out = False) -> None:
        self.rect = rect
        self.blacked_out = blacked_out

if __name__ == '__main__':
    main()