# pygame_chat.py (Pygame application)
import pygame
import pygame.emscripten
import json
import asyncio

pygame.init()
screen = pygame.display.set_mode((600, 400))
font = pygame.font.Font(None, 30)
input_text = ""
chat_log = []

async def send_message(message):
    # Send message to Django backend using fetch API
    # (This needs to be adapted for Emscripten's async model)
    pass

def main():
    global input_text, chat_log
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    asyncio.run(send_message(input_text))  # Send message
                    chat_log.append("You: " + input_text)
                    input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        screen.fill((255, 255, 255))  # White background
        text_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(text_surface, (10, 370))

        y_offset = 10
        for line in chat_log:
            log_surface = font.render(line, True, (0, 0, 0))
            screen.blit(log_surface, (10, y_offset))
            y_offset += 30

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    pygame.emscripten.set_main_loop(main, 0)