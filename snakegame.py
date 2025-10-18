import pygame
import random

# Класс для представления игрового объекта
class GameObject:
    def __init__(self, position, color):
        self.position = position
        self.color = color

    def draw(self, surface):
        pass  # Этот метод должен быть переопределён в дочерних классах

# Класс для представления яблока
class Apple(GameObject):
    def __init__(self):
        super().__init__(self.randomize_position(), (255, 0, 0))

    def randomize_position(self):
        return (random.randint(0, 31) * 20, random.randint(0, 23) * 20)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], 20, 20))

# Класс для представления змейки
class Snake(GameObject):
    def __init__(self):
        super().__init__((320, 240), (0, 255, 0))
        self.length = 1
        self.positions = [self.position]
        self.direction = 'right'
        self.next_direction = None

    def update_direction(self, new_direction):
        if new_direction is not None:
            self.direction = new_direction

    def move(self):
        head_x, head_y = self.positions[0]
        if self.direction == 'right':
            head_x += 20
        elif self.direction == 'left':
            head_x -= 20
        elif self.direction == 'up':
            head_y -= 20
        elif self.direction == 'down':
            head_y += 20

        self.positions.insert(0, (head_x, head_y))
        if self.length < len(self.positions):
            self.positions.pop()

    def draw(self, surface):
        for segment in self.positions:
            pygame.draw.rect(surface, self.color, (segment[0], segment[1], 20, 20))

    def get_head_position(self):
        return self.positions[0]

    def reset(self):
        self.length = 1
        self.positions = [self.position]
        self.direction = 'right'
        self.next_direction = None

def handle_keys(snake):
    """Обрабатывает нажатия клавиш для изменения направления движения змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                snake.next_direction = 'right'
            elif event.key == pygame.K_LEFT:
                snake.next_direction = 'left'
            elif event.key == pygame.K_UP:
                snake.next_direction = 'up'
            elif event.key == pygame.K_DOWN:
                snake.next_direction = 'down'

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    snake = Snake()
    apple = Apple()

    while True:
        handle_keys(snake)
        snake.update_direction(snake.next_direction)
        snake.move()

        # Проверка столкновения со стенками
        if snake.get_head_position()[0] >= 640:
            snake.reset()
        elif snake.get_head_position()[0] < 0:
            snake.reset()
        elif snake.get_head_position()[1] >= 480:
            snake.reset()
        elif snake.get_head_position()[1] < 0:
            snake.reset()

        # Проверка поедания яблока
        if snake.get_head_position() == apple.position:
            apple = Apple()
            snake.length += 1

        screen.fill((0, 0, 0))
        apple.draw(screen)
        snake.draw(screen)
        pygame.display.update()
        clock.tick(10)

if __name__ == "__main__":
    main()
