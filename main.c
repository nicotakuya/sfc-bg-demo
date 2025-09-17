// BG DEMO for Super Famicom
// by Takuya Matsubara
#include <snes.h>

extern char patterns, patterns_end;
extern char palette, palette_end;
extern char map, map_end;
extern char patterns2, patterns2_end;
extern char palette2, palette2_end;
extern char map2, map2_end;
extern char tilfont, palfont;
extern char tilfont_end, palfont_end;

// パレット番号
#define PAL_TXT    0  // テキスト
#define PAL_BACK   1  // 背景（手前）
#define PAL_BACK2  2  // 背景（奥）

// BG番号
#define BGN_TXT    2  // テキスト
#define BGN_BACK   0  // 背景（手前）
#define BGN_BACK2  1  // 背景（奥）

// VRAM 0x0000-7FFF
#define VRAM_TXTMAP   0x2800 // テキスト タイルマップ
#define VRAM_TXTPTN   0x2000 // テキスト パターン
#define VRAM_BACKMAP  0x3000 // 背景(手前) タイルマップ
#define VRAM_BACKPTN  0x4000 // 背景(手前) パターン
#define VRAM_BACK2MAP 0x5000 // 背景(奥) タイルマップ
#define VRAM_BACK2PTN 0x6000 // 背景(奥) パターン

u8 vramwork[32];
char tempstr[6];

// 10進数3ケタ変換(格納先ポインタ,数値0～255)
void u8_to_str(char *str,u8 num)
{
    char i=3;
    str += 3;
    *str = 0; // NULL
    str--;
    while(i--){
        *str = (num % 10)+'0';
        num /= 10;
        str--;
    }
}

// BG3に文字表示
void bg3print(u8 x, u8 y, u8 *ptr)
{
    u16 vramaddr;
    u16 length=0;
    u8 *dst;
    dst = (u8 *)vramwork;
    // タイルマップに変換
    while(*ptr != 0){
        *dst++ = *ptr++ - 0x20;
        *dst++ = (1 << 5)+(PAL_TXT << 2);
           // priority bit + palette
        length += 2;
    }
    vramaddr = VRAM_TXTMAP+(32*y)+x;
    dmaCopyVram(vramwork, vramaddr, length);
//    WaitForVBlank();
}

//----
int main(void)
{
    char i;
    unsigned char bgx,bgy,bg2x,bg2y;

    // 背景(手前)
    bgInitTileSet(
        BGN_BACK,   // BG番号
        &patterns,  // パターンデータ
        &palette,   // パレットデータ
        PAL_BACK,   // パレット番号
        (&patterns_end - &patterns),   // パターンのサイズ
        (&palette_end - &palette),     // パレットのサイズ
        BG_16COLORS,   // used for correctry
        VRAM_BACKPTN   // パターンのアドレス
    );

    // 背景(手前)
    bgInitMapSet(
        BGN_BACK,    // BG番号
        &map,        // タイルマップデータ
        (&map_end - &map),// タイルマップのサイズ
        SC_32x32,    // tile mapping
        VRAM_BACKMAP // タイルマップのアドレス
    );

    // 背景(奥)
    bgInitTileSet(
        BGN_BACK2,  // BG番号
        &patterns2, // パターンのデータ
        &palette2,  // パレットのデータ
        PAL_BACK2,  // パレット番号
        (&patterns2_end - &patterns2),   // パターンのサイズ
        (&palette2_end - &palette2),     // パレットのサイズ
        BG_16COLORS,   //
        VRAM_BACK2PTN     // パターンのアドレス
    );

    // 背景(奥)
    bgInitMapSet(
        BGN_BACK2,    // BG番号
        &map2,        // タイルマップのデータ
        (&map2_end - &map2),// タイルマップのサイズ
        SC_32x32,     // tile mapping
        VRAM_BACK2MAP // タイルマップのアドレス
    );

    // テキストの初期化
    bgSetGfxPtr(BGN_TXT, VRAM_TXTPTN); // パターンのアドレス
    bgSetMapPtr(BGN_TXT, VRAM_TXTMAP, SC_32x32); // タイルマップのアドレス

    // テキストのパターン
    bgInitTileSet(
        BGN_TXT,
        &tilfont,
        &palfont,
        PAL_TXT,
        (&tilfont_end - &tilfont),
        (&palfont_end - &palfont),
        BG_4COLORS0,
        VRAM_TXTPTN
    );

    // テキストのパレットを変更
    u8 *ptr = (u8 *)&palfont;
    for(i=0; i<4; i++){
        u16 color;  // 15bit カラー
        color = (u16)*ptr++;
        color += (u16)*ptr++ << 8;
        setPaletteColor(i+(PAL_TXT*16),color);
    }

    bg3print(8,  8, "BG DEMO");
    bg3print(8, 10, " for SUPER FAMICOM");
    bg3print(10,14, "X:");

    // BG3を一番手前にする
    setMode(BG_MODE1, BG3_MODE1_PRIORITY_HIGH);
    WaitForVBlank();
    setScreenOn();

    bgx = 0;
    bgy = 0;
    bg2x = 0;
    bg2y = 0;
    while (1){
    	u8_to_str(tempstr,bgx);
        bg3print(12,14,tempstr);

        bgSetScroll(BGN_BACK , bgx , bgy);
        bgSetScroll(BGN_BACK2, bg2x, bg2y);
        bgx++;
        if(bgx & 1){
            bgy++;
            if(bgy & 1){
                bg2x++;
                if(bg2x & 1){
                    bg2y++;
                }
            }
        }
        WaitForVBlank();
    }
    return 0;
}
