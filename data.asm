.include "hdr.asm"

.section ".rodata1" superfree

patterns:
.incbin "resource_bg.pic"
patterns_end:

map:
.incbin "resource_bg.map"
map_end:

palette:
.incbin "resource_bg.pal"
palette_end:
.ends

.section ".rodata2" superfree
patterns2:
.incbin "resource_bg2.pic"
patterns2_end:

map2:
.incbin "resource_bg2.map"
map2_end:

palette2:
.incbin "resource_bg2.pal"
palette2_end:
.ends

.section ".rodata3" superfree
tilfont:
.incbin "resource_font.pic"
tilfont_end:

palfont:
.incbin "resource_font.pal"
palfont_end:
.ends
