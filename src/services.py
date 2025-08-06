from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import logging

from src.database import IPAddress
from src.utils import reverse_ip_address, format_ip_display, get_client_ip
from src.models import IPAddressHistory

logger = logging.getLogger(__name__)


class IPAddressService:
    """Service class for IP address operations"""

    @staticmethod
    def process_ip_request(
        db: Session, client_ip: str, user_agent: Optional[str] = None
    ) -> dict:
        """
        Process an IP address request and store it in the database.

        Args:
            db: Database session
            client_ip: Client IP address
            user_agent: User agent string (optional)

        Returns:
            Dictionary with IP information
        """
        try:
            # Reverse the IP address
            reversed_ip = reverse_ip_address(client_ip)

            # Format the response
            ip_info = format_ip_display(client_ip)
            ip_info["timestamp"] = datetime.utcnow()
            ip_info["user_agent"] = user_agent

            # Store in database
            db_record = IPAddress(
                original_ip=client_ip, reversed_ip=reversed_ip, user_agent=user_agent
            )

            db.add(db_record)
            db.commit()
            db.refresh(db_record)

            logger.info(f"Stored IP address: {client_ip} -> {reversed_ip}")

            return ip_info

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing IP request: {e}")
            raise

    @staticmethod
    def get_ip_history(db: Session, limit: int = 50, offset: int = 0) -> dict:
        """
        Get IP address history from the database.

        Args:
            db: Database session
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            Dictionary with history data
        """
        try:
            # Get total count
            total_count = db.query(IPAddress).count()

            # Get records with pagination
            records = (
                db.query(IPAddress)
                .order_by(desc(IPAddress.timestamp))
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Convert to response models
            history_records = []
            for record in records:
                history_records.append(
                    IPAddressHistory(
                        id=record.id,
                        original_ip=record.original_ip,
                        reversed_ip=record.reversed_ip,
                        user_agent=record.user_agent,
                        timestamp=record.timestamp,
                    )
                )

            return {"total_count": total_count, "records": history_records}

        except Exception as e:
            logger.error(f"Error retrieving IP history: {e}")
            raise

    @staticmethod
    def get_statistics(db: Session) -> dict:
        """
        Get IP address statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with statistics
        """
        try:
            total_requests = db.query(IPAddress).count()

            # Get unique IPs
            unique_ips = db.query(IPAddress.original_ip).distinct().count()

            # Get most recent request
            latest_request = (
                db.query(IPAddress).order_by(desc(IPAddress.timestamp)).first()
            )

            # Get requests in last 24 hours
            from datetime import timedelta

            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_requests = (
                db.query(IPAddress).filter(IPAddress.timestamp >= yesterday).count()
            )

            return {
                "total_requests": total_requests,
                "unique_ips": unique_ips,
                "recent_requests_24h": recent_requests,
                "latest_request": latest_request.timestamp if latest_request else None,
            }

        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}")
            raise

    @staticmethod
    def check_database_health(db: Session) -> str:
        """
        Check database connection health.

        Args:
            db: Database session

        Returns:
            Health status string
        """
        try:
            # Simple query to test connection
            db.execute("SELECT 1")
            return "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return "unhealthy"
