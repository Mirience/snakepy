import pygame
import random
from typing import List, Tuple, Optional

# --- Константы и настройки игры ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20  # Размер одной ячейки (20x20 пикселей)
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Цвета (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)  # Цвет змейки
RED = (255, 0, 0)    # Цвет яблока

# Направления движения (DX, DY)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


# --- Базовый класс для игровых объектов ---

class GameObject:
    """
    Базовый класс для всех игровых объектов.
    Содержит общие атрибуты (позиция, цвет) и базовый метод отрисовки.
    """
    def __init__(self, position: Tuple[int, int], body_color: Tuple[int, int]):
        """
        Инициализирует базовые атрибуты объекта.

        :param position: Начальная позиция объекта 
                         (координаты верхнего левого угла).
        :param body_color: Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color

    @staticmethod
    def draw_square(surface: pygame.Surface, position: Tuple[int, int],
                    color: Tuple[int, int]):
        """
        Вспомогательный статический метод для рисования одного квадрата.
        Используется классами Apple и Snake для отрисовки сегментов.
        """
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, color, rect)

    def draw(self, surface: pygame.Surface):
        """
        Абстрактный метод для отрисовки объекта на экране.
        Должен быть переопределен в дочерних классах.
        В базовом классе не должно быть рисующих действий.
        """
        pass


# --- Класс Apple ---

class Apple(GameObject):
    """
    Класс, описывающий яблоко (еду) и его поведение.
    """
    def __init__(self, snake: 'Snake'):
        """
        Инициализирует яблоко, устанавливая цвет и случайную позицию.
        """
        # Яблоко всегда красное
        super().__init__((0, 0), RED)
        self.snake = snake  # Сохраняем ссылку на змейку
        self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает случайное положение яблока на игровом поле.
        Гарантирует, что яблоко не появится на теле змейки.
        """
        while True:
            # Генерация случайных координат ячейки
            x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_position = (x, y)
            
            # Проверка, не появляется ли яблоко на теле змейки
            if new_position not in self.snake.positions:
                self.position = new_position
                break

    def draw(self, surface: pygame.Surface):
        """
        Отрисовывает яблоко как красный квадрат, используя базовый метод.
        :param surface: Игровая поверхность (окно Pygame).
        """
        GameObject.draw_square(surface, self.position, self.body_color)


# --- Класс Snake ---

class Snake(GameObject):
    """
    Класс, описывающий змейку, ее движение, отрисовку и столкновения.
    """
    def __init__(self):
        """
        Инициализирует начальное состояние змейки.
        """
        # Вызов super() с нулевыми координатами
        super().__init__((0, 0), GREEN)
        self._initial_state()

    def _initial_state(self):
        """
        Устанавливает змейку в начальное состояние (центр, длина 1, 
        случайное направление). Устраняет дублирование кода между __init__
        и reset.
        """
        center_x = (GRID_WIDTH // 2) * GRID_SIZE
        center_y = (GRID_HEIGHT // 2) * GRID_SIZE
        
        self.length = 1
        self.positions: List[Tuple[int, int]] = [(center_x, center_y)]
        
        # Выбор случайного направления
        self.direction: Tuple[int, int] = random.choice(
            [UP, DOWN, LEFT, RIGHT]
        )
        self.next_direction: Optional[Tuple[int, int]] = None
        self.last_tail_position: Optional[Tuple[int, int]] = None
        # Обновление позиции базового класса
        self.position = (center_x, center_y) 

    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает позицию головы змейки 
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def reset(self):
        """
        Сбрасывает змейку в начальное состояние после проигрыша, вызывая 
        общий метод установки начального состояния.
        """
        self._initial_state()

    def update_direction(self):
        """
        Обновляет текущее направление движения, если было задано новое 
        и оно не противоположно текущему 
        (змейка не может двигаться назад).
        """
        if self.next_direction:
            current_dx, current_dy = self.direction
            next_dx, next_dy = self.next_direction

            # Проверка, что новое направление не противоположно текущему
            if (current_dx, current_dy) != (-next_dx, -next_dy):
                self.direction = self.next_direction
            
            self.next_direction = None

    def move(self):
        """
        Обновляет позицию змейки, используя оператор остатка от деления (%) 
        для обработки прохождения сквозь стены (торус).
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        # Расчет нового положения головы (тороидальность)
        new_head_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_head_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT

        # Новая позиция головы
        new_head_position = (new_head_x, new_head_y)
        
        # Вставляем новый элемент в начало списка positions
        self.positions.insert(0, new_head_position)
        
        # Если змейка не выросла, удаляем хвост
        if len(self.positions) > self.length:
            # last_tail_position используется для затирания следа
            self.last_tail_position = self.positions.pop()
        else:
            self.last_tail_position = None
            
    def draw(self, surface: pygame.Surface):
        """
        Отрисовывает все сегменты змейки и затирает ее след (хвост).
        :param surface: Игровая поверхность (окно Pygame).
        """
        # 1. Затираем след (предыдущую позицию хвоста)
        if self.last_tail_position:
            GameObject.draw_square(
                surface, self.last_tail_position, BLACK
            )

        # 2. Отрисовываем все сегменты змейки
        for position in self.positions:
            GameObject.draw_square(surface, position, self.body_color)

    def check_collision(self):
        """
        Проверяет столкновение головы змейки с ее телом.
        
        Проверяем, совпадает ли позиция головы с какой-либо позицией 
        в остальной части тела (self.positions[1:]). Короткая змея 
        (длина 1) не может укусить себя.
        
        :return: True, если произошло столкновение, иначе False.
        """
        head = self.get_head_position()
        return self.length > 1 and head in self.positions[1:]


# --- Функции обработки ввода ---

def handle_keys(snake: Snake):
    """
    Обрабатывает нажатия клавиш для изменения направления движения змейки.
    :param snake: Объект змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                snake.next_direction = RIGHT


# --- Основной игровой цикл ---

def main():
    """
    Основной цикл игры «Изгиб Питона».
    """
    # Инициализация Pygame
    pygame.init()
    
    # Настройка игрового окна
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Изгиб Питона (Snake Game)')
    clock = pygame.time.Clock()

    # Создание экземпляров игровых объектов
    snake = Snake()
    # Передаем змейку для проверки коллизий яблока
    apple = Apple(snake) 

    # Отрисовка начального состояния
    screen.fill(BLACK)
    apple.draw(screen)
    snake.draw(screen)
    pygame.display.update()
    
    running = True
    while running:
        # 1. Обработка событий (нажатия клавиш)
        handle_keys(snake)
        
        # 2. Обновление направления движения
        snake.update_direction()
        
        # 3. Движение змейки
        snake.move()
        
        # 4. Проверка, съела ли змейка яблоко 
        # (совпадение координат головы и яблока)
        if snake.get_head_position() == apple.position:
            # Увеличиваем длину змейки
            snake.length += 1
            # Перемещаем яблоко на новую случайную позицию
            apple.randomize_position()
        
        # 5. Проверка столкновения змейки с самой собой
        if snake.check_collision():
            # Если столкновение, сбрасываем игру
            snake.reset()
            # Очищаем экран после сброса
            screen.fill(BLACK) 
            # Перемещаем яблоко
            apple.randomize_position()

        # 6. Отрисовка объектов
        # Яблоко (оно может быть перерисовано змейкой)
        apple.draw(screen)
        # Змейка (включает затирание следа)
        snake.draw(screen)
        
        # 7. Обновление экрана
        pygame.display.update()
        
        # 8. Регулирование скорости (20 кадров в секунду)
        clock.tick(20)

    pygame.quit()

if __name__ == '__main__':
    main()
