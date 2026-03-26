from __future__ import annotations

from pathlib import Path

import trimesh


def load_and_repair_mesh(input_path: str | Path, simplify_target: int = 50000) -> trimesh.Trimesh:
    """Load a source mesh and run Pluto3D's print repair pipeline."""
    mesh = trimesh.load(str(input_path), force="mesh")

    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

    mesh.fill_holes()

    try:
        mesh.update_faces(mesh.nondegenerate_faces())
    except Exception:
        pass

    try:
        mesh.update_faces(mesh.unique_faces())
    except Exception:
        pass

    mesh.remove_unreferenced_vertices()
    mesh.merge_vertices()

    if simplify_target and len(mesh.faces) > simplify_target:
        try:
            mesh = mesh.simplify_quadric_decimation(simplify_target)
        except Exception:
            pass

    return mesh
