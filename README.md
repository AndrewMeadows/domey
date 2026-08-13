# Domey

A Python application for visualizing spherical geodesics based on the five regular
polyhedra and the rhombic dodecahedron, with subdivision orders 1-3.
<img width="1193" height="760" alt="domey-20260601-001" src="https://github.com/user-attachments/assets/2d62d829-533b-4882-b691-3e1e51f7da29" />

## Installation

Requires Python 3.8+. Use a python virtual environment (venv) and install this package along with the `app` extra,
which pulls in the viewer's OpenGL dependencies (ModernGL, moderngl-window, imgui-bundle):

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[app]"
```
## Running the viewer

Once installed, and while using the venv, launch the viewer with the `domey` command:

```bash
domey
```

Alternatively, run the module directly:

```bash
python -m app
```
