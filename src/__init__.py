"""
Logger configuration for OraLake
Fixed for Windows Unicode issues
"""

import logging
import sys
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(
    log_dir / "oralake.log",
    encoding='utf-8' 
)
file_handler.setLevel(logging.INFO)

# Console handler - UTF-8 encoding with fallback
if sys.platform == 'win32':
    # Windows: Try to set UTF-8 mode, fallback to ASCII if needed
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        console_handler = logging.StreamHandler(sys.stdout)
    except:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.stream.reconfigure(encoding='ascii', errors='replace')
else:
    console_handler = logging.StreamHandler(sys.stdout)

console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '[%(asctime)s: %(levelname)s: %(name)s: %(message)s]',
    datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.propagate = False