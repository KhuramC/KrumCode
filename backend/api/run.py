import uvicorn
from utils.config_loader import get_config


def start_server() -> None:
    """A function that Poetry can call to run the server based on the configurations."""
    try:
        config = get_config()
        serv_config = config.Server
    except (FileNotFoundError, ValueError):
        print("Config file not found or empty. Exiting...")
        exit(1)

    uvicorn.run(
        "api.main:app",
        host=str(serv_config.host),
        port=serv_config.port,
        reload=serv_config.development,
    )


if __name__ == "__main__":
    start_server()
