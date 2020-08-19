import socket


# based on https://stackoverflow.com/a/33117579/3315770
def internet_available(host: str = "8.8.8.8", port: int = 53, timeout: float = 3) -> bool:
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def await_internet() -> None:
    available: bool = False
    while not available:
        available = available or internet_available()
    print("Internet is available.")
