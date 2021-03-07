#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" #diretorio do script
cd $SCRIPT_DIR; cd ..
BASE_DIR=`pwd`
SYNC_DIR="$BASE_DIR"/data
URL_FILE="$BASE_DIR"/URLs.lst
LOG_FILE="$BASE_DIR"/logs/download_files.log

sed -i $'s/\r$//' "$URL_FILE" # DOS to Unix

cat "$URL_FILE" | while read URL; do
    echo "[`date +"%Y/%m/%d %H:%M:%S"`] Downloading files from "${URL}"..." 2>&1 |& tee -a "$LOG_FILE"
    cd "$SYNC_DIR"
    HTML_RESPONSE=`wget --server-response -r -nd "${URL}" -T 5 -t 3 2>&1` #nd = não cria diretórios com a URL (limite: 5s, tentativas: 3)
    #echo -e "$HTML_RESPONSE"
    FILE_NAME=`echo "$HTML_RESPONSE" | awk -F"filename=" '/filename/{print $2;exit;}'`
    mv index.html "$FILE_NAME"
    DATE_TIME=`echo "$HTML_RESPONSE" | awk -F "--" '{print $1 $2;exit;}'`
    SIZE=`echo "$HTML_RESPONSE" | awk '/Tamanho:/{print $2}' | sed -e 's/[()]//g' | sed 's/...$/.&/' | sed 's/..$//'` #sed 's/\(^...\)\(...\)/\1.\2/g'
    THROUGHPUT=`echo "$HTML_RESPONSE" | grep "/s" | head -1 |  awk '{print $3,$4}'`
    DOWNLOAD_TIME=`echo "$HTML_RESPONSE" | awk '/decorrido/{print $4}'`
    echo -e "[`date +"%Y/%m/%d %H:%M:%S"`] "$FILE_NAME" downloaded with "$SIZE" KB in "$DOWNLOAD_TIME" "$THROUGHPUT"" 2>&1 |& tee -a "$LOG_FILE"
    echo -e "[`date +"%Y/%m/%d %H:%M:%S"`] Files have finished downloading from "$URL"!" 2>&1 |& tee -a "$LOG_FILE"
done

#mv index.html `wget --server-response "$URL" 2>&1 | grep "Content-Disposition:" | tail -1 | awk -F"filename=" '{print $2}'`
