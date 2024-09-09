import Quartz
import Quartz.CoreGraphics as CG
from PIL import Image
import numpy as np

def capture_screen(window_title):
    # Get the list of all windows
    window_list = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
    
    # Find the window with the specified title
    window = None
    for win in window_list:
        if win.get('kCGWindowName', '') == window_title:
            window = win
            break
    
    if not window:
        print(f"Window with title '{window_title}' not found")
        return
    
    # Get the window bounds
    bounds = window['kCGWindowBounds']
    x, y, width, height = int(bounds['X']), int(bounds['Y']), int(bounds['Width']), int(bounds['Height'])
    
    # Create a screen capture of the specified area
    image_ref = Quartz.CGWindowListCreateImage(CG.CGRectMake(x, y, width, height),
                                               Quartz.kCGWindowListOptionIncludingWindow,
                                               window['kCGWindowNumber'],
                                               Quartz.kCGWindowImageBoundsIgnoreFraming)
    
    if image_ref is None:
        print(f"Failed to capture the window with title '{window_title}'.")
        return None
    
    # Get the actual width and height of the image
    width = Quartz.CGImageGetWidth(image_ref)
    height = Quartz.CGImageGetHeight(image_ref)
    bytesperrow = CG.CGImageGetBytesPerRow(image_ref)

    pixeldata = CG.CGDataProviderCopyData(CG.CGImageGetDataProvider(image_ref))
    image = np.frombuffer(pixeldata, dtype=np.uint8)
    image = image.reshape((height, bytesperrow//4, 4))
    image = image[:,:width,:]
    return image