for dir in ~/Pictures/*/
do
  echo "Processing $dir ..."
  cd "$dir"
  find . -type f -iname "*.jpg" -o -iname "*.jpeg" | xargs -d '\n' jpeginfo -c | grep -E "WARNING|ERROR"
done
