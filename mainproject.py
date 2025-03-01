import pygame
import csv
import random
import database

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FONT_SIZE = 24


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Викторина по Астрономии")


font = pygame.font.Font(None, FONT_SIZE)


def load_questions(filename="questions.csv"):
    questions = {}
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Пропускаем заголовок
        for row in reader:
            level = int(row[0])
            question = row[1]
            correct_answer = row[2]
            incorrect_answers = row[3:]
            if level not in questions:
                questions[level] = []
            questions[level].append({
                'question': question,
                'correct_answer': correct_answer,
                'incorrect_answers': incorrect_answers
            })
    return questions


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def create_button(text, x, y, width, height, color, hover_color, action=None):
    button_rect = pygame.Rect(x, y, width, height)
    button_text = font.render(text, True, BLACK)
    button_text_rect = button_text.get_rect(center=button_rect.center)

    return {
        'rect': button_rect,
        'text': text,
        'text_surface': button_text,
        'text_rect': button_text_rect,
        'color': color,
        'hover_color': hover_color,
        'action': action
    }


def draw_button(button, surface):
    mouse_pos = pygame.mouse.get_pos()
    if button['rect'].collidepoint(mouse_pos):
        pygame.draw.rect(surface, button['hover_color'], button['rect'])
    else:
        pygame.draw.rect(surface, button['color'], button['rect'])
    surface.blit(button['text_surface'], button['text_rect'])


def start_screen():
    running = True
    start_button = create_button("Начать игру", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200,
                                 50, WHITE, GREEN, action='start')
    quit_button = create_button("Выход", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200,
                                50, WHITE, RED, action='quit')

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if start_button['rect'].collidepoint(event.pos):
                        return 'start'
                    if quit_button['rect'].collidepoint(event.pos):
                        pygame.quit()
                        return 'quit'

        screen.fill(BLUE)
        draw_text("Добро пожаловать в викторину по Астрономии!", font, WHITE, screen, SCREEN_WIDTH // 2 - 200, 100)
        draw_text("Правила: Ответьте на вопросы и наберите как можно больше очков.", font, WHITE, screen,
                  SCREEN_WIDTH // 2 - 270, 150)
        draw_button(start_button, screen)
        draw_button(quit_button, screen)
        pygame.display.flip()
    return 'quit'


def end_screen(score):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill(BLACK)
        draw_text("Игра окончена!", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, 100)
        draw_text(f"Ваш счет: {score}", font, WHITE, screen, SCREEN_WIDTH // 2 - 80, 150)
        pygame.display.flip()


def game():
    conn = database.create_connection("scores.db")
    if conn is None:
        print("Не удалось подключиться к базе данных.")
        return

    questions = load_questions()
    levels = sorted(questions.keys())
    total_score = 0
    current_level_index = 0

    running = True
    while running and current_level_index < len(levels):
        level = levels[current_level_index]
        level_questions = questions[level]
        level_score_multiplier = level

        random.shuffle(level_questions)

        for i in range(min(3, len(level_questions))):
            question_data = level_questions[i]
            question_text = question_data['question']
            correct_answer = question_data['correct_answer']
            incorrect_answers = question_data['incorrect_answers']

            answers = [correct_answer] + incorrect_answers
            random.shuffle(answers)

            buttons = []
            for j, answer in enumerate(answers):
                x = SCREEN_WIDTH // 2 - 300
                y = 250 + j * 60
                button = create_button(answer, x, y, 600, 50, WHITE, BLUE)
                buttons.append(button)

            selected_answer = None
            correct_answer_selected = False

            question_running = True
            while question_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        question_running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for button in buttons:
                                if button['rect'].collidepoint(event.pos):
                                    selected_answer = button['text']
                                    if selected_answer == correct_answer:
                                        total_score += level_score_multiplier
                                        correct_answer_selected = True
                                    question_running = False

                screen.fill(BLACK)
                draw_text(f"Уровень: {level}", font, WHITE, screen, 50, 50)
                draw_text(f"Вопрос {i + 1}/3", font, WHITE, screen, 50, 80)
                draw_text(question_text, font, WHITE, screen, SCREEN_WIDTH // 2 - 300, 150)

                for button in buttons:
                    if selected_answer:
                        if button['text'] == correct_answer:
                            button_color = GREEN
                        elif button['text'] == selected_answer:
                            button_color = RED
                        else:
                            button_color = WHITE
                        pygame.draw.rect(screen, button_color, button['rect'])
                    else:
                        draw_button(button, screen)
                    screen.blit(button['text_surface'], button['text_rect'])

                pygame.display.flip()

                if selected_answer:
                    pygame.time.delay(1500)
                    break

        current_level_index += 1

    player_name = "Игрок"
    database.save_score(conn, player_name, total_score)
    conn.close()

    end_screen(total_score)


if __name__ == "__main__":
    start_result = start_screen()
    if start_result == 'start':
        game()
    pygame.quit()
