from dataclasses import dataclass, field, replace

SHAPES = (
    "tetrahedron",
    "hexahedron",
    "octahedron",
    "dodecahedron",
    "icosahedron",
    "rhombic_dodecahedron",
)

ORDERS = (1, 2, 3)


@dataclass(frozen=True)
class GeometryInputs:
    shape_name: str = "icosahedron"
    twist_angle: float = 0.0
    order: int = 1


@dataclass
class ObjectDisplay:
    """Per-object visibility: the object itself plus each element type."""
    enabled: bool = True
    show_vertices: bool = True
    show_edges: bool = True
    show_faces: bool = True


@dataclass
class DisplayFlags:
    polyhedron: ObjectDisplay = field(
        default_factory=lambda: ObjectDisplay(enabled=False)
    )
    geodesic: ObjectDisplay = field(default_factory=ObjectDisplay)


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
