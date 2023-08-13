from fastapi import APIRouter,UploadFile,File,HTTPException,Body
from fastapi.responses import FileResponse
from services.utils import upload_and_save_file,file_basename, get_current_time_stamp, check_extension,delete_folder,raise_error, file_to_base64,delete_file,delete_path,zip_folder, convert_url_to_file
from services.image.background_remover import bg_remove,bg_remover_multiple
from services.image.resize_image import upscale,resize
from services.user_service import get_user_info,canRemoveBg,update_user
import os
import io
import ntpath
from PIL import Image
import base64


router = APIRouter()

@router.post("/image/background_remover")
def bg_remover(files: list[UploadFile]):
    
    length_files = len(files)
    if length_files == 1:
        check_extension(files[0].filename, allows=['jpeg', 'jpg', 'png', 'JPEG', 'JPG', 'PNG'])
        filename = upload_and_save_file(files[0], "uploads/inputs/images/remove_bg/")
        output_path = "uploads/outputs/images/remove_bg/" + str(file_basename(files[0].filename)) + "_bg_remover.png"
        resp = bg_remove(filename, output_path)
        output_path_base64 = file_to_base64(output_path)
        delete_file(filename)
        delete_file(output_path)
        return {"status": "success", "output_file_name": str(file_basename(files[0].filename).split('.')[0]) + "_bg_remover.png", "output_file_base_64" : output_path_base64}
    elif length_files > 1: 

        files_path = []
        tt = get_current_time_stamp()
        input_folder_path = "uploads/inputs/images/remove_bg/" + "tmp_" + tt + "/"
        output_folder_path = "uploads/outputs/images/remove_bg/" + "tmp_" + tt + "/"
        try:
            os.makedirs(input_folder_path, exist_ok=True)
            os.makedirs(output_folder_path, exist_ok=True)
            for file in files:
                check_extension(file.filename, allows=['jpeg', 'jpg', 'png', 'JPEG', 'JPG', 'PNG'])
                f = upload_and_save_file(file, input_folder_path, file.filename)
                files_path.append(f)

            resp = bg_remover_multiple(files_path, output_folder_path, tt)
            output_path_base64 = file_to_base64("uploads/outputs/images/" + resp)
            delete_path(input_folder_path)
            delete_path(output_folder_path)
            return {"status": "success", "output_file_name": tt + "_bg_remover.zip", "output_file_base_64" : output_path_base64}         

        except:
            pass

@router.post("/image/remove-bg-from-url")
async def remove_bg_from_url(imageData : dict = Body(...)):

    urls = imageData["urls"]
    email = imageData["email"]

    user_info = await get_user_info(email)
    count_url = len(urls)

    autorize = False

    print(user_info)

    if len(user_info) == 1:
        user = user_info[0]
        autorize = canRemoveBg(user, count_url)

    if (autorize == True):

        if(count_url == 1):
            url = urls[0]
            ct = get_current_time_stamp()
            filepath = "uploads/inputs/images/remove_bg/" + ct + ".png"
            convert_url_to_file(url=url, file_path=filepath)
            output_path = "uploads/outputs/images/remove_bg/" + ct + "_bg_remover.png"
            resp = bg_remove(filepath, output_path)
            output_path_base64 = file_to_base64(output_path)
            delete_file(filepath)
            delete_file(output_path)
            user["nb_images"] = user["nb_images"] + count_url
            await update_user(email, user)
            return {"status": "success", "output_file_name": ct + "_bg_remover.png", "output_file_base_64" : output_path_base64, "plan" : user["plan"], "nb_images" : user["nb_images"], "nb_images_total" :  user["nb_images_total"] }

        elif count_url > 1:
            files_path = []
            tt = get_current_time_stamp()
            input_folder_path = "uploads/inputs/images/remove_bg/" + "tmp_" + tt + "/"
            output_folder_path = "uploads/outputs/images/remove_bg/" + "tmp_" + tt + "/"
            try:
                os.makedirs(input_folder_path, exist_ok=True)
                os.makedirs(output_folder_path, exist_ok=True)
                for url in urls:
                    filepath = input_folder_path + get_current_time_stamp() + ".png"
                    convert_url_to_file(url=url, file_path=filepath)
                    files_path.append(filepath)
                resp = bg_remover_multiple(files_path, output_folder_path, tt)
                output_path_base64 = file_to_base64("uploads/outputs/images/" + resp)
                delete_path(input_folder_path)
                delete_path(output_folder_path)
                user["nb_images"] = user["nb_images"] + count_url
                await update_user(email, user)
                return {"status": "success", "output_file_name": tt + "_bg_remover.zip", "output_file_base_64" : output_path_base64, "plan" : user["plan"], "nb_images" : user["nb_images"], "nb_images_total" :  user["nb_images_total"]}         

            except:
                pass
                
    else:
        raise HTTPException(status_code=418, detail={"type": "upgrade_plan", "message":"upgrade your plan to remove more background images",  "plan" : user["plan"], "nb_images" : user["nb_images"], "nb_images_total" :  user["nb_images_total"] })
        
@router.get("/download/image/")
def download_image(image_path: str):
    image_path = "uploads/outputs/images/" + image_path
    if os.path.exists(image_path):
        return FileResponse(path=image_path, filename=ntpath.basename(image_path), media_type='application/octet-stream')
    else:
        raise_error(500, "Error: file not found")





@router.post("/image/resize/")
async def resize_image(files: list[UploadFile], new_width:int = 0, new_height:int = 0):

    lenFiles = len(files)

    if lenFiles == 1:
        file = files[0]
        try:
            image = Image.open(file.file)
            resized_image = resize(image, new_width, new_height)

            new_filename = f"resized_{file.filename}"
            buffered = io.BytesIO()
            resized_image.save(buffered, format=image.format)
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return {"status":"success", "message": "Image resized successfully", "filename": new_filename, "image_base_64" : base64_image}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif lenFiles > 1:
        tt = get_current_time_stamp()
        output_tmp_path = "uploads/outputs/images/resized/" + "tmp_" + tt + "/"
        os.makedirs(output_tmp_path, exist_ok=True)
        for file in files:
            image = Image.open(file.file)
            resized_image = resize(image, new_width, new_height)
            new_filename = f"{output_tmp_path}_resized_{file.filename}"
            resized_image.save(new_filename)
        
        zip_path = zip_folder(output_tmp_path, "uploads/outputs/images/resized/" + tt + ".zip")
        output_path_base64 = file_to_base64(zip_path)
        delete_path(output_tmp_path)
        delete_file(zip_path)
        return {"status":"success", "message": "Images resized successfully", "filename": "resized_" + tt + ".zip", "zip_base_64" : output_path_base64}

    else:
        raise HTTPException(status_code=500, detail="error: empty files")


@router.post("/image/upscale/")
async def upscale_image(files: list[UploadFile], dpi: int = 300, new_width:int = 0, new_height:int = 0):

    lenFiles = len(files)

    if lenFiles == 1:
        file = files[0]
        try:
            image = Image.open(file.file)
            resized_image = upscale(image, dpi, new_width, new_height)

            new_filename = f"scaled_{file.filename}"
            buffered = io.BytesIO()
            resized_image.save(buffered, format=image.format)
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return {"status":"success", "message": "Image scaled successfully", "filename": new_filename, "image_base_64" : base64_image}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif lenFiles > 1:
        tt = get_current_time_stamp()
        output_tmp_path = "uploads/outputs/images/upscale/" + "tmp_" + tt + "/"
        os.makedirs(output_tmp_path, exist_ok=True)
        for file in files:
            image = Image.open(file.file)
            resized_image = upscale(image, dpi, new_width, new_height)
            new_filename = f"{output_tmp_path}scaled_{file.filename}"
            resized_image.save(new_filename)
        
        zip_path = zip_folder(output_tmp_path, "uploads/outputs/images/upscale/" + tt + ".zip")
        output_path_base64 = file_to_base64(zip_path)
        delete_path(output_tmp_path)
        delete_file(zip_path)
        return {"status":"success", "message": "Image scaled successfully", "filename": "upscale_" + tt + ".zip", "zip_base_64" : output_path_base64}

    else:
        raise HTTPException(status_code=500, detail="error: empty files")

        



