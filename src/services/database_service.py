"""
Supabase Database Service
Handles all database operations for transaction logging and history
"""
import os
import logging
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service class for Supabase database operations."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize Supabase client.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon/public API key
        """
        try:
            self.client: Client = create_client(supabase_url, supabase_key)
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    def log_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Log a transaction to the database.
        
        Args:
            transaction_data: Dictionary containing all transaction fields
            
        Returns:
            Inserted record data or None if failed
        """
        try:
            # Insert transaction
            response = self.client.table('transactions').insert(transaction_data).execute()
            
            if response.data:
                transaction_id = response.data[0]['id']
                logger.info(f"✅ Transaction logged: {transaction_id}")
                return response.data[0]
            else:
                logger.warning("⚠️ Transaction insert returned no data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to log transaction: {e}")
            return None
    
    def log_flagged_transaction(
        self, 
        transaction_id: str, 
        risk_level: str = "HIGH"
    ) -> Optional[Dict]:
        """
        Log a flagged transaction (BLOCK or REVIEW decisions).
        
        Args:
            transaction_id: UUID of the transaction
            risk_level: Risk level ('HIGH' or 'CRITICAL')
            
        Returns:
            Inserted flagged transaction record or None if failed
        """
        try:
            flagged_data = {
                'transaction_id': transaction_id,
                'risk_level': risk_level,
                'reviewed': False
            }
            
            response = self.client.table('flagged_transactions').insert(flagged_data).execute()
            
            if response.data:
                logger.info(f"🚩 Flagged transaction: {transaction_id} as {risk_level}")
                return response.data[0]
            else:
                logger.warning("⚠️ Flagged transaction insert returned no data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to log flagged transaction: {e}")
            return None
    
    def get_recent_transactions(self, limit: int = 20) -> List[Dict]:
        """
        Get recent transactions from the database.
        
        Args:
            limit: Maximum number of transactions to retrieve
            
        Returns:
            List of transaction records
        """
        try:
            response = self.client.table('transactions')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent transactions: {e}")
            return []
    
    def get_fraud_statistics(self) -> Dict[str, Any]:
        """
        Get fraud statistics from the database.
        
        Returns:
            Dictionary containing fraud statistics
        """
        try:
            # Use the fraud_statistics view we created
            response = self.client.table('fraud_statistics').select('*').execute()
            
            if response.data and len(response.data) > 0:
                stats = response.data[0]
                return {
                    'total_transactions': stats.get('total_transactions', 0),
                    'fraud_count': stats.get('fraud_count', 0),
                    'fraud_rate_percent': float(stats.get('fraud_rate_percent', 0.0)),
                    'allowed_count': stats.get('allowed_count', 0),
                    'review_count': stats.get('review_count', 0),
                    'blocked_count': stats.get('blocked_count', 0)
                }
            else:
                # Return zero stats if no data
                return {
                    'total_transactions': 0,
                    'fraud_count': 0,
                    'fraud_rate_percent': 0.0,
                    'allowed_count': 0,
                    'review_count': 0,
                    'blocked_count': 0
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get fraud statistics: {e}")
            # Return zero stats on error
            return {
                'total_transactions': 0,
                'fraud_count': 0,
                'fraud_rate_percent': 0.0,
                'allowed_count': 0,
                'review_count': 0,
                'blocked_count': 0
            }
    
    def get_flagged_transactions(self, limit: int = 50) -> List[Dict]:
        """
        Get recent flagged transactions.
        
        Args:
            limit: Maximum number of flagged transactions to retrieve
            
        Returns:
            List of flagged transaction records
        """
        try:
            response = self.client.table('recent_flagged_transactions')\
                .select('*')\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"❌ Failed to get flagged transactions: {e}")
            return []
    
    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            # Try a simple query
            response = self.client.table('transactions').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return False
