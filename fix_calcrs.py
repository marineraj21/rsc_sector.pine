import re

with open('rsc_sector.pine', 'r') as f:
    content = f.read()

# Replace rsLineX = onX ? calcRS(pxX, bmPx) : na
# with
# _rsRawX = calcRS(pxX, bmPx)
# rsLineX = onX ? _rsRawX : na

for i in range(1, 21):
    old_str = f"rsLine{i} = on{i} ? calcRS(px{i}, bmPx) : na"
    new_str = f"_rsRaw{i} = calcRS(px{i}, bmPx)\nrsLine{i} = on{i} ? _rsRaw{i} : na"
    content = content.replace(old_str, new_str)

with open('rsc_sector.pine', 'w') as f:
    f.write(content)
