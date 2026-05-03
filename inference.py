import sys
import subprocess
from pathlib import Path

def main():
    # Forward the execution to the actual inference.py inside the backend directory
    # This allows users to run 'python inference.py' from the root folder seamlessly.
    backend_script = Path(__file__).resolve().parent / "backend" / "inference.py"
    
    cmd = [sys.executable, str(backend_script)] + sys.argv[1:]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
