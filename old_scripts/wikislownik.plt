#!/usr/bin/env gnuplot
reset

set terminal svg enhanced fname "Times"

#set terminal png

set output "Wzrost_Wikislownika.svg"
#set output "Wzrost_Wikislownika.png"

#x data is in date format
set xdata time
set timefmt "%m-%Y"
set format x "%m.%Y"

#white background instead of transparent
set object 1 rect from screen 0, 0, 0 to screen 1, 1, 0 behind
set object 1 rect fc  rgb "white"  fillstyle solid 1.0

#labels
set title font "Times,27" "Rozwój Wikisłownika"
set ylabel font "Times,17" "liczba stron i haseł [tys.]"

#tick font
set xtics font "Times-Roman, 7"
set ytics font "Times-Roman, 7"

#line colors: green for pages, red for entries
set style line 1 lc rgb '#5e9c36'
set style line 2 lc rgb '#8b1a0e'

#setting a grey dashed grid
set style line 12 lc rgb '#808080' lt 0 lw 0.5
set grid back ls 12

#setting the borders in the backgroud (nice looking)
set style line 11 lc rgb '#808080' lt 1
set border 3 back ls 11
set tics nomirror

#ytics spacing: 25, xtics show vertically
set ytics out 25
set xtics out rotate
unset mxtics

#supress extension to the nearest tick (=no margins on x axis)
set autoscale xfix

set bmargin 3.5

#set xtics spacing for 6 months
set xtics 60*60*24*365/2

#key left top
set key inside left top

plot "stat-data.dat" using 1:2 with filledcurves y1=0 ls 1 title "strony", \
     ""              using 1:3 with lines ls 2 title "hasła"
