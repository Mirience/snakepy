import pygame as pg
import sys
import random

# Размеры окна и игровой сетки
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = (SCREEN_WIDTH - 400) // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
INFO_AREA_WIDTH = 400

# Цветовая палитра
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (200, 200, 200)
LIGHT_GREEN = (155, 188, 15)
DARK_GREEN = (15, 56, 15)
BOARD_BACKGROUND_COLOR = LIGHT_GREEN

# Константы направлений
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь управления движениями
MOVEMENT_KEYS = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
}

# Глобальные переменные
score = 0
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()

pg.init()

FONT = pg.font.Font(None, 24)

INSTRUCTION_TEXT = [
    "+-----------------+",
    "    Score: {}",
    "+-----------------+",
    "> Движение - клавиши стрелок",
    "> Выход из игры - клавиша Esc",
    "> Яблоки - красные",
    "> Отрава - синяя",

    "> За каждые 5 съеденных яблок:",
    "  + 2 к скорости дижения",
    "  + 1 отрава на экране",
    "",
    "Удачи в игре! И помни, что",
    "каждая змейка мечтает стать Python =)"
]


class GameObject:
    """Основной класс, представляющий фигуры в игре"""

    def __init__(self, body_color=WHITE):
        self.body_color = body_color
        self.position = None

    def draw(self):
        """Отрисовка фигур с переопределением в наследуемых классах"""

    def draw_cell(self, position, color=None):
        """Отрисовка ячейки на экране"""
        x, y = position
        color = color or self.body_color
        pg.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE,
                                     GRID_SIZE, GRID_SIZE))


class Snake(GameObject):
    """Наследуемый класс змейки"""

    def __init__(self):
        super().__init__(DARK_GREEN)
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow = False

    def move(self):
        """Инициализация движения"""
        head = self.positions[0]
        new_head = ((head[0] + self.direction[0]) % GRID_WIDTH,
                    (head[1] + self.direction[1]) % GRID_HEIGHT)

        if new_head in self.positions[4:]:
            game_over("self")
            return False

        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False

    def draw(self):
        """Отрисовка на игровом поле"""
        for segment in self.positions:
            self.draw_cell(segment)

    def update_direction(self, new_direction):
        """Смена направления движения змейки"""
        if (-new_direction[0], -new_direction[1]) != self.direction:
            self.direction = new_direction

    def reset(self):
        """Сброс параметров змейки"""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT

    def get_head_position(self):
        """Получить позицию головы змейки"""
        return self.positions[0]

    def length(self):
        """Получить длину змейки"""
        return len(self.positions)


class Apple(GameObject):
    """Наследуемый класс яблока"""

    def __init__(self, body_color=RED):
        super().__init__(body_color)
        self.position = None

    def draw(self):
        """Отрисовка на игровом поле"""
        self.draw_cell(self.position)

    def clear(self):
        """Удаление с игрового поля"""
        self.draw_cell(self.position, color=BOARD_BACKGROUND_COLOR)

    def randomize_position(self, occupied_cells):
        """Генерация объекта на случайной позиции"""
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))
        while self.position in occupied_cells:
            self.position = (random.randint(0, GRID_WIDTH - 1),
                             random.randint(0, GRID_HEIGHT - 1))


def draw_game_area(snake, apple, bombs):
    """Игровое поле"""
    screen.fill(BOARD_BACKGROUND_COLOR)
    for segment in snake.positions:
        snake.draw_cell(segment)
    for bomb in bombs:
        bomb.draw()

    if apple.position is not None:
        apple.draw()


def draw_info_area(score):
    """Информационное поле"""
    info_area = pg.Rect(SCREEN_WIDTH - 400, 0, 400, SCREEN_HEIGHT)
    pg.draw.rect(screen, LIGHT_GRAY, info_area)
    y = 10
    for text in INSTRUCTION_TEXT:
        if "{}" in text:
            text = text.format(score)
        line = FONT.render(text, True, BLACK)
        screen.blit(line, (SCREEN_WIDTH - 390, y))
        y += 30


def reset_game(snake, apple, bombs):
    """Сброс параметров игры"""
    global score, frame_delay, apples_eaten
    score = 0
    frame_delay = 100
    apples_eaten = 0
    snake.reset()
    bombs.clear()
    occupied_cells = [*snake.positions, *(bomb.position for bomb in bombs)]
    apple.randomize_position(occupied_cells)


def game_over(collision_type):
    """Сценарий завершения игры"""
    font = pg.font.Font(None, 36)
    if collision_type == "bomb":
        # Фанатам Скорпиона из Mortal Kombat посвящается
        text = font.render("Game over here! Отрава wins. Try again", True, RED)
    elif collision_type == "self":
        text = font.render("Game over here! Try again", True, RED)

    text_x = (SCREEN_WIDTH - INFO_AREA_WIDTH) // 2 - text.get_width() // 2
    text_y = SCREEN_HEIGHT // 2 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))
    pg.display.flip()
    pg.time.delay(2000)

    reset_game(snake, apple, bombs)


def handle_keys(snake):
    """Обработка пользовательского ввода"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

            if event.key in MOVEMENT_KEYS:
                snake.update_direction(MOVEMENT_KEYS[event.key])


def main():
    """Главная функция игры"""
    global score, screen, clock, frame_delay, snake, apple, bombs, apples_eaten
    pg.init()
    pg.display.set_caption('Змейка')

    snake = Snake()
    apple = Apple()
    bombs = []

    reset_game(snake, apple, bombs)
    frame_count = 0
    apples_eaten = 0

    while True:
        handle_keys(snake)

        if snake.move():
            game_over("self")
            continue

        collision = snake.positions[0] in snake.positions[1:]
        if collision:
            game_over("self")
            continue

        collision = snake.positions[0] in [bomb.position for
                                           bomb in bombs]
        if collision:
            game_over("bomb")
            continue

        if snake.get_head_position() == apple.position:
            occupied_cells = [*snake.positions, *(bomb.position
                                                  for bomb in bombs)]
            apple.randomize_position(occupied_cells)
            snake.grow = True
            score += 1
            apples_eaten += 1
            frame_count += 1

            if apples_eaten % 5 == 0:
                frame_delay -= 10
                occupied_cells = [*snake.positions, apple.position,
                                  *(bomb.position for bomb in bombs)]
                bomb = Apple(body_color=BLUE)
                if bomb is not None:
                    bomb.randomize_position(occupied_cells)
                bombs.append(bomb)

        draw_game_area(snake, apple, bombs)
        draw_info_area(score)

        pg.display.flip()
        clock.tick(1000 // frame_delay)


if __name__ == "__main__":
    main()
