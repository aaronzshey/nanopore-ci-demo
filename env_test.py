from dotenv import load_dotenv
import os
load_dotenv()
WDIR=os.getenv('WDIR')

print(WDIR)