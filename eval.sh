#! /bin/bash

# if [ "$#" -ne 3 ]; then
   # echo "Usage: ./eval.sh <darknet_home> <yolo_weights> <testing_data_file>"
   # exit 1
# fi

# darknet_home=$1
# weights=$2
# file=$3

weights=$1
darknet_home=/workspace/darknet
file=/data/full_10_class_yolo/val.txt

rm -rf $darknet_home/output
mkdir -p $darknet_home/output
while read img; do
  echo $img
  $darknet_home/darknet yolo test $darknet_home/cfg/yolo.cfg $weights $img && \
  mv $darknet_home/predictions.png $darknet_home/output/$img || exit 1
done < $file

