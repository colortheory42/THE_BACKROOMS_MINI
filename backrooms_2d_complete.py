import pygame
import random
import math
import json
import os
from datetime import datetime

pygame.init()

# Screen setup
WIDTH, HEIGHT = 4480, 2520
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("The Backrooms - Level 0")

# Colors - Backrooms palette
BG_COLOR = (40, 35, 20)  # Dark background
WALL_COLOR = (180, 170, 120)  # Yellowish aged walls
FLASHLIGHT_COLOR = (255, 240, 180)  # Warm flashlight
SHADOW_COLOR = (20, 18, 10)  # Deep shadows
CARPET_COLOR = (60, 45, 25)  # Moist carpet color
CEILING_COLOR = (200, 190, 140)  # Fluorescent lighting color

# Player
player_pos = [WIDTH // 2, HEIGHT // 2]  # Always starts at center of current panel
player_speed = 3
player_radius = 8
flashlight_radius = 200
flashlight_cone_angle = 0.8

# Current room/panel
current_room_x = 0
current_room_y = 0

# World settings - each room is exactly one screen
ROOM_WIDTH = WIDTH
ROOM_HEIGHT = HEIGHT
loaded_rooms = {}
visited_rooms = set()

# Atmosphere settings
ambient_light = 0.3
fluorescent_flicker = 0
footstep_timer = 0

# Footstep effects
footstep_ripples = []

# Save/load UI
save_message = ""
save_message_timer = 0.0
SAVE_DIR = "backrooms_2d_saves"


# === SAVE/LOAD SYSTEM ===

def ensure_save_dir():
    """Create save directory if it doesn't exist."""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def save_game(slot=1):
    """Save the game state."""
    global save_message, save_message_timer
    
    ensure_save_dir()
    
    save_data = {
        'version': '1.0',
        'timestamp': datetime.now().isoformat(),
        'player': {
            'x': player_pos[0],
            'y': player_pos[1]
        },
        'current_room': {
            'x': current_room_x,
            'y': current_room_y
        },
        'visited_rooms': list(visited_rooms),  # Convert set to list for JSON
        'stats': {
            'rooms_explored': len(visited_rooms)
        }
    }
    
    filename = os.path.join(SAVE_DIR, f"save_slot_{slot}.json")
    
    try:
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"Game saved to slot {slot}!")
        save_message = f"Game saved to slot {slot}!"
        save_message_timer = 3.0
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        save_message = "Save failed!"
        save_message_timer = 3.0
        return False


def load_game(slot=1):
    """Load game state from a slot."""
    global player_pos, current_room_x, current_room_y, visited_rooms
    global loaded_rooms, save_message, save_message_timer
    
    filename = os.path.join(SAVE_DIR, f"save_slot_{slot}.json")
    
    if not os.path.exists(filename):
        print(f"No save found in slot {slot}")
        save_message = f"No save found in slot {slot}!"
        save_message_timer = 3.0
        return False
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Restore player position
        player_pos[0] = data['player']['x']
        player_pos[1] = data['player']['y']
        
        # Restore current room
        current_room_x = data['current_room']['x']
        current_room_y = data['current_room']['y']
        
        # Convert visited_rooms list back to set of tuples
        visited_rooms = set(tuple(room) for room in data['visited_rooms'])
        
        # Regenerate current room if needed
        current_room_key = (current_room_x, current_room_y)
        if current_room_key not in loaded_rooms:
            starting = (current_room_key == (0, 0))
            loaded_rooms[current_room_key] = generate_backrooms_room(
                current_room_x, 
                current_room_y, 
                starting_room=starting
            )
        
        print(f"Game loaded from slot {slot}!")
        print(f"Position: Room ({current_room_x}, {current_room_y})")
        print(f"Rooms explored: {len(visited_rooms)}")
        
        save_message = f"Game loaded from slot {slot}!"
        save_message_timer = 3.0
        return True
    except Exception as e:
        print(f"Error loading game: {e}")
        save_message = "Load failed!"
        save_message_timer = 3.0
        return False


# === FOOTSTEP RIPPLES ===

class FootstepRipple:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 30
        self.lifetime = 60
        self.age = 0

    def update(self):
        self.age += 1
        self.radius = (self.age / self.lifetime) * self.max_radius
        return self.age < self.lifetime

    def draw(self, surface):
        alpha = max(0, 255 - (self.age * 4))
        if alpha > 0:
            color = (100, 80, 40, alpha)
            ripple_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surf, color, (self.radius, self.radius), int(self.radius), 2)
            surface.blit(ripple_surf, (self.x - self.radius, self.y - self.radius))


# === ROOM GENERATION ===

def generate_backrooms_room(room_x, room_y, starting_room=False):
    """Generate a single room that fills the entire screen"""
    walls = []

    # Use room coordinates as seed for consistent generation
    seed = hash((room_x, room_y)) % 1000
    random.seed(seed)

    wall_thickness = 8

    # Create room borders (but with doorways)
    door_width = 80

    # Top wall with door
    door_x = WIDTH // 2 - door_width // 2
    walls.append(pygame.Rect(0, 0, door_x, wall_thickness))  # Left part
    walls.append(pygame.Rect(door_x + door_width, 0, WIDTH - (door_x + door_width), wall_thickness))  # Right part

    # Bottom wall with door
    walls.append(pygame.Rect(0, HEIGHT - wall_thickness, door_x, wall_thickness))  # Left part
    walls.append(pygame.Rect(door_x + door_width, HEIGHT - wall_thickness, WIDTH - (door_x + door_width),
                             wall_thickness))  # Right part

    # Left wall with door
    door_y = HEIGHT // 2 - door_width // 2
    walls.append(pygame.Rect(0, 0, wall_thickness, door_y))  # Top part
    walls.append(pygame.Rect(0, door_y + door_width, wall_thickness, HEIGHT - (door_y + door_width)))  # Bottom part

    # Right wall with door
    walls.append(pygame.Rect(WIDTH - wall_thickness, 0, wall_thickness, door_y))  # Top part
    walls.append(pygame.Rect(WIDTH - wall_thickness, door_y + door_width, wall_thickness,
                             HEIGHT - (door_y + door_width)))  # Bottom part

    # Add some internal maze-like features (but not in starting room)
    if not starting_room:
        num_features = random.randint(2, 5)
        for _ in range(num_features):
            if random.random() < 0.7:  # 70% chance for internal features
                # Small pillar
                pillar_size = random.randint(20, 40)
                pillar_x = random.randint(50, WIDTH - 50 - pillar_size)
                pillar_y = random.randint(50, HEIGHT - 50 - pillar_size)
                walls.append(pygame.Rect(pillar_x, pillar_y, pillar_size, pillar_size))
            else:
                # Short wall segment
                if random.random() < 0.5:  # Horizontal wall
                    wall_length = random.randint(60, 150)
                    wall_x = random.randint(40, WIDTH - 40 - wall_length)
                    wall_y = random.randint(80, HEIGHT - 80)
                    walls.append(pygame.Rect(wall_x, wall_y, wall_length, wall_thickness))
                else:  # Vertical wall
                    wall_height = random.randint(60, 150)
                    wall_x = random.randint(80, WIDTH - 80)
                    wall_y = random.randint(40, HEIGHT - 40 - wall_height)
                    walls.append(pygame.Rect(wall_x, wall_y, wall_thickness, wall_height))

    return walls


# === PLAYER MOVEMENT ===

def move_player(dx, dy):
    """Move player and handle room transitions"""
    global current_room_x, current_room_y, footstep_ripples

    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy

    # Check for room transitions first
    room_changed = False

    # Check if moving through doorways to adjacent rooms
    if new_x <= 10:  # Left edge - go to left room
        current_room_x -= 1
        player_pos[0] = WIDTH - 50  # Appear on right side of new room
        room_changed = True
    elif new_x >= WIDTH - 10:  # Right edge - go to right room
        current_room_x += 1
        player_pos[0] = 50  # Appear on left side of new room
        room_changed = True
    elif new_y <= 10:  # Top edge - go to room above
        current_room_y -= 1
        player_pos[1] = HEIGHT - 50  # Appear at bottom of new room
        room_changed = True
    elif new_y >= HEIGHT - 10:  # Bottom edge - go to room below
        current_room_y += 1
        player_pos[1] = 50  # Appear at top of new room
        room_changed = True

    if room_changed:
        # Clear footsteps when changing rooms
        footstep_ripples = []
        # Log new room visit
        room_key = (current_room_x, current_room_y)
        if room_key not in visited_rooms:
            visited_rooms.add(room_key)
            print(f"Entered room: {room_key}")
        # Generate new room if needed
        if room_key not in loaded_rooms:
            starting = (room_key == (0, 0))
            loaded_rooms[room_key] = generate_backrooms_room(current_room_x, current_room_y, starting_room=starting)
        return

    # Normal movement within room - check wall collisions
    player_rect = pygame.Rect(new_x - player_radius, new_y - player_radius, player_radius * 2, player_radius * 2)

    # Get current room walls
    current_room_key = (current_room_x, current_room_y)
    if current_room_key in loaded_rooms:
        for wall in loaded_rooms[current_room_key]:
            if player_rect.colliderect(wall):
                return  # Collision detected, don't move

    # No collision, move player
    player_pos[0] = new_x
    player_pos[1] = new_y

    # Add footstep effects
    if abs(dx) > 0 or abs(dy) > 0:
        footstep_ripples.append(FootstepRipple(player_pos[0], player_pos[1]))
        # Limit ripples to prevent memory issues
        if len(footstep_ripples) > 8:
            footstep_ripples.pop(0)


# === RENDERING ===

def draw_lighting_overlay():
    """Create atmospheric lighting with shadows"""
    global fluorescent_flicker

    # Create a dark overlay
    dark_overlay = pygame.Surface((WIDTH, HEIGHT))
    dark_overlay.fill(SHADOW_COLOR)

    # Flickering fluorescent effect
    fluorescent_flicker += random.uniform(-0.1, 0.1)
    fluorescent_flicker = max(0, min(1, fluorescent_flicker + 0.02))

    base_light = int(255 * (ambient_light + fluorescent_flicker * 0.1))

    # Create flashlight cone
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - player_pos[0]
    dy = mouse_y - player_pos[1]
    flashlight_angle = math.atan2(dy, dx)

    # Draw multiple light rays for smoother cone
    for i in range(15):
        angle_offset = (i - 7) * flashlight_cone_angle / 15
        ray_angle = flashlight_angle + angle_offset

        # Cast light ray
        for distance in range(10, flashlight_radius, 8):
            light_x = player_pos[0] + math.cos(ray_angle) * distance
            light_y = player_pos[1] + math.sin(ray_angle) * distance

            # Check bounds
            if light_x < 0 or light_x >= WIDTH or light_y < 0 or light_y >= HEIGHT:
                break

            # Check if ray hits wall
            hit_wall = False
            test_rect = pygame.Rect(light_x - 2, light_y - 2, 4, 4)
            current_room_key = (current_room_x, current_room_y)
            if current_room_key in loaded_rooms:
                for wall in loaded_rooms[current_room_key]:
                    if test_rect.colliderect(wall):
                        hit_wall = True
                        break

            if hit_wall:
                break

            # Draw light spot
            intensity = max(0, 1 - (distance / flashlight_radius))
            light_radius = int(12 * intensity)
            if light_radius > 0:
                light_color = (int(255 * intensity), int(240 * intensity), int(180 * intensity))
                pygame.draw.circle(dark_overlay, light_color, (int(light_x), int(light_y)), light_radius)

    # Apply lighting overlay
    screen.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_MULT)


def draw_carpet_texture():
    """Draw subtle carpet texture for current room"""
    for x in range(0, WIDTH, 40):
        for y in range(0, HEIGHT, 40):
            # Add room coordinates to pattern for variation
            pattern_seed = (x // 40 + y // 40 + current_room_x + current_room_y) % 2
            if pattern_seed:
                pygame.draw.rect(screen, CARPET_COLOR, (x, y, 40, 40))


# === INITIALIZATION ===

# Initialize starting room
current_room_key = (0, 0)
loaded_rooms[current_room_key] = generate_backrooms_room(0, 0, starting_room=True)
visited_rooms.add(current_room_key)

# Game loop
running = True
clock = pygame.time.Clock()
frame_count = 0

print("=" * 60)
print("Welcome to the Backrooms - 2D Edition")
print("=" * 60)
print("Controls:")
print("  WASD - Move between rooms")
print("  F5 - Quick save (slot 1)")
print("  F9 - Quick load (slot 1)")
print("  ENTER - Search for room coordinates")
print("  ESC - Exit")
print("=" * 60)

# === MAIN LOOP ===

while running:
    frame_count += 1
    dt = 1/60  # Assuming 60 FPS

    # Update save message timer
    if save_message_timer > 0:
        save_message_timer -= dt
        if save_message_timer <= 0:
            save_message = ""

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # Quick save (F5)
            if event.key == pygame.K_F5:
                save_game(slot=1)
            
            # Quick load (F9)
            elif event.key == pygame.K_F9:
                load_game(slot=1)
            
            # Room coordinate search
            elif event.key == pygame.K_RETURN:
                try:
                    input_coords = input("Enter room coordinates to search (x,y): ")
                    x_str, y_str = input_coords.split(",")
                    coords = (int(x_str.strip()), int(y_str.strip()))
                    if coords in visited_rooms:
                        print(f"Room {coords} has been visited.")
                    else:
                        print(f"Room {coords} is unknown (not yet visited).")
                except:
                    print("Invalid format. Use: x,y")
            
            # Exit
            elif event.key == pygame.K_ESCAPE:
                running = False

    # Handle movement
    keys = pygame.key.get_pressed()
    moving = False
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        move_player(0, -player_speed)
        moving = True
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        move_player(0, player_speed)
        moving = True
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        move_player(-player_speed, 0)
        moving = True
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        move_player(player_speed, 0)
        moving = True

    # Clear screen with carpet background
    screen.fill(BG_COLOR)
    draw_carpet_texture()

    # Update and draw footstep ripples
    footstep_ripples = [ripple for ripple in footstep_ripples if ripple.update()]
    for ripple in footstep_ripples:
        ripple.draw(screen)

    # Draw current room walls
    current_room_key = (current_room_x, current_room_y)
    if current_room_key in loaded_rooms:
        for wall in loaded_rooms[current_room_key]:
            # Add slight color variation for worn look
            wall_shade = random.randint(-8, 8)
            wall_color = (
                max(0, min(255, WALL_COLOR[0] + wall_shade)),
                max(0, min(255, WALL_COLOR[1] + wall_shade)),
                max(0, min(255, WALL_COLOR[2] + wall_shade))
            )
            pygame.draw.rect(screen, wall_color, wall)
            # Add subtle highlight
            pygame.draw.rect(screen, CEILING_COLOR, wall, 1)

    # Draw player
    player_color = (200, 100, 100)
    if moving:
        player_color = (220, 120, 120)

    pygame.draw.circle(screen, player_color, (int(player_pos[0]), int(player_pos[1])), player_radius)
    pygame.draw.circle(screen, (255, 255, 255), (int(player_pos[0]), int(player_pos[1])), player_radius, 2)

    # Apply atmospheric lighting
    draw_lighting_overlay()

    # Draw UI elements
    font = pygame.font.Font(None, 36)
    room_text = font.render(f"Room: ({current_room_x}, {current_room_y})", True, (200, 200, 150))
    rooms_visited_text = font.render(f"Rooms Visited: {len(visited_rooms)}", True, (200, 200, 150))

    screen.blit(room_text, (10, 10))
    screen.blit(rooms_visited_text, (10, 50))

    # Show save message
    if save_message:
        save_text = font.render(save_message, True, (100, 255, 100))
        screen.blit(save_text, (10, 90))

    # Show navigation hint for first few seconds
    if frame_count < 300:  # Show for first 5 seconds
        help_text = font.render("Walk to screen edges to enter new rooms | F5: Save | F9: Load", True, (255, 255, 100))
        text_rect = help_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(help_text, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print(f"\nSession ended. You explored {len(visited_rooms)} rooms in the Backrooms.")
