import random
import tkinter as tk
from dataclasses import dataclass


CELL_SIZE = 24
GRID_WIDTH = 24
GRID_HEIGHT = 18
UPDATE_DELAY_MS = 110

BG_COLOR = "#151515"
GRID_COLOR = "#222222"
SNAKE_COLOR = "#4ADE80"
HEAD_COLOR = "#22C55E"
FOOD_COLOR = "#EF4444"
TEXT_COLOR = "#F8FAFC"


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class SnakeGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Змейка")
        self.root.resizable(False, False)

        canvas_width = GRID_WIDTH * CELL_SIZE
        canvas_height = GRID_HEIGHT * CELL_SIZE

        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.score_label = tk.Label(
            root,
            text="Счёт: 0",
            font=("Segoe UI", 13, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            pady=10,
        )
        self.score_label.pack(fill=tk.X)

        self.direction = Point(1, 0)
        self.next_direction = self.direction
        self.snake: list[Point] = []
        self.food = Point(0, 0)
        self.score = 0
        self.game_over = False
        self.after_id: str | None = None

        self.root.bind("<KeyPress>", self.handle_keypress)
        self.reset_game()

    def reset_game(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [
            Point(start_x, start_y),
            Point(start_x - 1, start_y),
            Point(start_x - 2, start_y),
        ]
        self.direction = Point(1, 0)
        self.next_direction = self.direction
        self.score = 0
        self.game_over = False
        self.spawn_food()
        self.update_score()
        self.draw()
        self.schedule_next_tick()

    def spawn_food(self) -> None:
        occupied = set(self.snake)
        candidates = [
            Point(x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if Point(x, y) not in occupied
        ]
        if not candidates:
            self.food = Point(-1, -1)
            self.win_game()
            return
        self.food = random.choice(candidates)

    def handle_keypress(self, event: tk.Event) -> None:
        key_map = {
            "Up": Point(0, -1),
            "w": Point(0, -1),
            "W": Point(0, -1),
            "Down": Point(0, 1),
            "s": Point(0, 1),
            "S": Point(0, 1),
            "Left": Point(-1, 0),
            "a": Point(-1, 0),
            "A": Point(-1, 0),
            "Right": Point(1, 0),
            "d": Point(1, 0),
            "D": Point(1, 0),
        }

        if self.game_over and event.keysym.lower() == "r":
            self.reset_game()
            return

        new_direction = key_map.get(event.keysym, key_map.get(event.char))
        if new_direction is None:
            return

        if (new_direction.x == -self.direction.x and new_direction.y == -self.direction.y):
            return

        self.next_direction = new_direction

    def tick(self) -> None:
        if self.game_over:
            return

        self.direction = self.next_direction
        head = self.snake[0]
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)

        if (
            new_head.x < 0
            or new_head.x >= GRID_WIDTH
            or new_head.y < 0
            or new_head.y >= GRID_HEIGHT
            or new_head in self.snake
        ):
            self.end_game()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.update_score()
            self.spawn_food()
        else:
            self.snake.pop()

        self.draw()
        self.schedule_next_tick()

    def schedule_next_tick(self) -> None:
        self.after_id = self.root.after(UPDATE_DELAY_MS, self.tick)

    def update_score(self) -> None:
        self.score_label.config(text=f"Счёт: {self.score}")

    def draw(self) -> None:
        self.canvas.delete("all")
        self.draw_grid()

        if self.food.x >= 0 and self.food.y >= 0:
            self.draw_cell(self.food, FOOD_COLOR)

        for index, segment in enumerate(self.snake):
            color = HEAD_COLOR if index == 0 else SNAKE_COLOR
            self.draw_cell(segment, color)

        if self.game_over:
            self.draw_overlay()

    def draw_grid(self) -> None:
        for x in range(GRID_WIDTH + 1):
            px = x * CELL_SIZE
            self.canvas.create_line(px, 0, px, GRID_HEIGHT * CELL_SIZE, fill=GRID_COLOR)
        for y in range(GRID_HEIGHT + 1):
            py = y * CELL_SIZE
            self.canvas.create_line(0, py, GRID_WIDTH * CELL_SIZE, py, fill=GRID_COLOR)

    def draw_cell(self, point: Point, color: str) -> None:
        x1 = point.x * CELL_SIZE + 1
        y1 = point.y * CELL_SIZE + 1
        x2 = x1 + CELL_SIZE - 2
        y2 = y1 + CELL_SIZE - 2
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def draw_overlay(self) -> None:
        w = GRID_WIDTH * CELL_SIZE
        h = GRID_HEIGHT * CELL_SIZE
        self.canvas.create_rectangle(0, 0, w, h, fill="#000000", stipple="gray50", outline="")
        self.canvas.create_text(
            w // 2,
            h // 2 - 16,
            text="Игра окончена",
            fill=TEXT_COLOR,
            font=("Segoe UI", 24, "bold"),
        )
        self.canvas.create_text(
            w // 2,
            h // 2 + 18,
            text="Нажмите R для рестарта",
            fill=TEXT_COLOR,
            font=("Segoe UI", 14),
        )

    def end_game(self) -> None:
        self.game_over = True
        self.draw()

    def win_game(self) -> None:
        self.game_over = True
        self.draw()


def main() -> None:
    root = tk.Tk()
    root.configure(bg=BG_COLOR)
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
