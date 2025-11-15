import uvicorn
from sentinel.config import settings


def main() -> None:
    uvicorn.run(
        "sentinel.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
