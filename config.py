import os

create_temp_dict = False
output_dir = "./output"
input_dir = "./input"
dict_name = "JA-VIdict"
jmdict_path = f"{input_dir}/JMdict.xml"
temp_dict_output = "./temp_dict"
temp_dict_file = "temp_dict.json"
temp_dict_fullpath = temp_dict_output + "/" + temp_dict_file

  
def delete_all_item_inside_dir(dir_path):
    try:
        if os.path.exists(dir_path) and os.listdir(dir_path):
            for item in os.listdir(dir_path):
                if item == ".gitignore":
                    continue
                        
                item_path = dir_path + "/" + item
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    if os.listdir(item_path): 
                        delete_all_item_inside_dir(item_path)
                    os.rmdir(item_path)
        # else:
        #     print(f"dir_path is not exists: {dir_path}")
    except Exception as ex:
        print(f"Error occurs when deleting files in folder {dir_path}: ", ex)
        
def parse_xref(xref):
    ref_texts = xref.split("・")
    ref_kanji = ref_texts[0]
    ref_reading = None
    ref_sense_position = None
                                                                                    
    if len(ref_texts) == 2 and ref_texts[1].isdigit():
        ref_sense_position = int(ref_texts[1])
                                                
    elif len(ref_texts) == 3:
        ref_reading = ref_texts[1]
        ref_sense_position = int(ref_texts[2])
    
    return {
        "ref_kanji": ref_kanji,
        "ref_reading": ref_reading,
        "ref_sense_position": ref_sense_position
    }