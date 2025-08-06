import ipaddress
from typing import Optional
import re


def reverse_ip_address(ip_str: str) -> str:
    """
    Reverse an IP address (IPv4 or IPv6).
    For IPv4, returns the dot-reversed address (useful for PTR lookups).
    For IPv6, returns the nibble-reversed address (useful for PTR lookups).
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.version == 4:
            parts = str(ip).split(".")
            return ".".join(reversed(parts))
        else:
            # Expand IPv6, remove colons, then reverse nibbles for PTR format
            expanded = ip.exploded.replace(":", "")
            return ".".join(reversed(list(expanded)))
    except ValueError as e:
        raise ValueError(f"Invalid IP address: {ip_str}") from e


def is_valid_ip(ip_str: str) -> bool:
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def get_client_ip(request) -> str:
    """
    Extract the real client IP address from the request (FastAPI style).
    Validates all candidates and extracts the first valid one.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
        if is_valid_ip(ip):
            return ip
    real_ip = request.headers.get("X-Real-IP")
    if real_ip and is_valid_ip(real_ip):
        return real_ip
    client_ip = request.headers.get("X-Client-IP")
    if client_ip and is_valid_ip(client_ip):
        return client_ip
    if (
        hasattr(request, "client")
        and request.client
        and is_valid_ip(request.client.host)
    ):
        return request.client.host
    return "127.0.0.1"


def format_ip_display(ip_str: str) -> dict:
    try:
        ip = ipaddress.ip_address(ip_str)
        reversed_ip = reverse_ip_address(ip_str)
        return {
            "original_ip": str(ip),
            "reversed_ip": reversed_ip,
            "version": f"IPv{ip.version}",
            "is_private": ip.is_private,
            "is_loopback": ip.is_loopback,
            "is_multicast": ip.is_multicast,
            "is_reserved": ip.is_reserved,
            "is_global": ip.is_global,
        }
    except ValueError:
        return {
            "error": f"Invalid IP address: {ip_str}",
            "original_ip": ip_str,
            "reversed_ip": None,
        }
