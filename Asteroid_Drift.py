import board
import displayio
import adafruit_imageload
import random
import time
import audiobusio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_display_text import label
import terminalio
import math
import digitalio
import pulseio
import simpleio
import os

# Setup display
display = board.DISPLAY

# Load spaceship and asteroid images
spaceship_bitmap, spaceship_palette = adafruit_imageload.load(
    "/spaceship.bmp",
    bitmap=displayio.Bitmap,
    palette=displayio.Palette
)

asteroid_bitmap, asteroid_palette = adafruit_imageload.load(
    "/asteroid.bmp",
    bitmap=displayio.Bitmap,
    palette=displayio.Palette
)

# Initialize buzzer pin
buzzer = board.BUZZER

# Function to reset game variables
def reset_game():
    global score, asteroids, charge_level
    score = 0
    asteroids = displayio.Group()
    sprites.append(asteroids)
    charge_level = 0
    for asteroid in asteroids:
            asteroids.remove(asteroid)

# Create a spaceship sprite
spaceship_sprite = displayio.TileGrid(spaceship_bitmap, pixel_shader=spaceship_palette)
spaceship_sprite.x = 120
spaceship_sprite.y = 120

# Create a group for sprites
sprites = displayio.Group()
sprites.append(spaceship_sprite)

# Set the root group to display
display.root_group = (sprites)

# Setup joystick buttons using DigitalInOut
joystick_up = DigitalInOut(board.SWITCH_UP)
joystick_down = DigitalInOut(board.SWITCH_DOWN)
joystick_left = DigitalInOut(board.SWITCH_LEFT)
joystick_right = DigitalInOut(board.SWITCH_RIGHT)
joystick_pressed = DigitalInOut(board.SWITCH_PRESS)

# Set the direction for the joystick buttons
for button in [joystick_up, joystick_down, joystick_left, joystick_right, joystick_pressed]:
    button.direction = Direction.INPUT
    button.pull = Pull.UP  # Assuming the buttons are active low

# Game variables
asteroid_speed = 5
score = 0
collision_threshold = 20  # Set the collision threshold distance
charge_threshold = 100  # Set the charge threshold for destroying asteroids
charge_increment = 1  # Set the charge increment per iteration

# Create score label
score_label = label.Label(terminalio.FONT, text="Score: 0", color=0xFFFFFF)
score_label.anchor_point = (0, 0)
score_label.anchored_position = (5, 5)
sprites.append(score_label)

# Create charge label
charge_label = label.Label(terminalio.FONT, text="Charge: 0", color=0xFFFFFF)
charge_label.anchor_point = (0, 0)
charge_label.anchored_position = (5, 30)
sprites.append(charge_label)

def play_asteroid_tune():
    """ Play a simple tune using the buzzer pin for an asteroid creation. """
    simpleio.tone(buzzer, 440, duration=0.01)

def play_collision_tune():
    """ Play a different tune using the buzzer pin for a collision. """
    simpleio.tone(buzzer, 440, duration=0.5)
    simpleio.tone(buzzer, 415, duration=0.5)
    simpleio.tone(buzzer, 392, duration=0.5)
    simpleio.tone(buzzer, 370, duration=1)

def read_joystick():
    """ Check joystick state and return the movement direction. """
    if not joystick_up.value:  # Active low
        return (0, -2)  # Move up
    elif not joystick_down.value:  # Active low
        return (0, 2)   # Move down
    elif not joystick_left.value:  # Active low
        return (-2, 0)  # Move left
    elif not joystick_right.value:  # Active low
        return (2, 0)   # Move right
    return (0, 0)  # No movement

def create_asteroid():
    """ Function to create an asteroid at a random x position above the screen. """
    play_asteroid_tune()
    asteroid = displayio.TileGrid(asteroid_bitmap, pixel_shader=asteroid_palette)
    asteroid.x = random.randint(0, display.width - asteroid.width)
    asteroid.y = -asteroid.height  # Start above the screen
    return asteroid

def check_collision(spaceship, asteroid):
    """ Check for collision based on distance between spaceship and asteroid. """
    # Calculate the center points of both sprites
    spaceship_center_x = spaceship.x + (spaceship.width // 2)
    spaceship_center_y = spaceship.y + (spaceship.height // 2)
    asteroid_center_x = asteroid.x + (asteroid.width // 2)
    asteroid_center_y = asteroid.y + (asteroid.height // 2)

    # Calculate the distance between the two centers
    distance = math.sqrt((spaceship_center_x - asteroid_center_x) ** 2 +
                         (spaceship_center_y - asteroid_center_y) ** 2)
    
    # Check if the distance is less than the collision threshold
    return distance < collision_threshold

def charge_up():
    """ Charge the power level by the specified increment. """
    global charge_level
    charge_level += charge_increment

def discharge():
    """ Discharge the power level to destroy all asteroids. """
    global charge_level
    if charge_level > 99:
        charge_level -= charge_threshold
        for asteroid in asteroids:
            asteroids.remove(asteroid)
        simpleio.tone(buzzer, 500, duration=0.5)

# Main game loop
reset_game()
while True:
    # Read joystick input
    dx, dy = read_joystick()

    # Move spaceship based on joystick input
    spaceship_sprite.x += dx
    spaceship_sprite.y += dy

    # Keep spaceship within screen bounds
    spaceship_sprite.x = max(0, min(display.width - spaceship_sprite.width, spaceship_sprite.x))
    spaceship_sprite.y = max(0, min(display.height - spaceship_sprite.height, spaceship_sprite.y))

    # Charge up the power level
    charge_up()

    # Create a new asteroid periodically
    if random.randint(0, 30) == 0:
        asteroids.append(create_asteroid())

    # Move asteroids and check for collisions
    for asteroid in asteroids:
        asteroid.y += asteroid_speed

        # Check for collision with the spaceship
        if check_collision(spaceship_sprite, asteroid):
            play_collision_tune()                
            print("Game Over! Final Score:", score)
            score_label.text = f"Score: {score}"
            time.sleep(2)  # Display final score for 2 seconds
            break  # Exit the inner loop to restart the game

        # Remove asteroids that have gone off screen
        if asteroid.y > display.height:
            asteroids.remove(asteroid)
            score += 1  # Increase score for dodging

    # Update score and charge display on the screen
    score_label.text = f"Score: {score}"
    charge_label.text = f"Charge: {charge_level}"

    if not joystick_pressed.value:
        discharge()

    time.sleep(0.01)  # Control the game loop speed