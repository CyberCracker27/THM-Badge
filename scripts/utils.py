import datetime
import re

def parse_joined_date(text):
    """Extract YYYY-MM-DD from 'Joined 2022-01-15'."""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    if match:
        return datetime.datetime.strptime(match.group(1), '%Y-%m-%d')
    return None

def days_since(date):
    return (datetime.datetime.now() - date).days if date else 0
