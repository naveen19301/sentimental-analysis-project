import re
import html

def extract_fresh_message(text):
    """Extract only sender's fresh message - removes email history"""
    if not text:
        return ""

    text = html.unescape(text)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)

    reply_patterns = [
        r'\bOn\s+.*?wrote\s*:',
        r'\bFrom:\s+.*',
        r'\bSent:\s+.*',
        r'\bTo:\s+.*',
        r'\bSubject:\s+.*',
        r'-----Original Message-----',
        r'---- Forwarded message ----',
        r'>\s*wrote:',
    ]

    for p in reply_patterns:
        text = re.split(p, text, flags=re.IGNORECASE | re.DOTALL)[0]

    footer_patterns = [
        r'(?i)thanks.*',
        r'(?i)warm\s+regards.*',
        r'(?i)regards.*',
        r'(?i)team\s+astro.*',
        r'(?i)astro\s+arun\s+pandit.*',
        r'(?i)customer\s+support.*',
    ]

    for f in footer_patterns:
        text = re.split(f, text)[0]

    return re.sub(r'\s+', ' ', text).strip()

def extract_full_text(text):
    """Extract full text without removing email history"""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def build_thread_text(threads):
    if not threads:
        return ""
    result = []
    for idx, thread in enumerate(threads, 1):
        result.append(f"Thread{idx}- {thread}")
    return "\n\n".join(result)
