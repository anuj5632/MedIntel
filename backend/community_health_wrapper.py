"""
Wrapper to import Community Health Agent with proper path setup
"""
import sys
import os

# Add the community health agent directory to path
community_health_dir = r"C:\nextycce\MEDINTEL\Agents\community_health_agent"
if community_health_dir not in sys.path:
    sys.path.insert(0, community_health_dir)

# Now we can import the module normally
from community_agent import CommunityHealthAgent

__all__ = ['CommunityHealthAgent']
