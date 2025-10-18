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
        :param position: Начальная позиция объекта (координаты верхнего левого угла).
        :param body_color: Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color

    def draw(self, surface: pygame.Surface):
        """
        Абстрактный метод для отрисовки объекта на экране.
        Должен быть переопределен в дочерних классах.
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
        При инициализации требует объект змейки для проверки коллизий.
        :param snake: Экземпляр класса Snake для проверки, что яблоко 
                      не появится на теле змейки.
        """
        # Яблоко всегда красное
        super().__init__((0, 0), RED)
        self.snake = snake  # Сохраняем ссылку на змейку
        self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает случайное положение яблока на игровом поле.
        Позиция выбирается в координатах сетки (пикселях), кратных GRID_SIZE.
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
        Отрисовывает яблоко как красный квадрат.
        :param surface: Игровая поверхность (окно Pygame).
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)

# --- Класс Snake ---

class Snake(GameObject):
    """
    Класс, описывающий змейку, ее движение, отрисовку и столкновения.
    """
    def __init__(self):
        """
        Инициализирует начальное состояние змейки.
        """
        # Центральная точка экрана
        center_x = (GRID_WIDTH // 2) * GRID_SIZE
        center_y = (GRID_HEIGHT // 2) * GRID_SIZE
        
        # Змейка всегда зеленая
        super().__init__((center_x, center_y), GREEN)
        
        self.length: int = 1
        # Список позиций сегментов змейки
        self.positions: List[Tuple[int, int]] = [self.position] 
        # Начальное направление движения - вправо
        self.direction: Tuple[int, int] = RIGHT
        # Следующее направление, устанавливается после нажатия клавиши
        self.next_direction: Optional[Tuple[int, int]] = None
        # Позиция удаленного хвоста для затирания следа
        self.last_tail_position: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает позицию головы змейки (первый элемент в списке positions).
        """
        return self.positions[0]

    def reset(self):
        """
        Сбрасывает змейку в начальное состояние после проигрыша.
        Направление движения выбирается случайным образом.
        """
        center_x = (GRID_WIDTH // 2) * GRID_SIZE
        center_y = (GRID_HEIGHT // 2) * GRID_SIZE
        
        self.length = 1
        self.positions = [(center_x, center_y)]
        # Выбор случайного направления при сбросе
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last_tail_position = None

    def update_direction(self):
        """
        Обновляет текущее направление движения, если было задано новое 
        и оно не противоположно текущему (змейка не может двигаться назад).
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
        Обновляет позицию змейки, добавляя новую голову и удаляя хвост 
        (если змейка не съела яблоко).
        Также обрабатывает прохождение сквозь стены (эффект "бублика").
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        # Вычисляем новую позицию головы (в координатах сетки)
        new_head_x = head_x + dir_x * GRID_SIZE
        new_head_y = head_y + dir_y * GRID_SIZE

        # Обработка прохождения сквозь стены (торус)
        if new_head_x < 0:
            new_head_x = SCREEN_WIDTH - GRID_SIZE
        elif new_head_x >= SCREEN_WIDTH:
            new_head_x = 0
        
        if new_head_y < 0:
            new_head_y = SCREEN_HEIGHT - GRID_SIZE
        elif new_head_y >= SCREEN_HEIGHT:
            new_head_y = 0

        # Новая позиция головы
        new_head_position = (new_head_x, new_head_y)
        
        # Вставляем новый элемент в начало списка positions
        self.positions.insert(0, new_head_position)
        
        # Если змейка не выросла (длина списка больше заданной), удаляем хвост
        if len(self.positions) > self.length:
            # last_tail_position используется для затирания следа
            self.last_tail_position = self.positions.pop()
        else:
            self.last_tail_position = None
            
    def draw(self, surface: pygame.Surface):
        """
        Отрисовывает змейку и затирает ее след (хвост).
        :param surface: Игровая поверхность (окно Pygame).
        """
        # 1. Затираем след (предыдущую позицию хвоста)
        if self.last_tail_position:
            tail_rect = pygame.Rect(self.last_tail_position, (GRID_SIZE, GRID_SIZE))
            # Затираем черным цветом (цветом фона)
            pygame.draw.rect(surface, BLACK, tail_rect)

        # 2. Отрисовываем все сегменты змейки
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)

    def check_collision(self):
        """
        Проверяет столкновение головы змейки с ее телом.
        :return: True, если произошло столкновение, иначе False.
        """
        head = self.get_head_position()
        # Проверяем, совпадает ли позиция головы с какой-либо позицией 
        # в остальной части тела (self.positions[1:])
        return head in self.positions[1:]

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
    apple = Apple(snake) # Передаем змейку для проверки коллизий яблока

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
        
        # 4. Проверка, съела ли змейка яблоко (совпадение координат головы и яблока)
        if snake.get_head_position() == apple.position:
            # Увеличиваем длину змейки
            snake.length += 1
            # Перемещаем яблоко на новую случайную позицию
            apple.randomize_position()
        
        # 5. Проверка столкновения змейки с самой собой
        if snake.check_collision():
            # Если столкновение, сбрасываем игру
            snake.reset()
            # Очищаем экран после сброса (screen.fill(BLACK))
            screen.fill(BLACK) 
            # Перемещаем яблоко, чтобы оно не осталось на месте предыдущего столкновения
            apple.randomize_position()

        # 6. Отрисовка объектов
        # Яблоко (оно может быть перерисовано змейкой, если позиция совпала)
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
