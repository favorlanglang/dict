#!/bin/bash
input="$1"
output="${1%.pdf}-header.pdf"
pagenum=$(pdftk "$input" dump_data | grep "NumberOfPages" | cut -d":" -f2)
enscript --fancy-header=simple --header="HEADER" -L1 -b'||' --footer '||$%' --output - < <(for i in $(seq "$pagenum"); do echo; done) | ps2pdf - | pdftk "$input" multistamp - output $output
