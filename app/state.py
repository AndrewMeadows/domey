from dataclasses import dataclass, field, replace

SHAPES = (
    "tetrahedron",
    "hexahedron",
    "octahedron",
    "dodecahedron",
    "icosahedron",
)


@dataclass(frozen=True)
class GeometryInputs:
    shape_name: str = "icosahedron"
    twist_angle: float = 0.6534


@dataclass
class DisplayFlags:
    show_base_polyhedron: bool = True
    show_arcs: bool = True
    show_intersections: bool = True
    show_faces: bool = False
    wireframe: bool = True


@dataclass
class CameraState:
    yaw: float = 0.6
    pitch: float = 0.4
    distance: float = 3.5


@dataclass
class AppState:
    geometry: GeometryInputs = field(default_factory=GeometryInputs)
    display: DisplayFlags = field(default_factory=DisplayFlags)
    camera: CameraState = field(default_factory=CameraState)

    def set_geometry(self, **kwargs) -> None:
        self.geometry = replace(self.geometry, **kwargs)
