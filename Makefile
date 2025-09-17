FASTROM=1

ifeq ($(strip $(PVSNESLIB_HOME)),)
$(error "Please create an environment variable PVSNESLIB_HOME by following this guide: https://github.com/alekmaul/pvsneslib/wiki/Installation")
endif

include ${PVSNESLIB_HOME}/devkitsnes/snes_rules

.PHONY: bitmaps all

#---------------------------------------------------------------------------------
# ROMNAME is used in snes_rules file
export ROMNAME := bgdemo

all: bitmaps $(ROMNAME).sfc

clean: cleanBuildRes cleanRom cleanGfx

resource_bg.pic: resource_bg.bmp
	$(GFXCONV) -s 8 -o 16 -u 16 -e 1 -p -m -t bmp -i $<

resource_bg2.pic: resource_bg2.bmp
	$(GFXCONV) -s 8 -o 16 -u 16 -e 2 -p -m -t bmp -i $<

resource_font.pic: resource_font.bmp
	$(GFXCONV) -s 8 -o 4 -u 4 -p -t bmp -i $<

bitmaps : resource_bg.pic resource_bg2.pic resource_font.pic

