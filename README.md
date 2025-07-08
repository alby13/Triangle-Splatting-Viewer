# Triangle Splatting Viewer / Engine / Browser

A real-time 3D rendering engine built with Python, Pygame, and OpenGL to navigate Triangle Splatting assets in the `.off` file format. The engine features a loading progress bar and supports interactive camera navigation for exploring 3D meshes, with a pre-configured orientation for the `garden.off` mesh.

## Features
- **Real-Time Rendering**: Renders triangle-based meshes using OpenGL with vertex and fragment shaders.
- **Custom .off Parser**: Loads `.off` files with vertex positions and RGB colors, supporting large meshes efficiently.
- **Loading Screen**: Displays a progress bar during mesh loading for better user experience.
- **Camera Controls**: Smooth first-person camera navigation with mouse look and keyboard movement.
- **Optimized Orientation**: Fixed world orientation for the `garden.off` mesh (pitch=151.20°, yaw=-2.70°, roll=-1.35°).

## Controls
- **W, A, S, D**: Move camera forward, left, backward, right.
- **Mouse**: Look around (mouse cursor is locked to the window).
- **Space**: Move camera up.
- **Left Ctrl / Left Shift**: Move camera down.
- **Escape**: Exit the application.

## Requirements
- Python 3.8+
- Pygame
- PyOpenGL
- PyGLM
- NumPy
- A `.off` mesh file (e.g., `garden.off`)

## The .off Mesh Files
Garden and Room triangle splatting 3D mesh files can be downloaded at the project website: https://trianglesplatting.github.io/ 

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/triangle-splatting-viewer.git
   cd triangle-splatting-viewer

   Install dependencies:

pip install pygame PyOpenGL PyGLM numpy


Ensure the garden.off mesh file is in the project directory. (Replace with your own .off file if needed.)

## Usage

### Run the engine:

```
python engine.py
```

The loading screen will display while garden.off loads.

Once loaded, navigate the 3D mesh using the controls listed above.


## Project Structure

- engine.py: Main script containing the rendering engine, shaders, and .off parser.

- garden.off: Example mesh file (not included; available on Triangle Splatting Website).

- LICENSE: Copyright notice for this project.

## Notes

The engine is optimized for the garden.off mesh with a specific orientation. To use other .off files, you may need to adjust the model matrix in engine.py or preprocess the mesh.

## Third-Party Licenses

This project uses the following third-party libraries, each with its own license:


- Pygame: Licensed under the GNU Lesser General Public License v2.1 (LGPLv2.1). Copyright © 2000-2025 Pygame Developers.

- PyOpenGL: Licensed under the BSD 3-Clause License. Copyright © 1997-2007 Mike C. Fletcher and contributors.

- PyGLM: Licensed under the MIT License. Copyright © 2017-2025 Zuzu-Typ.

- NumPy: Licensed under the BSD 3-Clause License. Copyright © 2005-2025 NumPy Developers.

The full license texts for these libraries can be found in their respective repositories or documentation.

## License

This project is proprietary software under full copyright. All rights are reserved. See the LICENSE file for details. For permissions to use, copy, modify, or distribute this software, contact the project owner.


Acknowledgments

Built with Pygame, PyOpenGL, and PyGLM.

Inspired by triangle splatting project: https://github.com/trianglesplatting/triangle-splatting
