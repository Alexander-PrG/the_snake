from random import randint
import pygame as pg

# Константы для размеров экрана и размера сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (211, 211, 211)  # Светло-серый
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Начальная скорость игры
SPEED = 5

# Настройка игрового окна
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color=None):
        """Инициализирует базовые атрибуты объекта."""
        self.position = (0, 0)
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Отрисовывает одну ячейку.

        :param position: Позиция ячейки.
        :param color: Цвет ячейки (если не задан, используется цвет объекта).
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color if color else self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Абстрактный метод для отрисовки объекта."""
        raise NotImplementedError(
            "Метод draw должен быть реализован в дочерних классах."
        )


class Apple(GameObject):
    """Класс для яблока, наследуется от GameObject."""

    def __init__(self, body_color, occupied_cells):
        """Инициализирует яблоко и задает его начальную позицию."""
        super().__init__(body_color)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_positions):
        """Устанавливает случайное положение яблока на игровом поле."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс для змейки, наследуется от GameObject."""

    def __init__(self, color=SNAKE_COLOR):
        """Инициализирует начальное состояние змейки."""
        super().__init__(color)
        self.reset()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [
            (GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)
        ]
        self.direction = RIGHT

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки."""
        if (new_direction[0] != -self.direction[0] and
                new_direction[1] != -self.direction[1]):
            self.direction = new_direction

    def move(self):
        """Обновляет позицию змейки."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        # Обработка выхода за границы
        head_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        head_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT

        # Добавляем голову, удаляем последний сегмент
        self.positions.insert(0, (head_x, head_y))
        if len(self.positions) > self.length:
            self.positions.pop()

    def grow(self):
        """Увеличивает длину змейки."""
        self.length += 1

    def draw(self):
        """Отрисовывает змейку на экране."""
        self.draw_cell(self.get_head_position(), self.body_color)
        for position in self.positions[1:]:
            self.draw_cell(position, self.body_color)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]


current_speed = SPEED


def change_speed(amount):
    """Изменяет скорость игры на указанное значение."""
    global current_speed
    current_speed += amount
    current_speed = max(1, current_speed)


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:  # Выход из игры
                pg.quit()
                raise SystemExit
            elif event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                direction_map = {
                    pg.K_UP: UP,
                    pg.K_DOWN: DOWN,
                    pg.K_LEFT: LEFT,
                    pg.K_RIGHT: RIGHT
                }
                snake.update_direction(direction_map[event.key])
            elif event.key == pg.K_KP_PLUS:
                change_speed(1)
            elif event.key == pg.K_KP_MINUS:
                change_speed(-1)


def main():
    """Основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(APPLE_COLOR, snake.positions)
    score = 0  # Инициализация счета

    while True:
        clock.tick(current_speed)
        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)
            score += 1  # Увеличиваем счет на 1
        else:
            if snake.get_head_position() in snake.positions[1:]:
                snake.reset()
                score = 0  # Сбросить счет при столкновении с самим собой
                apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()

        # Отображение счета и дополнительной информации в заголовке окна
        pg.display.set_caption(
            f'Змейка - ESC для выхода, скорость: {current_speed}'
        )

        pg.display.update()


if __name__ == '__main__':
    main()
