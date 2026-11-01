# SFC用 BMP -> pic/pal/map変換
# by takuya matsubara

# 拡張子を外す
def del_extension(name):
    tempname = name[0:name.find(".")]
    return tempname

#(ファイル名,色数,マップ,マップのパレット番号)
def convert(bmpname,colormode,mapflag,mappal):
#bmpname = 'resource_bg.bmp'     # 入力ファイル名(16Color BMP)
#colormode = 16  # 出力する色数(4/16)
#mapflag = False # マップ保存の有効化(True / False)
#mappal = 0  # マップ保存時のパレット番号(0-7)
    tilename = del_extension(bmpname)+'.pic'        # 出力ファイル名(タイル画像)
    palname = del_extension(bmpname)+'.pal'         # 出力ファイル名(カラーパレット)
    mapname = del_extension(bmpname)+'.map'         # 出力ファイル名(マップ)

    if colormode == 16:
        planemax = 4
    elif colormode == 4:
        planemax = 2
    else:
        print("ERROR:mode error")
        return

    print("open: "+bmpname)
    infile = open(bmpname, 'rb')     # ファイルの読み込み
    bmpbuf = infile.read()
    infile.close()
    header = int.from_bytes(bmpbuf[10:14], 'little')    # ヘッダ長
    width = int.from_bytes(bmpbuf[18:22], 'little')     # 幅[pixel]
    height = int.from_bytes(bmpbuf[22:26], 'little')    # 高さ[pixel]
    depth = int.from_bytes(bmpbuf[28:30], 'little')     # カラーbit
    print(" "+str(width)+" x "+str(height)+"pixel / "+str(depth)+" bit")
    if depth != 4:
        print('ERROR:カラーが16色(4bit)ではありません')
        return
    
    if colormode==4:
        colors = []  # インデックスカラーを色変換テーブルに収集
        for py in range(height):
            for px in range(width):
                ptr = int((px+(((height-1)-py)*width))/2) + header
                if (px & 1)==0 :
                    color = (bmpbuf[ptr] >> 4) & 0x0f
                else:
                    color = bmpbuf[ptr] & 0x0f 
                
                if (color in colors)==False:
                    colors.append(color)  # 未知のインデックスを登録
                    if len(colors) > 4:
                        print("ERROR:4色を超えています")
                        return

        while(len(colors) < 4): # 4色に調整
            colors.append(0)    # 満たない場合は0を追加

        colors.sort()  # 色変換をソート。大きなインデックスを後方へ

    pals = []        # カラーパレット用バッファ
    for i in range(colormode):
        color = i
        if colormode==4:
            color = colors[color]
    
        ptr = 54+(4*color)
        # 24bit(8+8+8) color
        tmp = int.from_bytes(bmpbuf[ptr:ptr+4], 'little')
        r = (tmp >> 16) & 0xff
        g = (tmp >> 8) & 0xff
        b = tmp & 0xff

        # 15bit(5+5+5) color
        r = int(r/((1<<8)/(1<<5)))
        g = int(g/((1<<8)/(1<<5))) 
        b = int(b/((1<<8)/(1<<5))) 
        tmp = (b << 10)+(g << 5)+(r << 0)

        pals.append( (tmp).to_bytes(2, byteorder='little'))

    tiles = []    # タイル画像用バッファ
    chmax = int(width*height/(8*8)) #tile count[cell]
    cellwidth = int(width/8)     ## width[cell]

    tilemap = []    # マップ用バッファ
       
    for chnum in range(chmax):
        x1 = (chnum % cellwidth)*8
        y1 = int(chnum / cellwidth)*8
        tmptile = [] # 一時的なタイル画像
        for plane in range(0,planemax,2):    #プレーンに分解
            for y in range(8):
                tmp = 0
                for x in range(8):
                    px = x+x1
                    py = y+y1
                    ptr = int((px+(((height-1)-py)*width))/2) + header
                    if (px & 1)==0 :
                        color = (bmpbuf[ptr] >> 4) & 0x0f
                    else:
                        color = bmpbuf[ptr] & 0x0f 
                    
                    if colormode==4:
                        color = colors.index(color)

                    if((1 << (plane+0)) & color):
                        tmp += (0x80 >> x)

                    if((1 << (plane+1)) & color):
                        tmp += (0x8000 >> x)
                #
                tmptile.append( (tmp).to_bytes(2, byteorder='little'))
            #
        #
        tileword = len(tmptile)
        tilemax = int(len(tiles)/tileword)
        tilenum = tilemax
        if mapflag==True:
            for num in range(tilemax): # 登録済みタイルを照合
                match = True
                for i in range(tileword):
                    if tiles[(num*tileword)+i] != tmptile[i]:
                        match = False # タイル画像が同じではない
                        break
                
                if(match == True):    # 既知のタイル画像
                    tilenum = num
                    break

            #マップにタイル番号追加
            mapdata = tilenum
            # mapdata |= (0 << 15)   #bit15:V flip
            # mapdata |= (0 << 14)   #bit14:H flip
            # mapdata |= (1 << 13)   #bit13:priority
            mapdata |= (mappal << 10) #bit10-12:Palette number
            tilemap.append( (mapdata).to_bytes(2, byteorder='little'))

        if tilenum == tilemax:     #タイル画像が未発見の場合
            for temp in tmptile:   #タイル画像 追加
                tiles.append(temp)

    outfile = open(palname, 'wb')    # カラーパレットを保存
    for temp in pals:
        outfile.write(temp)
    outfile.close()
    print(" save: "+palname+"/"+str(len(pals)*2)+"Bytes/Color"+str(colormode))

    outfile = open(tilename, 'wb')    # タイル画像を保存
    for temp in tiles:
        outfile.write(temp)
    outfile.close()
    print(" save: "+tilename+"/"+str(len(tiles)*2)+"Bytes/Color"+str(colormode))

    if mapflag==True:
        outfile = open(mapname, 'wb')    # マップを保存
        for temp in tilemap:
            outfile.write(temp)
        outfile.close()
        print(" save: "+mapname+"/"+str(len(tilemap)*2)+"Bytes")

#main
print("BMPからpic/pal/mapを作成します")
convert("resource_bg.bmp",16,True,1)        
convert("resource_bg2.bmp",16,True,2)        
convert("resource_font.bmp",4,False,0)        
print("Done.")