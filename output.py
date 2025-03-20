import pygame
import pygame.midi
import mido
import random
import threading
from queue import Queue

# Ensure pygame uses shared mode for audio recording
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512, allowedchanges=pygame.AUDIO_ALLOW_ANY_CHANGE)

# Initialize Pygame and MIDI
pygame.init()
pygame.midi.init()

# Load MIDI file
midi_file = "fast_midi.mid"  # Replace with your MIDI file
mid = mido.MidiFile(midi_file)

# Set up Pygame window (Vertical Screen, Horizontal Notes)
WIDTH, HEIGHT = 400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Noise-Based MIDI Visualization")

# Colors
BLACK = (0, 0, 0)

# MIDI Player
midi_out = pygame.midi.Output(0)

# Visualization variables
notes = []
scroll_speed = 2
note_width = 30  # Bigger notes
note_height = 10

# Queue to process MIDI in real-time
midi_queue = Queue()

# Function to simulate noise level (Replace with real noise data)
def get_noise_level():
    return random.randint(10, 100)  # Simulated noise level (10 - 100)

# Function to set instrument based on noise level
def set_instrument_by_noise(noise_level):
    if noise_level < 30:
        midi_out.set_instrument(4)  # Electric Piano
    elif noise_level < 60:
        midi_out.set_instrument(66)  # Tenor Sax
    else:
        midi_out.set_instrument(118)  # Synth Drum (Chaotic Noise)

# Function to process MIDI messages and store them in a queue
def midi_player():
    for msg in mid.play():
        if msg.type in ["note_on", "note_off"]:
            midi_queue.put(msg)

# Start MIDI processing in a separate thread
threading.Thread(target=midi_player, daemon=True).start()

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    # Process Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get current noise level and update instrument
    noise_level = get_noise_level()
    set_instrument_by_noise(noise_level)

    # Process MIDI messages in queue
    while not midi_queue.empty():
        msg = midi_queue.get()
        if msg.type == "note_on" and msg.velocity > 0:
            y_pos = (msg.note % 48) * (HEIGHT // 48)  # Map note to screen height
            color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))  # Random color
            notes.append({"note": msg.note, "x": 0, "y": y_pos, "color": color})
            midi_out.note_on(msg.note, msg.velocity)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            midi_out.note_off(msg.note, 0)

    # Move and draw notes
    for note in notes:
        note["x"] += scroll_speed  # Move notes to the right
        pygame.draw.rect(screen, note["color"], (note["x"], note["y"], note_width, note_height))

    # Remove off-screen notes
    notes = [note for note in notes if note["x"] < WIDTH]

    pygame.display.flip()
    clock.tick(60)  # Maintain smooth FPS

pygame.midi.quit()
pygame.quit()
