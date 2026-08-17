```sh
just image-convert portrait light "imagemagick_charcoal" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -charcoal 2 $2"
just image-convert portrait light "imagemagick_dither" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -ordered-dither h4x4o -colors 8 $2"
just image-convert portrait light "imagemagick_gray-dither" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -colorspace Gray -ordered-dither o2x2 $2"
just image-convert portrait light "imagemagick_paint" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -paint 3 $2"
just image-convert portrait light "imagemagick_sketch" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -colorspace gray -sketch 0x10+120 $2"
just image-convert landscape light "imagemagick_colors8" "demo/assets/514_Blade Runner 2049_2017.png" "magick $1 -colors 8 -despeckle $2"
just image-convert landscape light "imagemagick_colors16" "demo/assets/514_Blade Runner 2049_2017.png" "magick $1 -colors 16 -despeckle $2"
just image-convert landscape light "imagemagick_threshold" "demo/assets/20200518_12_34_59.jpg" "magick $1 -threshold 60% -despeckle -transparent white $2"
just image-convert portrait light "imagemagick_annotate" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -undercolor #00000050 -fill #FFFFFF -gravity SouthWest -font ""C:/Users/User/Scoop/apps/Sarasa-Term-SC-Nerd/current/SarasaTermSCNerd-Regular.ttf"" -pointsize 20 -interline-spacing 2 -annotate +5+5 \"Pea Blossoms (1890),\n  Edward John Poynter\" $2"
# https://brontosaurusrex.github.io/2019/08/12/Halftone,-Imagemagick
just image-convert portrait light "imagemagick_halftone" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -level 0x70% -set option:distort:viewport '%wx%h+0+0' -colorspace CMYK -separate null: ( -size 2x2 xc: ( +clone -negate ) +append ( +clone -negate ) -append ) -virtual-pixel tile -filter gaussian ( +clone -distort SRT 60 ) +swap ( +clone -distort SRT 30 ) +swap ( +clone -distort SRT 45 ) +swap ( +clone -distort SRT 0 )  +swap +delete -compose Overlay -layers composite -set colorspace CMYK -combine -colorspace RGB $2"
```

```sh
just image-convert portrait light "gmic_gird" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 grid 10%,10%,0,0,0.2,255 -o $2"
just image-convert portrait light "gmic_kuwahara" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 kuwahara 9 -o $2"
just image-convert portrait light "gmic_quantize_blur" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 quantize 6 blur 1 round[-1] quantize_area[-1] 2 -o $2"
just image-convert portrait light "gmic_srgb2lab_blend" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 +srgb2lab slic[-1] 16 +blend shapeaverage f[-2] ""j(1,0)==is && j(0,1)==i"" *[-1][-2] rm[0,1] -o $2"
just image-convert portrait light "gmic_topographic-map" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 topographic_map 10 -o $2"
just image-convert portrait light "gmic_watershed" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 segment_watershed 4 -o $2"
# just image-convert portrait light gmic_matchpath "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 <pattern> +channels[1] 0,2 rm[1] +matchpatch[0] [1],3 +warp[2] [-1],0 rm[0-2] -o $2"
just image-convert portrait light "gmic_cutout" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 fx_cutout 6,0,8,2 -o $2"
just image-convert portrait light "gmic_engrave" "demo/assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 fx_engrave 0.6,60,2,8.8,40,2,4,1,10,1,0,12,0,1,0 gui_merge_layers -o $2"
just image-convert landscape light "gmic_transfer-rgb" "demo/assets/20200518_12_34_59.jpg" "gmic $1 ""demo/assets/514_Blade Runner 2049_2017.png"" +transfer_rgb[0] [1] rm[0,1] -o $2"
```

```sh
# posterust "demo/assets/image.jpg -n 11 -c #ae8653,#110a07,#f3dabd
```