import re

with open('rsc_sector.pine', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace ™ with (TM) to avoid Pine Script encoding errors
content = content.replace('™', '(TM)')
# Replace stylized dashes
content = content.replace('—', '-')

with open('rsc_sector.pine', 'w', encoding='utf-8') as f:
    f.write(content)
