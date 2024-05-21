# MandelbrotSetZoom
A Python script that generates a zoom animation of the Mandelbrot  set, a famous fractal in mathematics. The animation creates a  series of PNG frames, each showing a different portion of the  Mandelbrot set at increasingly higher magnification.
* Generates Mandelbrot sets using the `mandelbrot` function
* Creates a 2D array representing the Mandelbrot set using the 
`mandelbrot_set` function
* Plots the Mandelbrot set as an image using Matplotlib's `imshow`
function
* Saves frames to PNG files for animation creation
* Combines frames into a single video file using FFmpeg

**Usage:**

1. Clone this repository to your local machine
2. Run the script using Python (e.g., `python mandelbrot.py`)
3. Adjust parameters in the script as needed (e.g., zoom factor, 
number of frames)
4. View the resulting animation in a video player or image viewer

**License:**

This software is released under the MIT License.

**Authors:**

* ulisses177

**Version History:**

* 1.0: Initial release
* 1.1: Added FFmpeg support for combining frames into a single 
video file
