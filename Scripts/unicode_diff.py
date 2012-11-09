#!/bin/bash
~/rigaudon/Scripts/unicode_debug.py $1 > /tmp/a.txt
~/rigaudon/Scripts/unicode_debug.py $1 > /tmp/b.txt
diff /tmp/a.txt /tmp/b.txt
