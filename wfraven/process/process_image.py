import time
import shutil
import hashlib

from PIL import Image
from pathlib import Path


def calculate_sizes(image_type, image):
    """Calculate sizes to resize the `image` to, based on the `image_type`
    
    `image_type` can be any of `"avatar"`, `"audio"`, `"art"`, or `"image"`.
    """

    sizes = []
    (width, height) = image.size

    if image_type == 'avatar':
        # Always return default avatar sizes
        return [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512)]

    elif image_type == 'audio':
        # Always return default audio art sizes
        return [(50, 50), (100, 100), (200, 200)]

    elif image_type == 'art':
        # Clamp width/height at 8192px for art posts
        art_width = max(width, 8192)
        art_height = max(height, 8192)
        sizes.append((art_width, art_height))
    
    # Default sizes
    for size_test in [(1280, 4096), (810, 4096), (540, 4096), (300, 4096)]:
        if len(sizes) == 0 or width > size_test[0]:
            sizes.append(size_test)

    return sizes
        

def process(image_data, image_type, image_fn, size, date_hash, base_dir, output_dir):
    start_time = time.time()
    our_data = {'url': {}}
    image = Image.open(str(image_fn))
    
    # If the image is a GIF, store as-is
    if image.format.lower() == 'gif':
        image.close()

        # zero timedelta on the resize op because there was no resize op
        our_data['resize'] = 0 
        
        # generate output filename and just copy the image over
        output_filename = Path(output_dir) / f"wfraven_{date_hash}_{size[0]}.gif"
        shutil.copyfile(str(image_fn), str(Path(base_dir) / output_filename))
        
        # Set our paths
        our_data['url']['legacy'] = str(output_filename)
        our_data['url']['modern'] = str(output_filename)
        
        # Do the MD5
        with open(image_fn, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)

            our_data['md5'] = m.hexdigest()
            our_data['md5p'] = m.hexdigest()
            
    # Not a GIF, let's do some actual work
    else:
        # Convert to RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Resize the image and save our timedelta
        image.thumbnail(size)
        our_data['resize'] = (time.time() - start_time)

        # Save a WebP
        webp_filename = Path(output_dir) / f"wfraven_{date_hash}_{size[0]}.webp"
        image.save(str(Path(base_dir) / webp_filename), quality=100)
        
        # Save a PNG
        png_filename = Path(output_dir) / f"wfraven_{date_hash}_{size[0]}.png"
        image.save(str(Path(base_dir) / png_filename), quality=100)
        
        # Close the image
        image.close()
        
        # Set our paths
        # "Legacy" is PNG, "Modern" is WebP
        our_data['url']['legacy'] = str(png_filename)
        our_data['url']['modern'] = str(webp_filename)
        
        # MD5 the WebP
        with open(str(Path(base_dir) / webp_filename), 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)

            our_data['md5'] = m.hexdigest()

        # MD5 the PNG
        with open(str(Path(base_dir) / png_filename), 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)

            our_data['md5p'] = m.hexdigest()
        
    our_data['time'] = (time.time() - start_time)
    image_data[int(size[0])] = our_data
