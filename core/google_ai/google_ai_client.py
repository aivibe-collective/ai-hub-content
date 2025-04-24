#!/usr/bin/env python3
"""
Google Generative AI client for the AI Hub Content Creation System.

This module provides a unified interface for interacting with Google's Generative AI API.

It supports:
- Multiple Gemini models (1.5-flash, 1.5-pro, 2.0-flash, 2.5-pro-preview-03-25)
- Text generation with temperature control
- JSON generation with schema validation
- Fallback to Node.js implementation if Python package is not available
"""

import os
import json
import logging
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
