import math
import glm

from .state import CameraState


def view_proj(cam: CameraState, aspect: float) -> glm.mat4:
    cp = math.cos(cam.pitch)
    eye = glm.vec3(
        cam.distance * cp * math.sin(cam.yaw),
        cam.distance * math.sin(cam.pitch),
        cam.distance * cp * math.cos(cam.yaw),
    )
    view = glm.lookAt(eye, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
    proj = glm.perspective(glm.radians(45.0), aspect, 0.01, 100.0)
    return proj * view


def orbit(cam: CameraState, dx: float, dy: float) -> None:
    cam.yaw -= dx * 0.005
    cam.pitch += dy * 0.005
    limit = math.pi / 2 - 0.01
    cam.pitch = max(-limit, min(limit, cam.pitch))


def zoom(cam: CameraState, delta: float) -> None:
    cam.distance *= math.exp(-delta * 0.1)
    cam.distance = max(0.5, min(50.0, cam.distance))
