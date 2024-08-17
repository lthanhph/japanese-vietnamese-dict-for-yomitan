from yomitandic import DicEntry, Dictionary, create_html_element
from lxml import etree
from datetime import date
from tag_bank import TagBank
import os
import json
import config

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
        else:
            print(f"dir_path is not exists: {dir_path}")
    except Exception as ex:
        print("Error occurs when deleting files inside output folder: ", ex)


output_dir = config.output_dir
input_dir = config.input_dir
dict_name = config.dict_name

dictionary = Dictionary(f"{output_dir}/{dict_name}")

# Path to your JMdict XML file
jmdict_path = f"{input_dir}/JMdict.xml"

# Parse the JMdict XML file
parser = etree.XMLParser(load_dtd=True, resolve_entities=True, dtd_validation=False)
tree = etree.parse(jmdict_path, parser=parser)
root = tree.getroot()
dtd = tree.docinfo.internalDTD
tag_bank = TagBank()

# Iterate through each entry in the JMdict XML
for entry in root.findall('entry'):
    # Sequence number
    sequence = entry.find('ent_seq').text

    # Extract relevant information from the entry
    kanji_elements = entry.findall('k_ele')
    reading_elements = entry.findall('r_ele')
    sense_elements = entry.findall('sense')

    
    if len(kanji_elements) > 0: 
        
        # Kanji
        for kanji_ele in kanji_elements:   
            kanji = kanji_ele.find('keb').text
    
            # Reading
            if len(reading_elements) > 0: 
                for reading_ele in reading_elements:
                    reading = reading_ele.find('reb').text
            
                    for sense in sense_elements: 
                        # Tag 
                        tag = ''
                        poses = sense.findall('pos');
                        if len(poses) > 0 and poses[0].text != None and poses[0].text != '':
                    
                            for pos in poses:
                                if pos == None or pos == "":
                                    continue
                                
                                # Get entity name
                                entity_name = '';
                                for entity in dtd.entities():
                                    if pos.text.strip() == entity.content.strip(): 
                                        entity_name = entity.name
                                        tag_bank.build(entity_name)
                                
                                tag += " " + entity_name
                                
                        tag = tag.strip()    
                        
                        content = []    

                        # Definition
                        definition_items = []
                        gloss_elements = sense.findall('gloss')
                        for gloss in gloss_elements:
                            if gloss.text == None or gloss.text == "":
                                continue
                                
                            definition_items.append(create_html_element("li", gloss.text))
                        try:
                            if len(definition_items) > 0:      
                                definition = create_html_element("ul", definition_items, data={"content": "glossary"})
                                
                        except Exception as ex:
                            print(f"definition of {kanji} has error: ", ex)
                            print("definition: ")
                            print(definition)
                        
                        content.append(definition)
                        
                        # Example
                        example_elements = sense.findall('example')
                        if len(example_elements) > 0:
                            for example_ele in example_elements:
                                example = []
                                jpn = []
                                vi = []
                                sentences = example_ele.findall('ex_sent')
                                for sent in sentences:            
                                    if "jpn" in sent.attrib.values(): 
                                        jpn = create_html_element("li", sent.text, style={
                                            "listStyleType": "'🇯🇵 '"
                                        })
                                        
                                    if "vi" in sent.attrib.values(): 
                                        vi = create_html_element("li", sent.text, style={
                                            "listStyleType": "'🇻🇳 '"
                                        })
                                
                                if jpn != []: example = create_html_element("ul", [jpn, vi], data={"content": "examples"})
                                if example!= []: content.append(example)                
                                                                                       
                        # Entry    
                        new_entry = DicEntry(
                            kanji, 
                            reading, 
                            tag, 
                            sequence_number=sequence
                        )
                        new_entry.add_element(create_html_element("div", content))

                        # Add the entry to the Yomitan dictionary
                        dictionary.add_entry(new_entry);
                        
                    # Forms
                    if len(kanji_elements) > 1:
                        forms = []
                        for kanji_ele in kanji_elements:
                            forms.append(kanji_ele.find('keb').text)
                                        
                        form_entry = DicEntry(kanji, reading, "forms", forms)
                        dictionary.add_entry(form_entry)    
                        
  
# clear output folder
delete_all_item_inside_dir(output_dir)                   
dictionary.export()
tag_bank.write()

# Open and read the JSON file
with open(f"output/{dict_name}/index.json", 'w') as file:
    today = date.today()
    index = {
        "title": f"{dict_name} [{today}]",
        "format": 3,
        "revision": f"{dict_name}.{today}",
        "sequenced": True,
        "author": "PhuLe",
        "url": "https://github.com/lthanhph/japanese-vietnamese-dict-for-yomitan",
        "description": "",
        "attribution": "This is data from tudienjp. See https://tudienjp.com/",
        "isUpdatable": True,
        "indexUrl": f"https://raw.githubusercontent.com/lthanhph/japanese-vietnamese-dict-for-yomitan/releases/download/{dict_name}/index.json",
        "downloadUrl": f"https://raw.githubusercontent.com/lthanhph/japanese-vietnamese-dict-for-yomitan/releases/download/{dict_name}.zip"
    }
    
    json.dump(index, file, indent=4)

dictionary.zip()
print('success')
