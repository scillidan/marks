```sh
just image-convert portrait light "imagemagick_charcoal" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -charcoal 2 $2"
just image-convert portrait light "imagemagick_paint" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -paint 3 $2"
just image-convert portrait light "imagemagick_sketch" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -colorspace gray -sketch 0x10+120 $2"
just image-convert portrait light "imagemagick_annotate" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -undercolor #00000050 -fill #FFFFFF -gravity SouthWest -font ""C:/Users/User/Scoop/apps/Sarasa-Term-SC-Nerd/current/SarasaTermSCNerd-Regular.ttf"" -pointsize 20 -interline-spacing 2 -annotate +5+5 ""Pea Blossoms (1890),\n  Edward John Poynter"" $2"
just image-convert landscape light "imagemagick_threshold" "assets/20200518_12_34_59.jpg" "magick $1 -threshold 60% -despeckle -transparent white $2"
just image-convert landscape light "imagemagick_range-threshold" "assets/20200518_12_34_59.jpg" "magick $1 -range-threshold 20,50,80% $2"
just image-convert portrait light "imagemagick_ordered-dither" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -ordered-dither h6x6o -colors 8 $2"
just image-convert portrait light "imagemagick_ordered-dither_baver" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -colorspace Gray -ordered-dither o8x8 $2"
just image-convert portrait light "imagemagick_ordered-dither_blue-noise" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -colorspace Gray -ordered-dither h8x8a $2"
just image-convert portrait light "imagemagick_dither_riemersma" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -dither Riemersma -colors 16 $2"
just image-convert portrait light "imagemagick_dither_floydsteinberg" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -dither FloydSteinberg -colors 16 $2"
just image-convert landscape light "imagemagick_colors8" "assets/514_Blade Runner 2049_2017.png" "magick $1 -colors 8 -despeckle $2"
just image-convert landscape light "imagemagick_colors16" "assets/514_Blade Runner 2049_2017.png" "magick $1 -colors 16 -despeckle $2"
just image-convert landscape light "imagemagick_noise_level" "assets/20200518_12_34_59.jpg" "magick $1 +level 20%,80% -sigmoidal-contrast 6,50% -attenuate 0.8  +noise Gaussian $2"
just image-convert landscape light "imagemagick_noise_overlay" "assets/20200518_12_34_59.jpg" "magick $1 ( +clone -fill gray50 -colorize 100 -attenuate 1.2 +noise Gaussian -blur 0x0.3 -colorspace Gray ) -compose overlay -composite $2"
just image-convert landscape light "imagemagick_scanlines_vignette" "assets/20211224_21_25_04.jpg" "magick $1 -colorspace Gray -sigmoidal-contrast 10,45% -modulate 75,0,80 -fill #4a4a3a -tint 60% ( +clone -fill gray50 -colorize 100 +noise Random -blur 0x0.8 -colorspace Gray ) -compose Overlay -composite ( +clone -alpha set -channel A -evaluate set 0 +channel ( -size 8x8 xc:none -fill ""rgba(0,0,0,0.2)"" -draw ""rectangle 0,0 7,3"" -write mpr:scan +delete ) -tile mpr:scan -draw ""rectangle 0,0 %[fx:w-1],%[fx:h-1]"" ) -compose Over -composite ( -size ""%[w]x%[h]"" radial-gradient:""rgba(255,255,255,0.9)-rgba(0,0,0,0.6)"" ) -compose Multiply -composite -level 5%,92% -unsharp 0x1.5+0.8+0 $2"
magick -size 2x4 xc:none -fill rgba(0,0,0,0.35) -draw "line 0,0 2,0" -draw "line 0,2 2,2" assets/scanlines.png && just image-convert portrait light "imagemagick_scanlines" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -write mpr:BASE +delete mpr:BASE -alpha transparent -tile assets/scanlines.png -draw ""rectangle 0,0 99999,99999"" mpr:BASE +swap -composite $2"
magick -size 1x256 gradient:blue-yellow assets/lut.png && just image-convert portrait light "imagemagick_clut" "assets/20200518_12_34_59.jpg" "magick $1 ""assets/lut.png"" -clut $2"
# https://brontosaurusrex.github.io/2019/08/12/Halftone,-Imagemagick
just image-convert portrait light "imagemagick_halftone_fx" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "magick $1 -level 0x70% -set option:distort:viewport '%wx%h+0+0' -colorspace CMYK -separate null: ( -size 2x2 xc: ( +clone -negate ) +append ( +clone -negate ) -append ) -virtual-pixel tile -filter gaussian ( +clone -distort SRT 60 ) +swap ( +clone -distort SRT 30 ) +swap ( +clone -distort SRT 45 ) +swap ( +clone -distort SRT 0 )  +swap +delete -compose Overlay -layers composite -set colorspace CMYK -combine -colorspace Gray $2"
# https://github.com/antiboredom/p5.riso/tree/master/examples/Halftone
just image-convert landscape light "imagemagick_halftone_misregistration-distort" "assets/20200518_12_34_59.jpg" "magick $1 -colorspace gray -fx ""angle=(45 * 3.1415926/180); spacing=8; pos=(i*cos(angle) + j*sin(angle)); line=((sin(pos*2 * 3.1415926/spacing)+1)/2); u < line ? 1 : 0"" -alpha copy -fill #0000FF -colorize 100 -background #FFFF00 -flatten $2"
```

```sh
just image-convert portrait light "gmic_gird" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 grid 10%,10%,0,0,0.2,255 -o $2"
just image-convert portrait light "gmic_kuwahara" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 kuwahara 9 -o $2"
just image-convert portrait light "gmic_quantize_blur" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 quantize 6 blur 1 round[-1] quantize_area[-1] 2 -o $2"
just image-convert portrait light "gmic_srgb2lab_blend" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 +srgb2lab slic[-1] 16 +blend shapeaverage f[-2] ""j(1,0)==is && j(0,1)==i"" *[-1][-2] rm[0,1] -o $2"
just image-convert portrait light "gmic_topographic-map" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 topographic_map 10 -o $2"
just image-convert portrait light "gmic_watershed" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 segment_watershed 4 -o $2"
just image-convert portrait light "gmic_cutout" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 fx_cutout 6,0,8,2 -o $2"
just image-convert portrait light "gmic_engrave" "assets/Edward John Poynter_Pea Blossoms, 1890.jpg" "gmic $1 fx_engrave 0.6,60,2,8.8,40,2,4,1,10,1,0,12,0,1,0 gui_merge_layers -o $2"
just image-convert landscape light "gmic_transfer-rgb" "assets/20200518_12_34_59.jpg" "gmic $1 ""assets/514_Blade Runner 2049_2017.png"" +transfer_rgb[0] [1] rm[0,1] -o $2"
just image-convert landscape light "gmic_matchpath_01" "assets/20200518_12_34_59.jpg" "gmic $1 ""assets/Edward John Poynter_Pea Blossoms, 1890.jpg"" +matchpatch[0] [1],3 +warp[-2] [-1],0 rm[0-2] -o $2"
just image-convert landscape light "gmic_matchpath_02" "assets/20200518_12_34_59.jpg" "gmic $1 ""image-collect\assets\待ちぼうけ.jpg"" +matchpatch[0] [1],3 +warp[-2] [-1],0 rm[0-2] -o $2"
just image-convert landscape light "gmic_quantize" "assets/20200518_12_34_59.jpg" "gmic $1 quantize 8 -o $2"
# gmic $1 quantize 8 +split_colors 3 -o "output_%d.png"
```

```sh
# posterust "assets/image.jpg -n 11 -c #ae8653,#110a07,#f3dabd
```