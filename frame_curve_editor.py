import drawing
import matplotlib.image as mpimg
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.widgets import Button
import io
import json

# Global list to store frames in memory (as np.ndarray)
frames_in_memory = []

def interactive_pick_and_drag_points():
    """
    Function for creating animation frames using Bézier curves.

    Returns:
    ----------
    was_end_clicked : bool 
        Indicates whether the user ended the process by clicking the "End" button 
        (as opposed to closing the window forcefully).
    """

    # Path to the script directory  
    base_path = Path(__file__).parent

    # Start animation from the last frame
    index = len(frames_in_memory) - 1

    # Empty background image
    blank = np.ones((1000, 1600, 3))

    # Create figure and plot
    fig, ax = plt.subplots(figsize=(16, 10))
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()  # fullscreen mode
    ax.imshow(frames_in_memory[index], extent=[0, 1600, 0, 1000], cmap='gray', alpha=0.2)
    ax.set_aspect('equal')

    # Button positions [left, bottom, width, height]
    ax_save = plt.axes([0, 0, 0.1, 0.075])      # Save button    
    ax_end = plt.axes([0.9, 0, 0.1, 0.075])     # End button

    # Create buttons
    button_save = Button(ax_save, 'Save', color='royalblue', hovercolor='cornflowerblue')
    button_end = Button(ax_end, 'End', color='forestgreen', hovercolor='limegreen')
    for button in [button_save, button_end]:
        button.label.set_fontsize(13)
        button.label.set_color('white')
        button.label.set_fontweight('bold')

    # Coordinate lists
    x_coords = []
    y_coords = []

    # JSON file with saved curves
    saved_plots_file = base_path / "animation" / "saved_curves.json"

    # Creating a list of coordinate tuples [(x_coords1, y_coords1), (x_coords2, y_coords2),...]
    if saved_plots_file.exists():
        with open(saved_plots_file, "r") as file:
            already_drawn = json.load(file)
    else:
        already_drawn = []
    
    # Index of dragged point
    dragged_point_idx = None

    # To check, if the program was closed using End button (for finishing the animation or not)
    was_end_clicked = False

    # Index of the curve to be modified compared to the previous frame
    bezier_index = len(already_drawn)

    def redraw():
        """Refresh the plot and redraw everything from scratch"""  
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        ax.clear()

        ax.imshow(frames_in_memory[index], extent=[0, 1600, 0, 1000], cmap='gray', alpha=0.2)

        ax.set_title(
        "$\\mathbf{LPM}$ - add/move point,      "
        "$\\mathbf{PPM}$ - delete point,      "
        "$\\mathbf{Enter}$ - edit/save curve (required to save frame),      "
        "$\\mathbf{Backspace}$ - delete (last) curve,      "
        "$\\mathbf{←/→, ↑/↓}$ - change frame/curve\n",
        fontsize=11, loc='center'
        )
        ax.text(
            0.5, 1.08,
            "CREATING ANIMATION FRAMES WITH BÉZIER CURVES",
            transform=ax.transAxes,
            ha="center",
            fontsize=19, fontweight="bold",
            color="darkviolet"
        )
        ax.text(
            0.48, -0.08,
            f" {index+1} / {len(frames_in_memory)} ",
            transform=ax.transAxes,
            ha="center",
            fontsize=14, fontweight="bold",
            color="whitesmoke",
            bbox=dict(
                boxstyle='round,pad=0.7',
                facecolor='firebrick',
                edgecolor='black',
                linewidth=2
            )
        )

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
        if bezier_index == len(already_drawn):
            for x_todraw, y_todraw in already_drawn:
                drawing.draw_bezier(x_todraw, y_todraw, ax, 50, already_drawn=True)
        else:
            for i, (x_todraw, y_todraw) in enumerate(already_drawn):
                if i == bezier_index:
                    drawing.draw_bezier(x_todraw, y_todraw, ax, 50, already_drawn=True, draw_color="darkorange")
                else:
                    drawing.draw_bezier(x_todraw, y_todraw, ax, 50, already_drawn=True)

        # Draw curve: draw_bezier(...) z parametrem stałym (np. 100)
        if len(x_coords) == 1:
            ax.scatter(x_coords, y_coords, color="green", s=20)
        elif len(x_coords) > 1:
            drawing.draw_bezier(x_coords, y_coords, ax, 50)

        fig.canvas.draw_idle()

    redraw()

    # Function to search for the nearest point
    def get_nearest_point_idx(x_click, y_click, eps=12):
        """
        Returns the index of the nearest point to (x, y) if it is within eps pixels.
        Otherwise, returns None.
        """
        trans = ax.transData
        pts_screen = trans.transform(np.column_stack((x_coords, y_coords)))
        x_scr, y_scr = pts_screen[:, 0], pts_screen[:, 1]
        dist_sq = (x_scr - x_click)**2 + (y_scr - y_click)**2
        if len(dist_sq) == 0:
            return None
        min_idx = np.argmin(dist_sq)
        if dist_sq[min_idx] < eps**2:
            return min_idx
        return None

    def on_button_press(event):
        """
        Mouse click event handler.
        - Left click (event.button == 1): add or drag point.
        - Right click (event.button == 3): remove point.
        """
        nonlocal dragged_point_idx

        # Was click in the range of our plot?
        if event.inaxes != ax:
            return

        if event.button == 1:  # Left click
            idx = get_nearest_point_idx(event.x, event.y, eps=12)
            if idx is not None:
                # Beggining of dragging
                dragged_point_idx = idx
            else:
                # Add new point
                if event.xdata is not None and event.ydata is not None:
                    x_coords.append(event.xdata)
                    y_coords.append(event.ydata)
                    dragged_point_idx = len(x_coords) - 1
                    redraw()

        elif event.button == 3:  # Right click
            idx = get_nearest_point_idx(event.x, event.y, eps=12)
            if idx is not None: # Deletion
                x_coords.pop(idx)
                y_coords.pop(idx)
                redraw()

    def on_motion_notify(event):
        """Mouse drag handler for moving a point."""
        nonlocal dragged_point_idx
        if dragged_point_idx is None:
            return
        if event.inaxes != ax:
            return
        x_coords[dragged_point_idx] = event.xdata
        y_coords[dragged_point_idx] = event.ydata
        redraw()

    def on_button_release(event):
        """Mouse release handler - stop dragging."""
        nonlocal dragged_point_idx
        if event.button == 1 and dragged_point_idx is not None:
            dragged_point_idx = None

    def on_key_press(event):
        """Keyboard input handler."""
        nonlocal x_coords, y_coords, index, bezier_index
        if event.key == "shift":
            # Beer mug drawing (exactly 3 points chosen required)
            mug_draw()
            x_coords.clear()
            y_coords.clear()
            bezier_index = len(already_drawn)
            redraw()
        if event.key == 'enter':
            # Save the currently created curve, skip selection
            if len(x_coords) >= 2:
                # Save and clear the coordinate lists
                already_drawn.append((x_coords.copy(), y_coords.copy()))
                x_coords.clear()
                y_coords.clear()
                # Update selection index
                bezier_index = len(already_drawn)
                redraw()
            else:
                # Edit a previously drawn curve
                if bezier_index < len(already_drawn):
                    # Load the selected curve into editable points
                    x_coords, y_coords = already_drawn.pop(bezier_index)
                    # Update selection index
                    bezier_index = len(already_drawn)
                    redraw()

        if event.key == 'backspace':
            if already_drawn:
                if bezier_index == len(already_drawn):
                    already_drawn.pop()    # Remove the last added curve
                else:
                    already_drawn.pop(bezier_index)
                bezier_index = len(already_drawn)
                redraw()
        if event.key == 'left':
            if index > 0:
                index -= 1
                redraw()
        if event.key == 'right':
            if index < len(frames_in_memory) - 1:
                index += 1
                redraw()
        if event.key == 'down':
            if bezier_index < len(already_drawn):
                bezier_index += 1
                redraw()
        if event.key == 'up':
            if bezier_index > 0:
                bezier_index -= 1
                redraw()

    def mug_draw():
        # Helper function for automating the drawing of a beer mug
        pairs = list(zip(x_coords, y_coords))
        p_zero, p_up, p_right = pairs
        x_diff = [b - a for a, b in zip(p_zero, p_right)]
        y_diff = [b - a for a, b in zip(p_zero, p_up)]
        left_side = [[p_zero[0], p_zero[0]+0.1*x_diff[0]+0.3*y_diff[0], p_up[0]+0.05*x_diff[0]], [p_zero[1], p_zero[1]+0.1*x_diff[1]+0.3*y_diff[1], p_up[1]+0.05*x_diff[1]]]
        right_side = [[p_right[0], p_zero[0]+0.9*x_diff[0]+0.3*y_diff[0], p_up[0]+0.95*x_diff[0]],[p_right[1], p_zero[1]+0.9*x_diff[1]+0.3*y_diff[1], p_up[1]+0.95*x_diff[1]]]
        bottom_lower = [[p_zero[0], p_zero[0]+0.5*x_diff[0]-0.1*y_diff[0], p_right[0]], [p_zero[1], p_zero[1]+0.5*x_diff[1]-0.1*y_diff[1], p_right[1]]]
        bottom_upper = [[p_zero[0]+0.05*x_diff[0]+0.045*y_diff[0], p_zero[0]+0.5*x_diff[0]-0.02*y_diff[0], p_right[0]-0.05*x_diff[0]+0.045*y_diff[0]], [p_zero[1]+0.05*x_diff[1]+0.045*y_diff[1], p_zero[1]+0.5*x_diff[1]-0.02*y_diff[1], p_right[1]-0.05*x_diff[1]+0.045*y_diff[1]]]
        upper_side = [[p_up[0]+0.05*x_diff[0], p_up[0]+0.5*x_diff[0]-0.04*y_diff[0], p_up[0]+0.95*x_diff[0]], [p_up[1]+0.05*x_diff[1], p_up[1]+0.5*x_diff[1]-0.04*y_diff[1], p_up[1]+0.95*x_diff[1]]]
        middle_line = [[p_zero[0]+0.5*x_diff[0]+0.15*y_diff[0], p_zero[0]+0.5*x_diff[0]+0.65*y_diff[0]], [p_zero[1]+0.5*x_diff[1]+0.15*y_diff[1], p_zero[1]+0.5*x_diff[1]+0.65*y_diff[1]]]
        left_line = [[p_zero[0]+0.25*x_diff[0]+0.17*y_diff[0], p_zero[0]+0.33*x_diff[0]+0.4*y_diff[0], p_zero[0]+0.25*x_diff[0]+0.63*y_diff[0]], [p_zero[1]+0.25*x_diff[1]+0.17*y_diff[1], p_zero[1]+0.33*x_diff[1]+0.4*y_diff[1], p_zero[1]+0.25*x_diff[1]+0.63*y_diff[1]]]
        right_line = [[p_zero[0]+0.75*x_diff[0]+0.17*y_diff[0], p_zero[0]+0.67*x_diff[0]+0.4*y_diff[0], p_zero[0]+0.75*x_diff[0]+0.63*y_diff[0]], [p_zero[1]+0.75*x_diff[1]+0.17*y_diff[1], p_zero[1]+0.67*x_diff[1]+0.4*y_diff[1], p_zero[1]+0.75*x_diff[1]+0.63*y_diff[1]]]
        already_drawn.append(left_side)
        already_drawn.append(right_side)
        already_drawn.append(bottom_lower)
        already_drawn.append(bottom_upper)
        already_drawn.append(upper_side)
        already_drawn.append(middle_line)
        already_drawn.append(left_line)
        already_drawn.append(right_line)

    def on_button_click_save(event):
        """Handle Save button click."""
        nonlocal index, ax_save, ax_end

        # # Only save if there are no unfinished curves
        if len(x_coords) > 0:
            return

        index += 1
        saved_frame_name = f"frame{index}.png"
        saved_frame_path = base_path / "animation" / saved_frame_name

        # Prepare a clean plot for saving
        ax_save.set_visible(False)
        ax_end.set_visible(False)
        ax.clear()
        ax.imshow(blank, extent=[0, 1600, 0, 1000])
        for x_todraw, y_todraw in already_drawn:
            drawing.draw_bezier(x_todraw, y_todraw, ax, 200, True)
        ax.axis("off")
        
        # Save frame to file
        fig.savefig(saved_frame_path, dpi=72, bbox_inches="tight", pad_inches=0)

        # Save to memory buffer (PNG), and then to frames_in_memory as np.ndarray
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=72, bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        # Loading from buffer to np.ndarray
        np_img = mpimg.imread(buf)
        # Add to the list of frames in memory
        if index < len(frames_in_memory):
            frames_in_memory[index] = np_img  # Overwriting the existing one
        else:
            frames_in_memory.append(np_img)

        # Restore UI
        ax_save.set_visible(True)
        ax_end.set_visible(True)
        redraw()
        
    def on_button_click_end(event):
        """Handle End button click."""
        nonlocal was_end_clicked
        # User wants to see the animation
        was_end_clicked = True
        plt.close(fig)

    cid_press     = fig.canvas.mpl_connect('button_press_event',   on_button_press)
    cid_motion    = fig.canvas.mpl_connect('motion_notify_event',  on_motion_notify)
    cid_release   = fig.canvas.mpl_connect('button_release_event', on_button_release)
    cid_key_press = fig.canvas.mpl_connect('key_press_event',      on_key_press)

    button_save.on_clicked(on_button_click_save)
    button_end.on_clicked(on_button_click_end)

    plt.show()

    fig.canvas.mpl_disconnect(cid_press)
    fig.canvas.mpl_disconnect(cid_motion)
    fig.canvas.mpl_disconnect(cid_release)
    fig.canvas.mpl_disconnect(cid_key_press)

    # Save drawn curves to JSON file so they can be reloaded later
    with open(saved_plots_file, 'w') as file:
        json.dump(already_drawn, file)

    return was_end_clicked