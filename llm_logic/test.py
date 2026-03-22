import sys
import os
import traceback

from api import compress_code, get_modernizer, logger

try:
    print("compressing...")
    comp = compress_code('MOVE 10 TO WS-A')
    print("modernizing...")
    mod = get_modernizer()
    res = mod.modernize(comp, 'cobol', 'python')
    print("modernized success:", res.success)
    if not res.success:
        print("error:", res.error)
    metrics = logger.log(result=res, raw_token_count=10, source_file="test")
    print("logged success")
except Exception as e:
    traceback.print_exc()
