"""
Launcher script for ingestion pipeline.
Handles Python path setup automatically.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now run the pipeline
from src.ingestion.pipeline import main

if __name__ == "__main__":
    main()
