import sys
from pathlib import Path

from src.app.module import err, func

sys.path.append(str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    print(func())
    try:
        print(err())
    except RuntimeError as e:
        print(f"Caught an error: {e}")
