#!/usr/bin/env python3
"""
Supabase client for the AI Hub Content Creation System.

This module provides functions to interact with Supabase for content inventory,
prompt logging, and generation outputs.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
