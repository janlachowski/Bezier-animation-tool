import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from frame_curve_editor import interactive_pick_and_drag_points, frames_in_memory
from matplotlib.animation import ArtistAnimation
from pathlib import Path

# Path to the folder containing the script
base_path = Path(__file__).parent

# Path to the folder with animation frames
frames_path = base_path / "animation"
# frames_path = base_path / "saved_animations" / 

# List of frame files from the folder (sorted by the number at the end)
image_files = sorted(frames_path.glob("frame*.png"), key=lambda f: int(f.stem[5:]))

for image_file in image_files:
    img = mpimg.imread(image_file) # Load image
    frames_in_memory.append(img)

do_animate = interactive_pick_and_drag_points()

if do_animate:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis('off')  # Hide axes
    frames = []  # List of frames for the animation

    # Add images as animation frames
    for arr in frames_in_memory:
        frame = [ax.imshow(arr, animated=True)]  # Add image as a frame
        frames.append(frame)

    # Remove the initial blank frame
    frames = frames[1:]

    # Create the animation
    ani = ArtistAnimation(fig, frames, interval=100, blit=True)

    # Show the animation
    plt.show()

    # Save the animation as a GIF...
    ani.save(frames_path / "animation.gif", writer="pillow", fps=10)

    # ...or as MP4
    # ani.save(frames_path / "animation.mp4", writer="ffmpeg", fps=10)