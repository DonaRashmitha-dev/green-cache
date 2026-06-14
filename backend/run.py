import sys
from pathlib import Path

# Add src to Python path so imports work
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import create_app
import uvicorn
from config import settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
