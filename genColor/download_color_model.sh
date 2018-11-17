#!/bin/bash

# md5sum c88fa2bb6dc9f942a492a7dc7009b966
# sha1sum d397faf0b63a173680824474bfeab4725c375ca2
FILENAME="colornet.t7"
FILEURL="http://hi.cs.waseda.ac.jp/~iizuka/data/colornet.t7"
FILEMD5="c88fa2bb6dc9f942a492a7dc7009b966"

echo "Downloading colorized model (663M)..."
wget --continue -O "$FILENAME" -- "$FILEURL"

echo "Checking integrity (md5sum)..."
OS=`uname -s`
if [ "$OS" = "Darwin" ]; then
  CHECKSUM=`cat $FILENAME | md5`
  else
  CHECKSUM=`md5sum $FILENAME | awk '{ print $1 }'`
fi

if [ "$CHECKSUM" != "$FILEMD5" ]; then
  echo "CHECKSUM failed"
  echo "run this script before delete '$FILENAME'"
  exit 1
fi 
echo -e "Download success！"
