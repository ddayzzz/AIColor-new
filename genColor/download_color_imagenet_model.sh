#!/bin/bash

# md5sum 09eddf45cd1b085fcb4cc880ba448072
# sha1sum 36b3f03dab74262552dd63ee16b4e1df842a680f

FILENAME="colornet_imagenet.t7"
FILEURL="http://hi.cs.waseda.ac.jp/~iizuka/data/colornet_imagenet.t7"
FILEMD5="09eddf45cd1b085fcb4cc880ba448072"

echo "Downloading ImageNet model (665M)..."
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
