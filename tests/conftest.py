
import sys
from unittest.mock import MagicMock

# Mock modules that might cause import errors in CI
module_names = [
    "google.cloud",
    "google.cloud.firestore",
    "google.cloud.storage",
    "google.cloud.aiplatform",
    "google.generativeai",
    "google.genai",
    "google.genai.types",
    "vertexai",
    "vertexai.generative_models",
    "winsound",
    "flet",
]

for module_name in module_names:
    sys.modules[module_name] = MagicMock()

# Specifically for vertexai.generative_models.Part (used in Owl/Voidoll)
sys.modules["vertexai.generative_models"].Part = MagicMock()
sys.modules["vertexai.generative_models"].GenerativeModel = MagicMock()
