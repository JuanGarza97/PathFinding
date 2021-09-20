import pygame
import math
from queue import PriorityQueue

HEIGHT = 400
WIDTH = 400

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (255, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node:

    def __init__(self, row: int, column: int, height: int, width: int, total_rows: int, diagonal: bool = False) -> None:
        self.row = row
        self.column = column
        self.x = row * width
        self.y = column * height
        self.color = WHITE
        self.neighbors = []
        self.height = height
        self.width = width
        self.total_rows = total_rows
        self.diagonal = diagonal

    def get_neighbors(self):
        return self.neighbors

    def get_pos(self) -> [int, int]:
        return self.row, self.column

    def is_closed(self) -> bool:
        return self.color == RED

    def is_open(self) -> bool:
        return self.color == GREEN

    def is_barrier(self) -> bool:
        return self.color == BLACK

    def is_start(self) -> bool:
        return self.color == ORANGE

    def is_end(self) -> bool:
        return self.color == TURQUOISE

    def reset(self) -> None:
        self.color = WHITE

    def make_closed(self) -> None:
        self.color = RED

    def make_open(self) -> None:
        self.color = GREEN

    def make_barrier(self) -> None:
        self.color = BLACK

    def make_start(self) -> None:
        self.color = ORANGE

    def make_end(self) -> None:
        self.color = TURQUOISE

    def make_path(self) -> None:
        self.color = PURPLE

    def draw(self, win: pygame.display) -> None:
        pygame.draw.rect(win, self.color, (self.x, self.y, self.height, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []

        if self.diagonal:
            # DOWN RIGHT
            if self.row < self.total_rows - 1 and self.column < self.total_rows - 1 and not grid[self.row + 1][self.column + 1].is_barrier():
                self.neighbors.append(grid[self.row + 1][self.column + 1])
            # UP RIGHT
            if self.row > 0 and self.column < self.total_rows - 1 and not grid[self.row - 1][self.column + 1].is_barrier():
                self.neighbors.append(grid[self.row - 1][self.column + 1])
            # DOWN LEFT
            if self.row < self.total_rows - 1 and self.column > 0 and not grid[self.row + 1][self.column - 1].is_barrier():
                self.neighbors.append(grid[self.row + 1][self.column - 1])
            # UP LEFT
            if self.row > 0 and self.column > 0 and not grid[self.row - 1][self.column - 1].is_barrier():
                self.neighbors.append(grid[self.row - 1][self.column - 1])

        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.column].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.column])
        # UP
        if self.row > 0 and not grid[self.row - 1][self.column].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.column])
        # RIGHT
        if self.column < self.total_rows - 1 and not grid[self.row][self.column + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.column + 1])
        # LEFT
        if self.column > 0 and not grid[self.row][self.column - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.column - 1])

    def __lt__(self, other) -> bool:
        return False


def h(p1: [int, int], p2: [int, int]):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, drawFunc):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        drawFunc()


def algorithm(drawFunc, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, drawFunc)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        drawFunc()

        if current != start:
            current.make_closed()

    return False


def make_grid(rows: int, width: int):
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, gap, rows)
            grid[i].append(node)

    return grid


def draw_grid(win, rows, columns, height, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GRAY, (0, i * gap), (width, i * gap))
        for j in range(columns):
            pygame.draw.line(win, GRAY, (j * gap, 0), (j * gap, height))


def draw(win, grid, rows, columns, height, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, columns, height, width)
    pygame.display.update()


def get_clicked_pos(position, rows, width):
    gap = width // rows
    y, x = position

    row = y // gap
    col = x // gap

    return row, col


def main(win, height, width):
    ROWS = 10
    COLUMNS = 10

    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        draw(win, grid, ROWS, COLUMNS, height, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                position = pygame.mouse.get_pos()
                row, column = get_clicked_pos(position, ROWS, WIDTH)
                node = grid[row][column]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                position = pygame.mouse.get_pos()
                row, column = get_clicked_pos(position, ROWS, WIDTH)
                node = grid[row][column]
                node.reset()

                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    success = algorithm(lambda: draw(win, grid, ROWS, COLUMNS, height, width), grid, start, end)
                    if success:
                        print("Path found")
                    else:
                        print("Could not find a path")

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(window, HEIGHT, WIDTH)








