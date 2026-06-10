# limit the ram usage to 256000 Kilobytes(KB)
ulimit -v 256000

# Run the file with time limit of 1 second
timeout 1 python3 test.py < input.txt
