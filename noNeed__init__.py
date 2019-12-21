# This file is required to use relative import.
# Note: This file is not needed since pytest somehow support direct import from pxutil.
import os, sys
# sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# add sub-folder pxutil to python import path.
sys.path.append(os.path.join( os.path.dirname(os.path.realpath(__file__)),'pxutil' ) )