"""
URL Shortener Utility
Based on pyshorteners with fallbacks
"""
import pyshorteners
from .logger import logger

def shorten_url(long_url: str) -> str:
    """
    Shorten URL using TinyURL with fallbacks
    
    Args:
        long_url: URL to shorten
        
    Returns:
        str: Shortened URL or original if failed
    """
    try:
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(long_url)
        logger.info(f"URL shortened: {short_url}")
        return short_url
        
    except Exception as e:
        logger.warning(f"TinyURL failed: {e}. Trying Bitly...")
        try:
            # Note: Bitly usually requires API key in pyshorteners, 
            # but lo.py implies it might worth a try or maybe clckru/dagd etc.
            # lo.py tried s.bitly.short which usually fails without key.
            # Let's try clckru as a backup which assumes no key usually
            short_url = s.clckru.short(long_url)
            logger.info(f"URL shortened (clckru): {short_url}")
            return short_url
        except Exception as e2:
            logger.error(f"Failed to shorten URL: {e2}")
            return long_url
