from time import strftime

# Get well formated timestamp
def timestamp():
    ts = strftime("(%x, %X)")
    return ts