from __future__ import annotations

from pathlib import Path

import trimesh


def load_and_repair_mesh(input_path: str | Path, simplify_target: int = 50000) -> trimesh.Trimesh:
    """Load a source mesh and run Pluto3D's print repair pipeline."""
    mesh = trimesh.load(str(input_path), force="mesh")

    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

    mesh.fill_holes()
    mesh.remove_degenerate_faces()
    mesh.remove_unreferenced_vertices()
    mesh.remove_duplicate_faces()
    mesh.merge_vertices()

    if simplify_target:
        try:
            mesh = mesh.simplify_quadratic_decimation(simplify_target)
        except Exception:
            pass

    return mesh
