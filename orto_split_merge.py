import os, glob, ntpath, cv2, subprocess, shutil

APP_PATH = r"C:\Program Files\QGIS 3.32.0\OSGeo4W.bat"
dir_path = r"D:\Ortofoto_teste_RGBN\_Tudo"

def filename_from_path(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_list_file_tif(dir_path):        
    listTif = glob.glob(os.path.join(dir_path, '*.tif'))
    listTiff = glob.glob(os.path.join(dir_path, '*.tiff'))
    listTIF = glob.glob(os.path.join(dir_path, '*.TIF'))
    listTIFF = glob.glob(os.path.join(dir_path, '*.TIFF'))
    return listTif + listTiff + listTIF + listTIFF

def pair_dictionary(dir_path):
    img_list = get_list_file_tif(dir_path)
    dictionary = {}

    for img in img_list:
        filename = filename_from_path(img)
        main_name = filename.rsplit('_', 1)[0] 

        if main_name not in dictionary:
            dictionary[main_name] = {'RGB': None, 'INF': None}
        if 'RGB' in filename:
            dictionary[main_name]['RGB'] = img
        if 'INF' in filename:
            dictionary[main_name]['INF'] = img
    return dictionary

def get_red_band(img):
    (_, _, r_channel) = cv2.split(img)
    return r_channel

out_folder_red_inf = os.path.join(dir_path, 'red')
if not os.path.isdir(out_folder_red_inf):
    os.mkdir(out_folder_red_inf)

out_folder_final = os.path.join(dir_path, 'final')
if not os.path.isdir(out_folder_final):
    os.mkdir(out_folder_final)

dictionary = pair_dictionary(dir_path)

for key, value in dictionary.items():
    rgb_img_path = value['RGB']
    inf_img_path = value['INF']

    inf_band = cv2.imread(inf_img_path)
    r_inf = get_red_band(inf_band)
    output_path_image_red_inf = os.path.join(out_folder_red_inf, key + ".tif")
    cv2.imwrite(output_path_image_red_inf, r_inf)
    outpath = os.path.join(out_folder_final,key + ".tif")

    runstrings = [
        f'"{APP_PATH}" gdalbuildvrt r.vrt "{rgb_img_path}" -b 1',
        f'"{APP_PATH}" gdalbuildvrt g.vrt "{rgb_img_path}" -b 2',
        f'"{APP_PATH}" gdalbuildvrt b.vrt "{rgb_img_path}" -b 3',
        f'"{APP_PATH}" gdalbuildvrt mask.vrt "{inf_img_path}" -b 1',
        f'"{APP_PATH}" gdalbuildvrt -separate RGBNA.vrt r.vrt g.vrt b.vrt "{out_folder_final}" mask.vrt',
    ]
    
    for command in runstrings:
        try:
            subprocess.run(command, shell=True, check=True)
            print(f'Success: {command}')
        except subprocess.CalledProcessError as e:
            print(f'Error executing command: {command}\nError: {e}')

    runstring_final_img =  f'"{APP_PATH}" gdal_translate RGBNA.vrt "{outpath}" -co tfw=yes -co -BIGTIFF=YES -colorinterp red,green,blue,gray,alpha'
    runstring_final_img_alt = f'"{APP_PATH}" gdal_translate RGBNA.vrt "{outpath}" -co tfw=yes -colorinterp red,green,blue,gray,alpha'

    try:
        subprocess.run(runstring_final_img, shell=True)    
    except:
        subprocess.run(runstring_final_img_alt, shell=True)  

tempfiles = ['r.vrt','g.vrt','b.vrt','mask.vrt','RGBNA.vrt']
for filename in tempfiles:
    if os.path.isfile(filename):
        os.remove(filename)

if os.path.exists(out_folder_red_inf):
    shutil.rmtree(out_folder_red_inf)

print("Processo concluído.")
input()
