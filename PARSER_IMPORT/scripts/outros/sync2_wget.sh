#!/usr/bin/env bash

URL=192.168.0.150
BASE_DIR=c:/Users/tulio/Desktop/FILES/
SYNC_DIR="$BASE_DIR"/data
LOG_FILE="$BASE_DIR"/log/download_log.txt

cd $SYNC_DIR
HTML_RESPONSE=`wget --content-disposition "$URL" 2>&1`
echo -e "$HTML_RESPONSE"
FILE_NAME=`echo "$HTML_RESPONSE" | awk '/Salvando/{print $3;exit;}'`
DATE_TIME=`echo "$HTML_RESPONSE" | awk -F "--" '{print $1 $2;exit;}'`
SIZE=`echo "$HTML_RESPONSE" | awk '/Tamanho:/{print $2}' | sed -e 's/[()]//g' | sed 's/...$/.&/' | sed 's/..$//'` #sed 's/\(^...\)\(...\)/\1.\2/g'
THROUGHPUT=`echo "$HTML_RESPONSE" | grep "/s" | head -1 |  awk '{print $3,$4}'`
DOWNLOAD_TIME=`echo "$HTML_RESPONSE" | awk '/%/{print $4}'`
echo -e "["$DATE_TIME"] "$FILE_NAME" downloaded with "$SIZE" KB in "$DOWNLOAD_TIME" "$THROUGHPUT""
#echo -e "["$DATE_TIME"] "$FILE_NAME" downloaded with "$SIZE" KB in "$DOWNLOAD_TIME" "$THROUGHPUT"" >> $LOG_FILE


#mv index.html `wget --server-response "$URL" 2>&1 | grep "Content-Disposition:" | tail -1 | awk -F"filename=" '{print $2}'`
