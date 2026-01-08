# The Backrooms - 2D Edition

A top-down exploration of infinite liminal space with atmospheric lighting, procedural room generation, and persistent save/load system.

## Overview

The 2D Backrooms is a companion piece to the 3D first-person version. While the 3D version emphasizes temporal immersion (3+ hours per zone), the 2D version focuses on **spatial mapping** - exploring and cataloging an infinite grid of procedurally generated rooms.

## Features

### Core Gameplay
- **Infinite procedural rooms** - Deterministically generated from coordinates
- **Room-to-room traversal** - Walk to screen edges to transition
- **Visited rooms tracking** - Every room you enter is logged
- **Coordinate search system** - Check if you've visited specific rooms

### Atmosphere
- **Dynamic flashlight cone** - Follows mouse cursor
- **Shadow casting** - Light rays blocked by walls
- **Flickering fluorescent lighting** - Subtle ambient variation
- **Footstep ripples** - Visual feedback on moist carpet
- **Worn wall textures** - Subtle color variation

### Persistence
- **Save/load system** - Preserve exploration progress across sessions
- **Automatic room regeneration** - Loaded rooms use same seed for consistency
- **Exploration statistics** - Track total rooms visited

## Installation

### Requirements
- Python 3.7+
- Pygame

### Setup
```bash
# Install pygame
pip install pygame

# Run the game
python backrooms_2d_complete.py
```

## Controls

### Movement
- **W / UP** - Move up
- **S / DOWN** - Move down
- **A / LEFT** - Move left
- **D / RIGHT** - Move right

### System
- **F5** - Quick save (slot 1)
- **F9** - Quick load (slot 1)
- **ENTER** - Search room coordinates
- **ESC** - Exit game
- **Mouse** - Aim flashlight

## Gameplay

### Room Transitions
Walk to any screen edge to transition to an adjacent room. Doorways are centered on each wall.

- **Left edge** → Room (x-1, y)
- **Right edge** → Room (x+1, y)
- **Top edge** → Room (x, y-1)
- **Bottom edge** → Room (x, y+1)

### Room Generation
Each room is procedurally generated based on its coordinates:
- **Starting room (0,0)** - Empty space with doorways
- **Other rooms** - May contain internal pillars and wall segments
- **Deterministic** - Same coordinates always generate same room

### Coordinate Search
Press ENTER and type coordinates (e.g., `5,3`) to check if you've visited that room.

### Save System
Saves are stored in `backrooms_2d_saves/` directory as JSON files.

**What gets saved:**
- Player position within current room
- Current room coordinates (x, y)
- Complete set of visited rooms
- Exploration statistics
- Timestamp

## Technical Details

### Display
- **Resolution**: 4480 x 2520 (fullscreen)
- **Frame rate**: 60 FPS
- **Room size**: 1 screen = 1 room

### Generation
- **Seed system**: `hash((room_x, room_y)) % 1000`
- **Wall thickness**: 8 pixels
- **Doorway width**: 80 pixels
- **Internal features**: 2-5 per room (random)

### Lighting
- **Ambient light**: 30% base visibility
- **Flashlight radius**: 200 pixels
- **Cone angle**: 0.8 radians
- **Ray count**: 15 rays per frame
- **Shadow casting**: Walls block light rays

## Design Philosophy

### Spatial vs Temporal Horror

The 2D version explores **spatial infinity** rather than temporal infinity:

- **3D version**: Takes 3+ hours to cross one zone (temporal horror)
- **2D version**: Can cross dozens of rooms per minute (spatial horror)

The horror comes not from the time investment, but from the **infinite room count**:
- How many rooms exist? Infinite.
- How many can you remember? Very few.
- How do you find your way back? You can't.

### Mapping the Unmappable

The coordinate system and visited rooms tracker give the illusion of control:
- You can search for specific rooms
- You can count how many you've visited
- You can see your current position

But the space is **still infinite**. No amount of cataloging will ever be complete.

### Save System as Memory

The save system isn't just a convenience - it's a **prosthetic memory**. Without it, your exploration is ephemeral. The visited rooms set is the only proof you were ever there.

## Performance

### Optimization Features
- **Footstep ripple cap**: Maximum 8 active ripples
- **Lazy room generation**: Rooms only generated when visited
- **No persistent room data**: Only current room is fully loaded

### Known Limitations
- **No minimap**: Infinite space cannot be mapped
- **No breadcrumb trail**: You must remember your path
- **No room persistence**: Rooms are regenerated from seed each visit

## File Structure

```
backrooms_2d_complete.py       # Complete game + save system
backrooms_2d_saves/            # Save directory (auto-created)
  └── save_slot_1.json         # Quick save file
```

## Comparison to 3D Version

| Feature | 2D Version | 3D Version |
|---------|-----------|------------|
| Perspective | Top-down | First-person |
| Unit of space | Rooms (1 screen) | Zones (400 units) |
| Traversal time | Seconds per room | 3+ hours per zone |
| Navigation | Coordinate-based | Immersive wandering |
| Horror type | Spatial infinity | Temporal infinity |
| Lighting | Flashlight cone | Ambient + fog |
| Destruction | No | Yes (walls + debris) |
| Save/load | Yes | Yes |

## Tips for Exploration

1. **Pick a direction and commit** - Walking in circles won't reveal variety
2. **Use the coordinate search** - Track rooms you want to return to
3. **Save frequently** - Your visited rooms data is valuable
4. **Look for patterns** - Room generation has biases based on coordinates
5. **Accept the infinite** - You will never see all rooms

## Philosophy

The 2D Backrooms demonstrates that **scale transcends dimension**. Even in a simple top-down view, infinity is incomprehensible. The ability to see the entire room at once doesn't make the space less vast - it just makes the vastness more obvious.

You can count. You can catalog. You can map. But you cannot finish.

That's the Backrooms.

## Credits

Built from first principles using Pygame. No external room data, no texture files, all procedurally generated at runtime.

Companion to THE_BACKROOMS 3D: https://github.com/colortheory42/THE_BACKROOMS.git

---

*"If you're not careful and you noclip out of reality in the wrong areas, you'll end up in the Backrooms..."*
