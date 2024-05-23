# Mandelbrot Set Visualization

This project visualizes the Mandelbrot Set using OpenGL and GLFW. It includes functionalities for smooth zooming and panning, allowing you to explore the intricate details of the Mandelbrot Set interactively.

## Features

- **Smooth Zooming**: Use the mouse scroll wheel to zoom in and out smoothly.
- **Drag-and-Drop Panning**: Click and hold the left mouse button to drag and move the view around.
- **High-Resolution Rendering**: Dynamically adjusts the resolution based on the zoom level to ensure high-quality rendering.

## Requirements

- Python 3.x
- OpenGL
- GLFW
- NumPy

You can install the required packages using pip:

```sh
pip install glfw PyOpenGL numpy

**Authors:**

* ulisses177

**Version History:**

* 1.0: Initial release
* 1.1: Added FFmpeg support for combining frames into a single 
video file
* 2.0: Changed it to use openGL shaders and use the cursor to navegate the set.
