import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CAR_WIDTH, CAR_HEIGHT = 80, 100  # Car dimensions
FUEL_WIDTH, FUEL_HEIGHT = 50, 50  # Fuel station dimensions
FPS = 60
RACE_TIME = 300  # 5 minutes in seconds
RED_CAR_MAX_SPEED = 10  # Max speed of the car
FUEL_CONSUMPTION_RATE = 0.1  # Fuel consumption per second
FUEL_GAIN = 26  # Amount of fuel gained from fuel stations
FUEL_SPAWN_INTERVAL = 2  # Fuel spawn interval in seconds
FUEL_SPEED = 5  # Fuel stations' downward movement speed
FUEL_SPAWN_COUNT = 3  # Number of fuel stations to spawn

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game")

# Load images for background, fuel, and cars
road2_image = pygame.image.load("road2.png").convert()
road2_image = pygame.transform.scale(road2_image, (WIDTH, HEIGHT)) # Scale background image
fuel_cell_image = pygame.image.load("fuelcell.png").convert_alpha()  # Load the fuel cell image
fuel_cell_image = pygame.transform.scale(fuel_cell_image, (FUEL_WIDTH, FUEL_HEIGHT))  # Scale the fuel cell image

# Load the player car image and scale it
player_car_image = pygame.image.load("aeroplane.png").convert_alpha()  # Load the player's car image
player_car_image = pygame.transform.scale(player_car_image, (CAR_WIDTH, CAR_HEIGHT))  # Scale to fit

# Load obstacle images (other cars)
red_car_image = pygame.image.load("red_car.png").convert_alpha()
yellow_car_image = pygame.image.load("yellow_car.png").convert_alpha()
blue_car_image = pygame.image.load("car2.png").convert_alpha()  # Assuming this is the blue car
red_car_image = pygame.transform.scale(red_car_image, (CAR_WIDTH, CAR_HEIGHT))
yellow_car_image = pygame.transform.scale(yellow_car_image, (CAR_WIDTH, CAR_HEIGHT))
blue_car_image = pygame.transform.scale(blue_car_image, (CAR_WIDTH, CAR_HEIGHT))

#  List of obstacle images and their corresponding colors
obstacle_images = [red_car_image, yellow_car_image, blue_car_image]
obstacle_colors = ["red", "yellow", "blue"]

# Clock for controlling FPS
clock = pygame.time.Clock()

# Variables for background scrolling
background_y1 = 0
background_y2 = -HEIGHT

# Font setup for displaying text on screen
font = pygame.font.SysFont(None, 35)

def draw_background():
    """Handles the scrolling background effect."""
    global background_y1, background_y2
    background_y1 += 5
    background_y2 += 5

    screen.blit(road2_image, (0, background_y1)) # Draw first background
    screen.blit(road2_image, (0, background_y2)) # Draw second background

    # Reset background position when it scrolls past the screen
    if background_y1 >= HEIGHT:
        background_y1 = -HEIGHT
    if background_y2 >= HEIGHT:
        background_y2 = -HEIGHT

def draw_obstacle(x, y, image):
    """Draw an obstacle on the screen."""
    screen.blit(image, (x, y))

def draw_fuel_station(x, y):
    """Draw a fuel station on the screen."""
    screen.blit(fuel_cell_image, (x, y))

def is_overlapping(x, y, obstacles):
    """Check if the new obstacle overlaps with existing ones."""
    new_obstacle_rect = pygame.Rect(x, y, CAR_WIDTH, CAR_HEIGHT)
    for obs in obstacles:
        existing_obstacle_rect = pygame.Rect(obs[0], obs[1], CAR_WIDTH, CAR_HEIGHT)
        if new_obstacle_rect.colliderect(existing_obstacle_rect):
            return True
    return False

def is_overlapping_fuel(x, y, obstacles):
    """Check if the fuel station overlaps with any obstacles."""
    new_fuel_rect = pygame.Rect(x, y, FUEL_WIDTH, FUEL_HEIGHT)
    for obs in obstacles:
        existing_obstacle_rect = pygame.Rect(obs[0], obs[1], CAR_WIDTH, CAR_HEIGHT)
        if new_fuel_rect.colliderect(existing_obstacle_rect):
            return True
    return False
# Show the welcome message at the beginning
def show_welcome_message():
    """Displays the welcome message and instructions at the start of the game."""
    screen.fill(BLACK)  # Fill screen with black
    welcome_message_1 = pygame.font.SysFont(None, 30).render("Welcome to the Hydrogen Racing Game!", True, WHITE)
    mission_message = pygame.font.SysFont(None, 22).render("Your mission: Convert 5000 cars to hydrogen-powered vehicles by avoiding obstacles and collecting fuel.", True, WHITE)

    instructions_message = pygame.font.SysFont(None, 22).render("Use the arrow keys to move your car and race towards the goal. Stay fueled and avoid crashes!", True, WHITE)


    screen.blit(welcome_message_1, (WIDTH // 2 - welcome_message_1.get_width() // 2, HEIGHT // 2 - welcome_message_1.get_height() // 2 - 50)) # Position welcome message
    screen.blit(mission_message, (WIDTH // 2 - mission_message.get_width() // 2, HEIGHT // 2))   # Position mission message
    screen.blit(instructions_message, (WIDTH // 2 - instructions_message.get_width() // 2, HEIGHT // 2 + 50))  # Position instructions


    pygame.display.flip()  # Update the screen
    time.sleep(4)  # Display the message for 4 seconds

def get_player_name():
    """Get the player's name input and show the welcome message."""
    input_active = True
    player_name = ''
    show_welcome_message()   # Show the initial welcome message
    while input_active:
        screen.fill(BLACK)
        name_prompt = font.render("Enter your name: " + player_name, True, WHITE)
        screen.blit(name_prompt, (WIDTH // 2 - name_prompt.get_width() // 2, HEIGHT // 2 - name_prompt.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                input_active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False      # Stop input when Enter is pressed
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]     # Remove last character on Backspace
                else:
                    player_name += event.unicode    # Add new character to player name

        pygame.display.flip()

    return player_name

def game_loop(player_name):
    """Main game loop where gameplay happens."""
    x = (WIDTH * 0.45)     # Starting position for the car (centered)
    y = (HEIGHT * 0.6)     # Starting position for the car (lower half)
    x_change = 0
    converted_cars = 0     # Number of converted cars
    fuel = 100             # Initial fuel level
    start_time = time.time()     # Start timer
    last_fuel_spawn_time = time.time()    # Last time fuel spawned
    out_of_fuel = False

    obstacles = []    # List to store obstacles
    fuel_stations = []    # List to store fuel stations

    while not out_of_fuel:
        draw_background()     # Draw the moving background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()     # Check key presses for movement
        if keys[pygame.K_LEFT]:
            x_change = -5            # Move left
        elif keys[pygame.K_RIGHT]:
            x_change = 5             # Move right
        else:
            x_change = 0

        x += x_change    # Update car position
        x = max(220, min(WIDTH - CAR_WIDTH, x))    # Prevent car from going off-screen

        # Spawn obstacles
        if random.randint(1, 10) == 1:
            obstacle_x = random.randint(220, WIDTH - 220 - CAR_WIDTH)
            obstacle_y = random.randint(-CAR_HEIGHT * 2, -CAR_HEIGHT)
            obstacle_color = random.choice(obstacle_colors)

            if obstacle_color == "red":
                obstacle_image = red_car_image
            elif obstacle_color == "yellow":
                obstacle_image = yellow_car_image
            else:
                obstacle_image = blue_car_image

            # Ensure no overlap with other obstacles
            if not is_overlapping(obstacle_x, obstacle_y, obstacles):
                obstacles.append([obstacle_x, obstacle_y, obstacle_image, obstacle_color])

        # Move and draw obstacles
        for obstacle in obstacles:
            obstacle[1] += 5      # Move downwards
            draw_obstacle(obstacle[0], obstacle[1], obstacle[2])

        obstacles = [obs for obs in obstacles if obs[1] < HEIGHT]

        # Convert cars
        for obstacle in obstacles:
            if (y < obstacle[1] + CAR_HEIGHT and
                    y + CAR_HEIGHT > obstacle[1] and
                    x < obstacle[0] + CAR_WIDTH and
                    x + CAR_WIDTH > obstacle[0]):
                if obstacle[3] in ["yellow", "blue"]:
                    obstacle[2] = red_car_image
                    obstacle[3] = "red"
                    converted_cars += 25

        # Check if player reaches the goal
        if converted_cars >= 5000:
            message = font.render("Congratulations! You have converted 5000 hydrogen cars!", True, WHITE)
            screen.fill(BLACK)
            screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - message.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(5000)
            break

        # Spawn fuel stations
        if time.time() - last_fuel_spawn_time >= FUEL_SPAWN_INTERVAL:
            last_fuel_spawn_time = time.time()
            for _ in range(FUEL_SPAWN_COUNT):
                fuel_x = random.randint(220, WIDTH - 220 - FUEL_WIDTH)
                fuel_y = random.randint(-FUEL_HEIGHT * 2, -FUEL_HEIGHT)
                if not is_overlapping_fuel(fuel_x, fuel_y, fuel_stations):
                    fuel_stations.append([fuel_x, fuel_y])

        # Move and draw fuel stations
        for fuel_station in fuel_stations:
            fuel_station[1] += FUEL_SPEED
            draw_fuel_station(fuel_station[0], fuel_station[1])

        fuel_stations = [fs for fs in fuel_stations if fs[1] < HEIGHT]

        # Collect fuel
        for fuel_station in fuel_stations:
            if (y < fuel_station[1] + FUEL_HEIGHT and
                    y + CAR_HEIGHT > fuel_station[1] and
                    x < fuel_station[0] + FUEL_WIDTH and
                    x + CAR_WIDTH > fuel_station[0]):
                fuel += FUEL_GAIN
                fuel_stations.remove(fuel_station)

        # Update fuel and timer
        elapsed_time = time.time() - start_time
        if fuel > 0:
            fuel -= FUEL_CONSUMPTION_RATE * (elapsed_time / FPS)
        else:
            out_of_fuel = True

        # Draw player car
        screen.blit(player_car_image, (x, y))
        # Draw HUD
        player_name_text = font.render("Player: {}".format(player_name), True, WHITE)
        screen.blit(player_name_text, (10, 10))

        fuel_text = font.render("Fuel: {:.1f}".format(fuel), True, WHITE)
        screen.blit(fuel_text, (10, 40))

        converted_cars_text = font.render("Converted Cars: {}".format(converted_cars), True, WHITE)
        screen.blit(converted_cars_text, (10, 70))

        time_left = max(0, RACE_TIME - int(elapsed_time))
        timer_text = font.render("Time Left: {}s".format(time_left), True, WHITE)
        screen.blit(timer_text, (WIDTH - 200, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

player_name = get_player_name()
game_loop(player_name)

