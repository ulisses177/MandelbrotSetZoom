import numpy as np
import matplotlib.pyplot as plt
import os

def mandelbrot(c, max_iter):
    z = 0
    n = 0
    while abs(z) <= 2 and n < max_iter:
        z = z*z + c
        n += 1
    return n

def mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter):
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.empty((width, height))
    for i in range(width):
        for j in range(height):
            n3[i, j] = mandelbrot(r1[i] + 1j * r2[j], max_iter)
    return (r1, r2, n3)


def plot_mandelbrot(xmin, xmax, ymin, ymax, width=1920, height=1080, max_iter=512, cmap='hot', filename=None):
    dpi = 1000
    img_width = width / dpi
    img_height = height / dpi

    fig, ax = plt.subplots(figsize=(img_width, img_height), dpi=dpi)
    ax.imshow(mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter)[2].T, extent=[xmin, xmax, ymin, ymax], cmap=cmap)
    ax.axis('off')  # Turn off the axis

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove white space
    if filename:
        plt.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()

# Create a directory to save the frames
output_dir = 'mandelbrot_frames'
os.makedirs(output_dir, exist_ok=True)

# Parameters for the zoom animation
xmin, xmax = -2.0, 1.0
ymin, ymax = -1.5, 1.5
zoom_factor = 1.05
num_frames = 1600
x_center, y_center = -0.5693038674840807, -0.5724608139558649

# Generate the frames
for i in range(num_frames):
    range_x = (xmax - xmin) / (zoom_factor ** i)
    range_y = (ymax - ymin) / (zoom_factor ** i)
    xmin_frame = x_center - range_x / 2
    xmax_frame = x_center + range_x / 2
    ymin_frame = y_center - range_y / 2
    ymax_frame = y_center + range_y / 2



    filename = os.path.join(output_dir, f"frame_{i:04d}.png")
    plot_mandelbrot(xmin_frame, xmax_frame, ymin_frame, ymax_frame, filename=filename)

# Combine the frames into a video using ffmpeg
os.system(f"ffmpeg -framerate 24 -i {output_dir}/frame_%04d.png -c:v libx264 -pix_fmt yuv420p mandelbrot_zoom.mkv")