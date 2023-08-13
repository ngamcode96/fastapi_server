from rembg import remove, new_session
from pathlib import Path
from services.utils import file_basename,zip_folder,compress_png
import ntpath
from PIL import Image

def bg_remove(input_path, output_path):
    print(input_path)
    print(output_path)
    with open(input_path, 'rb') as i:
        with open(output_path, 'wb') as o:
            input = i.read()
            output = remove(input)
            print(output)
            o.write(output)
            # compress_png(input_path=output_path, output_path="test.png", quality=50)
    return output_path


def bg_remover_multiple(files_path, output_folder, tt):
    session = new_session()

    for input_path in files_path:
        out = output_folder + str(ntpath.basename(input_path)) +  "_bg_remover.png"
        with open(input_path, 'rb') as i:
            with open(out, 'wb') as o:
                input = i.read()
                output = remove(input, session=session)
                o.write(output)

    resp = zip_folder(output_folder, "uploads/outputs/images/remove_bg/" + tt + ".zip")

    if resp:
        return "remove_bg/" + tt + ".zip"
