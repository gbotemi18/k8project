import ipaddress
from typing import Optional
import re


def reverse_ip_address(ip_str: str) -> str:
    """
    Reverse an IP address.
    
    Args:
        ip_str: IP address string (IPv4 or IPv6)
    
    Returns:
        Reversed IP address string
    
    Examples:
        >>> reverse_ip_address("1.2.3.4")
        "4.3.2.1"
        >>> reverse_ip_address("2001:db8::1")
        "1::8bd:1002"
    """
    try:
        # Parse the IP address
        ip = ipaddress.ip_address(ip_str)
        
        if ip.version == 4:
            # For IPv4, split by dots and reverse
            parts = str(ip).split('.')
            return '.'.join(reversed(parts))
        else:
            # For IPv6, convert to expanded form and reverse
            expanded = ip.exploded
            # Remove colons and reverse
            hex_parts = expanded.replace(':', '')
            reversed_hex = ''.join(reversed(hex_parts))
            # Re-add colons every 4 characters
            reversed_ipv6 = ':'.join([reversed_hex[i:i+4] for i in range(0, len(reversed_hex), 4)])
            return reversed_ipv6
            
    except ValueError as e:
        raise ValueError(f"Invalid IP address: {ip_str}") from e


def is_valid_ip(ip_str: str) -> bool:
    """
    Check if a string is a valid IP address.
    
    Args:
        ip_str: String to validate
    
    Returns:
        True if valid IP address, False otherwise
    """
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def get_client_ip(request) -> str:
    """
    Extract the real client IP address from the request.
    Handles various proxy headers and forwarded IPs.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Client IP address string
    """
    # Check for forwarded headers (common in proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the list
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Check for client IP header
    client_ip = request.headers.get("X-Client-IP")
    if client_ip:
        return client_ip
    
    # Fallback to direct connection IP
    if hasattr(request, 'client') and request.client:
        return request.client.host
    
    # Last resort
    return "127.0.0.1"


def format_ip_display(ip_str: str) -> dict:
    """
    Format IP address information for display.
    
    Args:
        ip_str: IP address string
    
    Returns:
        Dictionary with formatted IP information
    """
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
            "is_global": ip.is_global
        }
    except ValueError as e:
        return {
            "error": f"Invalid IP address: {ip_str}",
            "original_ip": ip_str,
            "reversed_ip": None
        } 