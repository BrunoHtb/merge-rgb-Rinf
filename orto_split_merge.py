import os, glob, ntpath, cv2, subprocess

APP_PATH = r"C:\Program Files\QGIS 3.32.0\OSGeo4W.bat"
dir_path = r"D:\Ortofoto_teste_RGBN\_Tudo"

def filename_from_path(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_list_file_tif(dir_path):        
    result1 = glob.glob(os.path.join(dir_path, '*.tif'))
    result2 = glob.glob(os.path.join(dir_path, '*.tiff'))
    result3 = glob.glob(os.path.join(dir_path, '*.TIF'))
    result4 = glob.glob(os.path.join(dir_path, '*.TIFF'))
    return result1 + result2 + result3 + result4

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

def replace_red_with_nir(rgb_image, inf_band):
    r_inf = get_red_band(inf_band)
    b_rgb, g_rgb, r_rgb = cv2.split(rgb_image)
    new_image = cv2.merge((b_rgb, g_rgb, r_rgb, r_inf))
    return new_image

out_folder = os.path.join(dir_path, 'split')
out_folder_red_inf = os.path.join(dir_path, 'red')

if not os.path.isdir(out_folder):
    os.mkdir(out_folder)
if not os.path.isdir(out_folder_red_inf):
    os.mkdir(out_folder_red_inf)

img_list = get_list_file_tif(dir_path)
dictionary = pair_dictionary(dir_path)

for key, value in dictionary.items():
    rgb_img_path = value['RGB']
    inf_img_path = value['INF']

    rgb_image = cv2.imread(rgb_img_path)
    inf_band = cv2.imread(inf_img_path)

    result_image = replace_red_with_nir(rgb_image, inf_band)    
    output_path_image = os.path.join(out_folder, key + ".tif")
    cv2.imwrite(output_path_image, result_image)

    r_inf = get_red_band(inf_band)
    output_path_image_red_inf = os.path.join(out_folder_red_inf, key + ".tif")
    cv2.imwrite(output_path_image_red_inf, r_inf)

    out_folder_final = os.path.join(dir_path, 'final')
    if not os.path.isdir(out_folder_final):
        os.mkdir(out_folder_final)

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
    '''
    for runstring in runstrings:
        print(runstring)
        subprocess.run(runstring, shell=True)
'''
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

print("Processo concluído.")
input()
