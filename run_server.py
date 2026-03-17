"""Start the IBC ARMA 3 Mission Generator web server."""
import uvicorn
from web.app import app

if __name__ == "__main__":
    print("=" * 50)
    print("  IBC ARMA 3 Mission Generator")
    print("  http://127.0.0.1:8000")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)
