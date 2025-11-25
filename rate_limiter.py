"""
Rate Limiter for Public Access

Limits queries per session/IP to prevent API cost abuse.
Admin users can bypass limits with password.
"""

import streamlit as st
from datetime import datetime, timedelta
import hashlib


class RateLimiter:
    """
    Simple rate limiter using Streamlit session state.
    
    Tracks queries per session and enforces limits.
    """
    
    def __init__(self, max_queries: int = 5, max_input_length: int = 500):
        """
        Initialize rate limiter.
        
        Args:
            max_queries: Maximum queries allowed per session
            max_input_length: Maximum characters in a query
        """
        self.max_queries = max_queries
        self.max_input_length = max_input_length
        
        # Initialize session state
        if 'query_count' not in st.session_state:
            st.session_state.query_count = 0
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
    
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        return st.session_state.get('is_admin', False)
    
    def check_admin_password(self, password: str, correct_hash: str) -> bool:
        """
        Verify admin password.
        
        Args:
            password: User-provided password
            correct_hash: SHA256 hash of correct password
        
        Returns:
            True if password is correct
        """
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == correct_hash
    
    def grant_admin_access(self):
        """Grant admin access to current session."""
        st.session_state.is_admin = True
        st.session_state.query_count = 0  # Reset count for admin
    
    def can_query(self) -> tuple[bool, str]:
        """
        Check if user can make another query.
        
        Returns:
            (allowed, reason) tuple
        """
        # Admin bypass
        if self.is_admin():
            return True, "Admin access - unlimited queries"
        
        # Check query limit
        if st.session_state.query_count >= self.max_queries:
            return False, f"Query limit reached ({self.max_queries} queries per session)"
        
        return True, f"Queries remaining: {self.max_queries - st.session_state.query_count}"
    
    def check_input_length(self, query: str) -> tuple[bool, str]:
        """
        Check if query is within length limit.
        
        Returns:
            (valid, message) tuple
        """
        if len(query) > self.max_input_length:
            return False, f"Query too long ({len(query)} characters, max {self.max_input_length})"
        return True, f"Query length: {len(query)}/{self.max_input_length} characters"
    
    def increment_count(self):
        """Increment query count."""
        if not self.is_admin():
            st.session_state.query_count += 1
    
    def get_remaining_queries(self) -> int:
        """Get number of queries remaining."""
        if self.is_admin():
            return float('inf')
        return max(0, self.max_queries - st.session_state.query_count)
    
    def reset_session(self):
        """Reset session counts (for admin use)."""
        st.session_state.query_count = 0
        st.session_state.session_start = datetime.now()


def render_admin_panel(rate_limiter: RateLimiter, admin_password_hash: str):
    """
    Render admin login panel in sidebar.
    
    Args:
        rate_limiter: RateLimiter instance
        admin_password_hash: SHA256 hash of admin password
    """
    st.sidebar.markdown("---")
    
    if rate_limiter.is_admin():
        st.sidebar.success("🔓 Admin Mode Active")
        st.sidebar.caption("Unlimited queries enabled")
        
        if st.sidebar.button("Reset Session"):
            rate_limiter.reset_session()
            st.rerun()
    else:
        with st.sidebar.expander("🔐 Admin Access"):
            st.caption("Enter admin password for unlimited queries")
            password = st.text_input("Password", type="password", key="admin_password")
            
            if st.button("Login"):
                if rate_limiter.check_admin_password(password, admin_password_hash):
                    rate_limiter.grant_admin_access()
                    st.success("Admin access granted!")
                    st.rerun()
                else:
                    st.error("Incorrect password")


def render_rate_limit_info(rate_limiter: RateLimiter):
    """
    Show rate limit status to user.
    
    Args:
        rate_limiter: RateLimiter instance
    """
    if rate_limiter.is_admin():
        return  # Don't show limits to admin
    
    remaining = rate_limiter.get_remaining_queries()
    
    if remaining > 0:
        st.info(f"ℹ️ Queries remaining this session: **{remaining}/{rate_limiter.max_queries}**")
    else:
        st.error(f"🚫 Query limit reached. You've used all {rate_limiter.max_queries} queries for this session.")
        st.caption("Refresh the page to start a new session, or contact the admin for more access.")


if __name__ == "__main__":
    # Generate password hash for setup
    import sys
    
    if len(sys.argv) > 1:
        password = sys.argv[1]
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"\nPassword: {password}")
        print(f"Hash: {password_hash}")
        print(f"\nAdd this to your Streamlit secrets:")
        print(f'ADMIN_PASSWORD_HASH = "{password_hash}"')
    else:
        print("Usage: python rate_limiter.py YOUR_PASSWORD")
        print("This will generate a hash to put in Streamlit secrets")