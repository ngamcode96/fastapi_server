from PIL import Image
from fastapi import HTTPException


def resize(image, new_width, new_height):
    try:

        if (new_width != 0 and new_height != 0):
            new_size = (new_width, new_height)
        else:
            raise HTTPException(status_code=500, detail="an error occur")

        resized_image = image.resize(new_size, resample=Image.BICUBIC)

        return resized_image
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="an error occur")


def upscale(image, dpi, width, height):
    try:
        # dpi_ratio = dpi / image.info["dpi"][0]
        # new_size = (6000, 6000)

        if (width != 0 and height != 0):
            new_size = (width, height)
        elif (width == 0 and height == 0):
            current_dpi = image.info.get("dpi", (72, 72))
            scale_factor = dpi / current_dpi[0]
            # Calculate the new width and height based on the scale factor
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            new_size = (new_width, new_height)
        else:
            raise HTTPException(status_code=500, detail="an error occur")

        resized_image = image.resize(new_size, resample=Image.BICUBIC)

        return resized_image
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="an error occur")

