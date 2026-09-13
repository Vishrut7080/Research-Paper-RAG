import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models import Base, engine


def main():
    Base.metadata.create_all(engine)
    print(f"Database initialized: {engine.url}")


if __name__ == "__main__":
    main()