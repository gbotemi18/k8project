from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class IPAddressResponse(BaseModel):
    """Response model for IP address information"""

    original_ip: str = Field(..., description="Original IP address")
    reversed_ip: str = Field(..., description="Reversed IP address")
    version: str = Field(..., description="IP version (IPv4 or IPv6)")
    is_private: bool = Field(..., description="Whether IP is private")
    is_loopback: bool = Field(..., description="Whether IP is loopback")
    is_multicast: bool = Field(..., description="Whether IP is multicast")
    is_reserved: bool = Field(..., description="Whether IP is reserved")
    is_global: bool = Field(..., description="Whether IP is global")
    timestamp: datetime = Field(..., description="Request timestamp")
    user_agent: Optional[str] = Field(None, description="User agent string")


class IPAddressHistory(BaseModel):
    """Model for IP address history entry"""

    id: int = Field(..., description="Database record ID")
    original_ip: str = Field(..., description="Original IP address")
    reversed_ip: str = Field(..., description="Reversed IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    timestamp: datetime = Field(..., description="Record timestamp")


class IPAddressHistoryResponse(BaseModel):
    """Response model for IP address history"""

    total_count: int = Field(..., description="Total number of records")
    records: List[IPAddressHistory] = Field(
        ..., description="List of IP address records"
    )


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(..., description="Error timestamp")


class HealthCheckResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    database_status: str = Field(..., description="Database connection status")
