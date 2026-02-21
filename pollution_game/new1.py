import os
import glob
import pygame
import sys
import random
import math

# Initializing Pygame and Font system
pygame.init()
pygame.font.init()

# -------------------------------
# BASIC SETTINGS
# -------------------------------
WIDTH = 900
HEIGHT = 700
FPS = 60
BG_SWITCH_TIME = 300

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mission Earth")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED_UNCOMPLETED = (200, 50, 50)
GREEN_COMPLETED = (60, 148, 16)
BUTTON_COLOR = (60, 148, 16)
BUTTON_HOVER_COLOR = (100, 200, 80)

font_large = pygame.font.Font(None, 80)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 30)

# -------------------------------
# GAME STATES
# -------------------------------
STATE_MENU = "menu"
STATE_LEVEL_SELECT = "level_select"
STATE_INSTRUCTIONS = "instructions"
STATE_LEVEL1 = "Level 1"
STATE_LEVEL2 = "Level 2"
STATE_LEVEL3 = "Level 3"
STATE_FINISH = "finish_screen"
STATE_WIN = "win"

current_state = STATE_MENU
current_level_name = STATE_LEVEL1

# PROGRESS TRACKING
level_completion_status = {
    "Level 1": False,
    "Level 2": False,
    "Level 3": False
}

# -------------------------------
# ASSETS (Backgrounds)
# -------------------------------
BACKGROUND_DIR = os.path.join(os.path.dirname(__file__), 'backgrounds')
LEVEL_BACKGROUNDS = {
    "Level 1": [
        os.path.join(BACKGROUND_DIR, "1.png"),
        os.path.join(BACKGROUND_DIR, "2.png"),
        os.path.join(BACKGROUND_DIR, "3.png")
    ],
    "Level 2": [
        os.path.join(BACKGROUND_DIR, "4.png"),
        os.path.join(BACKGROUND_DIR, "5.png"),
        os.path.join(BACKGROUND_DIR, "6.png")
    ],
    "Level 3": [
        os.path.join(BACKGROUND_DIR, "7.png"),
        os.path.join(BACKGROUND_DIR, "8.png"),
        os.path.join(BACKGROUND_DIR, "9.png")
    ]
}

background_images = []
bg_x1, bg_x2 = 0, WIDTH
scroll_speed = 5
bg_index_left, bg_index_right, bg_timer = 0, 1, 0

# -------------------------------
# OBSTACLES (from latest.py style)
# -------------------------------
obstacles = []
OBSTACLE_WIDTH = 140
OBSTACLE_HEIGHT = 140
level_obstacle_speed = {"Level 1": 7, "Level 2": 10, "Level 3": 13}
level_obstacle_spawn_rate = {"Level 1": 80, "Level 2": 55, "Level 3": 35}
level_timer = 0  # used for obstacle spawn timing


def spawn_obstacle(current_level):
    lane = random.choice(lane_positions)
    x = WIDTH + 50
    rect = pygame.Rect(x, lane, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
    
    # Select an image specific to the current level
    lvl_images = LEVEL_SPECIFIC_OBSTACLES.get(current_level)
    img = random.choice(lvl_images)
    
    # Store both the rect and the image
    obstacles.append({"rect": rect, "img": img})


def update_obstacles(current_level):
    global player_x, player_y, player_width, player_height # Add this line
    speed = level_obstacle_speed[current_level]
    for obs_data in obstacles[:]:
        obs_rect = obs_data["rect"]
        obs_rect.x -= speed
        
        if obs_rect.x < -OBSTACLE_WIDTH:
            obstacles.remove(obs_data)
            continue

        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        if obs_rect.colliderect(player_rect):
            obstacles.remove(obs_data)
            start_level(current_level) # Changed "Level 1" to current_level so you don't reset to Lvl 1 every time
            return


def draw_obstacles():
    for obs_data in obstacles:
        # Drawing the level-specific image at the obstacle's position
        window.blit(obs_data["img"], (obs_data["rect"].x, obs_data["rect"].y))

# -------------------------------
# PUZZLE PIECES
# -------------------------------
PUZZLE_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "puzzle_images")
ALL_PUZZLE_IMAGES = []
for file in sorted(glob.glob(os.path.join(PUZZLE_IMAGE_DIR, "*.png"))):
    try:
        img = pygame.image.load(file).convert_alpha()
        ALL_PUZZLE_IMAGES.append(pygame.transform.scale(img, (90, 90)))
    except:
        pass

if not ALL_PUZZLE_IMAGES:
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    surf.fill((255, 215, 0))
    ALL_PUZZLE_IMAGES.append(surf)

PUZZLE_SIZE = 80
puzzle_pieces = []
puzzles_collected = 0
PIECES_REQUIRED_TO_FINISH = 3

# --- FINAL WIN IMAGE ---
# Replace 'final_puzzle.png' with your actual filename
WIN_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "final_puzzle.png") 
win_image = None

try:
    win_image = pygame.image.load(WIN_IMAGE_PATH).convert_alpha()
    # Scale it to fit a large portion of the screen, e.g., 500x500
    win_image = pygame.transform.scale(win_image, (500, 500))
except Exception as e:
    print(f"Error loading win image: {e}")

# --- FINAL WIN IMAGE ---
# Replace 'final_puzzle.png' with your actual filename
WIN_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "final_puzzle.png") 
win_image = None

try:
    win_image = pygame.image.load(WIN_IMAGE_PATH).convert_alpha()
    # Scale it to fit a large portion of the screen, e.g., 500x500
    win_image = pygame.transform.scale(win_image, (500, 500))
except Exception as e:
    print(f"Error loading win image: {e}")





# --- OBSTACLE ASSETS ---
# --- IMPROVED OBSTACLE LOADING ---
OBSTACLE_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "obstacles")
LEVEL_SPECIFIC_OBSTACLES = {
    "Level 1": [],
    "Level 2": [],
    "Level 3": []
}


def load_obstacle_images():
    """Populate LEVEL_SPECIFIC_OBSTACLES by loading images from the
    obstacles/<Level X>/ folders. If no images are found for a level,
    create a simple fallback surface so spawn_obstacle doesn't crash.
    """
    for lvl in list(LEVEL_SPECIFIC_OBSTACLES.keys()):
        lvl_folder = os.path.join(OBSTACLE_IMAGE_DIR, lvl)
        images = []
        if os.path.exists(lvl_folder):
            files = glob.glob(os.path.join(lvl_folder, "*.png"))
            for f in files:
                try:
                    img = pygame.image.load(f).convert_alpha()
                    img = pygame.transform.scale(img, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
                    images.append(img)
                except Exception:
                    pass

        # If none found in the level folder, try the root obstacles folder
        if not images and os.path.exists(OBSTACLE_IMAGE_DIR):
            files = glob.glob(os.path.join(OBSTACLE_IMAGE_DIR, "*.png"))
            for f in files:
                try:
                    img = pygame.image.load(f).convert_alpha()
                    img = pygame.transform.scale(img, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
                    images.append(img)
                except Exception:
                    pass

        # Final fallback: create a simple colored surface so random.choice works
        if not images:
            surf = pygame.Surface((OBSTACLE_WIDTH, OBSTACLE_HEIGHT), pygame.SRCALPHA)
            surf.fill((120, 120, 120))
            images = [surf]

        LEVEL_SPECIFIC_OBSTACLES[lvl] = images




# --- PLAYER ASSETS ---
CHARACTER_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "characters")
LEVEL_PLAYER_IMAGES = {
    "Level 1": None,
    "Level 2": None,
    "Level 3": None
}

def load_character_images():
    global player_width, player_height # Add this to use the variables above
    for lvl in LEVEL_PLAYER_IMAGES.keys():
        lvl_folder = os.path.join(CHARACTER_IMAGE_DIR, lvl)
        if os.path.exists(lvl_folder):
            char_files = glob.glob(os.path.join(lvl_folder, "*.png"))
            if char_files:
                try:
                    img = pygame.image.load(char_files[0]).convert_alpha()
                    # Change (40, 40) to (player_width, player_height)
                    LEVEL_PLAYER_IMAGES[lvl] = pygame.transform.scale(img, (player_width, player_height))
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"Empty folder: No .png files found in {lvl_folder}")
        else:
            print(f"Folder Missing: Looking for {lvl_folder}")


# -------------------------------
# PLAYER SYSTEM
# -------------------------------
player_width, player_height, player_x = 60, 60, 100
grass_top = int(HEIGHT * 0.45)
grass_bottom = HEIGHT - player_height - 40
lane_positions = [
    int(grass_top + i * ((grass_bottom - grass_top) / 2)) for i in range(3)
]
LANE_COUNT = len(lane_positions)

lane_index = 1
player_y = lane_positions[lane_index]
player_vel_y, gravity, jump_strength, is_jumping = 0, 1, -15, False


def handle_player_movement(keys):
    global player_x, player_vel_y, is_jumping
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= 7
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += 7
    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        player_vel_y = jump_strength


def draw_player():
    global player_y, player_vel_y, is_jumping, current_state
    
    # Physics logic
    if is_jumping:
        player_vel_y += gravity
        player_y += player_vel_y
        if player_y >= HEIGHT - 50:
            player_y = HEIGHT - 50
            player_vel_y = 0
            is_jumping = False

    # Get image safely
    char_img = LEVEL_PLAYER_IMAGES.get(current_state)

    # Only draw the image if we are actually in a Level state and the image exists
    if char_img and current_state in ["Level 1", "Level 2", "Level 3"]:
        window.blit(char_img, (player_x, player_y))
    else:
        # Fallback to red block
        pygame.draw.rect(window, (245, 39, 39),
                         (player_x, player_y, player_width, player_height))

# -------------------------------
# BACKGROUND FUNCTIONS
# -------------------------------


def load_level_backgrounds(level_name):
    global background_images, bg_x1, bg_x2, bg_timer, bg_index_left, bg_index_right
    background_images = []
    if level_name in LEVEL_BACKGROUNDS:
        for path in LEVEL_BACKGROUNDS[level_name]:
            try:
                img = pygame.image.load(path).convert()
                background_images.append(
                    pygame.transform.scale(img, (WIDTH, HEIGHT))
                )
            except:
                pass
    if not background_images:
        background_images = [None]
    bg_x1, bg_x2 = 0, WIDTH
    bg_index_left = 0
    bg_index_right = 1 if len(background_images) > 1 else 0
    bg_timer = 0


def draw_scrolling_background():
    global bg_x1, bg_x2, bg_index_left, bg_index_right, bg_timer
    if not background_images or background_images[0] is None:
        window.fill(BLACK)
        return

    bg_timer += 1
    if bg_timer >= BG_SWITCH_TIME:
        bg_timer = 0
        bg_index_left = (bg_index_left + 1) % len(background_images)
        bg_index_right = (bg_index_right + 1) % len(background_images)

    bg_x1 -= scroll_speed
    bg_x2 -= scroll_speed

    if bg_x1 < -WIDTH:
        bg_x1 = WIDTH
        bg_index_left = (bg_index_left + 1) % len(background_images)

    if bg_x2 < -WIDTH:
        bg_x2 = WIDTH
        bg_index_right = (bg_index_right + 1) % len(background_images)

    window.blit(background_images[bg_index_left], (bg_x1, 0))
    window.blit(background_images[bg_index_right], (bg_x2, 0))

# -------------------------------
# PUZZLE SPAWN / UPDATE
# -------------------------------


def spawn_single_puzzle_piece(current_level):
    lane = random.choice(lane_positions)
    x = random.randint(WIDTH + 400, WIDTH + 1200)

    if ALL_PUZZLE_IMAGES:
        img = random.choice(ALL_PUZZLE_IMAGES)
    else:
        img = pygame.Surface((40, 40))
        img.fill((255, 215, 0))

    rect = pygame.Rect(x, lane, PUZZLE_SIZE, PUZZLE_SIZE)
    puzzle_pieces.append({"rect": rect, "img": img})


def update_puzzle_pieces(current_level):
    global puzzles_collected, current_state, current_level_name

    for piece in puzzle_pieces[:]:
        piece["rect"].x -= int(scroll_speed * 1.4)

        if piece["rect"].x < -PUZZLE_SIZE:
            puzzle_pieces.remove(piece)
            spawn_single_puzzle_piece(current_level)
            continue

        player_rect = pygame.Rect(
            player_x, player_y, player_width, player_height
        )
        if piece["rect"].colliderect(player_rect):
            puzzles_collected += 1
            puzzle_pieces.remove(piece)

            if puzzles_collected >= PIECES_REQUIRED_TO_FINISH:
                current_level_name = current_level
                current_state = STATE_FINISH
                return
            else:
                spawn_single_puzzle_piece(current_level)

# -------------------------------
# LEVEL CONTROL
# -------------------------------


def start_level(level_name):
    global current_state, obstacles, puzzle_pieces, puzzles_collected
    global player_x, lane_index, player_y, scroll_speed, level_timer
    current_state = level_name
    level_timer = 0
    obstacles = []
    puzzle_pieces = []
    puzzles_collected = 0
    player_x = 100
    lane_index = 1
    scroll_speed = 5
    player_y = lane_positions[lane_index]
    load_level_backgrounds(level_name)
    for _ in range(3):
        spawn_single_puzzle_piece(level_name)

# -------------------------------
# SCREEN DRAWING
# -------------------------------
finish_continue_button = None


def draw_menu():
    window.fill(BLACK)
    t = font_large.render("Mission Earth", True, WHITE)
    window.blit(t, (WIDTH // 2 - t.get_width() // 2, 100))
    m = pygame.mouse.get_pos()
    b1 = pygame.Rect(WIDTH // 2 - 100, 250, 200, 60)
    b2 = pygame.Rect(WIDTH // 2 - 100, 350, 200, 60)
    pygame.draw.rect(window,
                     BUTTON_HOVER_COLOR if b1.collidepoint(m) else BUTTON_COLOR,
                     b1,
                     border_radius=10)
    pygame.draw.rect(window,
                     BUTTON_HOVER_COLOR if b2.collidepoint(m) else BUTTON_COLOR,
                     b2,
                     border_radius=10)
    window.blit(font_medium.render("Start", True, BLACK),
                (b1.x + 60, b1.y + 10))
    window.blit(font_medium.render("Levels", True, BLACK),
                (b2.x + 50, b2.y + 10))
    return {"start": b1, "levels": b2}


def draw_level_select():
    window.fill(BLACK)
    t = font_large.render("Select Level", True, WHITE)
    window.blit(t, (WIDTH // 2 - t.get_width() // 2, 50))
    m = pygame.mouse.get_pos()
    btns = {}
    for i, lvl in enumerate(["Level 1", "Level 2", "Level 3"]):
        if lvl == "Level 1":
            playable = True
        else:
            prev_level = "Level " + str(i)
            playable = level_completion_status.get(prev_level, False)

        if level_completion_status[lvl]:
            color = GREEN_COMPLETED
        elif playable:
            color = RED_UNCOMPLETED
        else:
            color = (50, 50, 50)

        r = pygame.Rect(WIDTH // 2 - 125, 180 + i * 100, 250, 80)
        pygame.draw.rect(window, color, r, border_radius=10)
        label = lvl + ("" if playable else " (Locked)")
        txt = font_medium.render(label, True, WHITE)
        window.blit(
            txt,
            (r.centerx - txt.get_width() // 2,
             r.centery - txt.get_height() // 2)
        )
        if playable:
            btns[lvl] = r

    back = pygame.Rect(50, HEIGHT - 80, 150, 50)
    pygame.draw.rect(window, BUTTON_COLOR, back, border_radius=5)
    window.blit(font_small.render("Back", True, BLACK),
                (back.x + 45, back.y + 12))
    btns["back"] = back
    return btns


def draw_instructions():
    window.fill(BLACK)
    title = font_large.render("How to Play", True, WHITE)
    window.blit(
        title,
        (WIDTH // 2 - title.get_width() // 2, 60)
    )

    lines = [
        "You are collecting puzzle pieces to save Earth.",
        "Arrow Up/Down: change lanes.",
        "Arrow Left/Right: move horizontally.",
        "Stars make you go faster",
        "Avoid pollution blocks and collect puzzle pieces.",
        "Collect 3 pieces to clear the level."
    ]
    y = 160
    for line in lines:
        txt = font_small.render(line, True, WHITE)
        window.blit(
            txt,
            (WIDTH // 2 - txt.get_width() // 2, y)
        )
        y += 40

    back = pygame.Rect(50, HEIGHT - 80, 150, 50)
    pygame.draw.rect(window, BUTTON_COLOR, back, border_radius=5)
    window.blit(font_small.render("Back", True, BLACK),
                (back.x + 45, back.y + 12))

    cont = pygame.Rect(WIDTH // 2 - 110, HEIGHT - 90, 220, 60)
    pygame.draw.rect(window, BUTTON_COLOR, cont, border_radius=10)
    window.blit(font_small.render("Continue", True, BLACK),
                (cont.x + 45, cont.y + 20))

    return {"back": back, "continue": cont}


def draw_finish_screen():
    global finish_continue_button, level_completion_status
    window.fill(BLACK)
    t = font_large.render("LEVEL CLEARED!", True, WHITE)
    window.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 100))
    finish_continue_button = pygame.Rect(WIDTH // 2 - 110,
                                         HEIGHT // 2, 220, 60)
    pygame.draw.rect(window, BUTTON_COLOR, finish_continue_button,
                     border_radius=10)
    window.blit(font_medium.render("Continue", True, BLACK),
                (finish_continue_button.x + 40, finish_continue_button.y + 10))

    if current_level_name in level_completion_status:
        level_completion_status[current_level_name] = True

    return finish_continue_button


def draw_win_screen():
    window.fill(BLACK)
    
    # Draw the "You Saved Earth" title
    title = font_large.render("YOU SAVED EARTH!", True, WHITE)
    window.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    
    # Draw the completed puzzle image if it loaded successfully
    if win_image:
        img_x = WIDTH // 2 - win_image.get_width() // 2
        img_y = HEIGHT // 2 - win_image.get_height() // 2 + 30
        window.blit(win_image, (img_x, img_y))
    
    # Draw the sub-text at the bottom
    sub = font_medium.render("All levels complete. Thanks for playing!", True, WHITE)
    window.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT - 100))


def draw_level_common(current_level):
    global level_timer
    window.fill(BLACK)
    draw_scrolling_background()
    draw_player()

    # Obstacles: spawn and update like in latest.py
    level_timer += 1
    spawn_rate = level_obstacle_spawn_rate[current_level]
    if level_timer % spawn_rate == 0:
        spawn_obstacle(current_level)
    update_obstacles(current_level)
    draw_obstacles()

    # Puzzle pieces
    update_puzzle_pieces(current_level)
    for piece in puzzle_pieces:
        window.blit(piece["img"], piece["rect"])

    # ground strip
    ground_rect = pygame.Rect(0, HEIGHT - 40, WIDTH, 40)
    pygame.draw.rect(window, (40, 80, 40), ground_rect)

    # back button
    back = pygame.Rect(50, 20, 150, 50)
    pygame.draw.rect(window, BUTTON_COLOR, back, border_radius=5)
    window.blit(font_small.render("Back", True, BLACK),
                (back.x + 45, back.y + 12))

    info = font_small.render(
        f"Energy: {puzzles_collected}/{PIECES_REQUIRED_TO_FINISH}",
        True,
        WHITE
    )
    window.blit(info, (WIDTH - info.get_width() - 20, 20))

    return {"back": back}

# -------------------------------
# MAIN LOOP
# -------------------------------


def main():
    global current_state, player_y, lane_index, current_level_name, level_timer

    run = True
    active_buttons = {}

    while run:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        active_buttons = {}

        if current_state == STATE_MENU:
            active_buttons = draw_menu()

        elif current_state == STATE_LEVEL_SELECT:
            active_buttons = draw_level_select()

        elif current_state == STATE_INSTRUCTIONS:
            active_buttons = draw_instructions()

        elif current_state in [STATE_LEVEL1, STATE_LEVEL2, STATE_LEVEL3]:
            active_buttons = draw_level_common(current_state)
            handle_player_movement(keys)

        elif current_state == STATE_FINISH:
            draw_finish_screen()

        elif current_state == STATE_WIN:
            draw_win_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and current_state in [
                STATE_LEVEL1, STATE_LEVEL2, STATE_LEVEL3
            ]:
                if event.key == pygame.K_UP and lane_index > 0:
                    lane_index -= 1
                    player_y = lane_positions[lane_index]
                elif event.key == pygame.K_DOWN and lane_index < LANE_COUNT - 1:
                    lane_index += 1
                    player_y = lane_positions[lane_index]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_state == STATE_MENU:
                    if active_buttons.get("start") and \
                            active_buttons["start"].collidepoint(event.pos):
                        current_state = STATE_INSTRUCTIONS
                    elif active_buttons.get("levels") and \
                            active_buttons["levels"].collidepoint(event.pos):
                        current_state = STATE_LEVEL_SELECT

                elif current_state == STATE_LEVEL_SELECT:
                    if active_buttons.get("back") and \
                            active_buttons["back"].collidepoint(event.pos):
                        current_state = STATE_MENU
                    for lvl in ["Level 1", "Level 2", "Level 3"]:
                        if active_buttons.get(lvl) and \
                                active_buttons[lvl].collidepoint(event.pos):
                            start_level(lvl)

                elif current_state == STATE_INSTRUCTIONS:
                    if active_buttons.get("back") and \
                            active_buttons["back"].collidepoint(event.pos):
                        current_state = STATE_MENU
                    if active_buttons.get("continue") and \
                            active_buttons["continue"].collidepoint(event.pos):
                        start_level("Level 1")

                elif current_state in [STATE_LEVEL1, STATE_LEVEL2, STATE_LEVEL3]:
                    if active_buttons.get("back") and \
                            active_buttons["back"].collidepoint(event.pos):
                        current_state = STATE_LEVEL_SELECT

                elif current_state == STATE_FINISH:
                    if finish_continue_button and \
                            finish_continue_button.collidepoint(event.pos):
                        if current_level_name == "Level 1":
                            start_level("Level 2")
                        elif current_level_name == "Level 2":
                            start_level("Level 3")
                        elif current_level_name == "Level 3":
                            current_state = STATE_WIN

                elif current_state == STATE_WIN:
                    current_state = STATE_MENU

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    # Now that the whole script has been read, player_width exists!
    load_character_images() 
    load_obstacle_images()
    main()
