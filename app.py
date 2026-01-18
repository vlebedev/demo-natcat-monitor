"""Entry point for NatCat Event Monitor Streamlit app."""

import sys
from pathlib import Path

# Add project root to path so imports work
sys.path.insert(0, str(Path(__file__).parent))

from src.app import main

if __name__ == "__main__":
    main()
