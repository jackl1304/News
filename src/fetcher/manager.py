# src/fetcher/manager.py

import os
import importlib
from typing import List
from .base import SourcePlugin

def load_plugins() -> List[SourcePlugin]:
    """
    Liest die Umgebungsvariable SOURCE_SPECS ein und instanziiert Plugins.
    Format: module_path|ClassName|arg1|arg2;module2|Class2|arg1;…
    """
    specs = os.getenv("SOURCE_SPECS", "").split(";")
    plugins: List[SourcePlugin] = []

    for spec in specs:
        if not spec:
            continue
        parts = spec.split("|")
        module_path, class_name, *args = parts
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        plugins.append(cls(*args))

    return plugins
