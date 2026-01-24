import sys
import os
sys.path.append(os.getcwd())
try:
    from animals import voidoll
    print("Import Successful")
except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()
