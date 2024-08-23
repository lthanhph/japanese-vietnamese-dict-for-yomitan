from yomitandic import DicEntry, Dictionary, create_html_element
from lxml import etree
from datetime import date
from tag_bank import TagBank
from temp_dictionary import TempDictionaryCreator
import json
import config
import os

if __name__ == "__main__":
    
    if config.create_temp_dict == True:
        temp_dict_creator = TempDictionaryCreator()
        temp_dict_creator.create()
        exit()
        
    if not os.path.exists(config.temp_dict_fullpath):
        print(f"{config.temp_dict_file} file not found")
        print(f"Please set create_temp_dict variable in config to True and create {config.temp_dict_file} before creating {config.dict_name} dictionary")
        exit()  

    output_dir = config.output_dir
    input_dir = config.input_dir
    dict_name = config.dict_name

    dictionary = Dictionary(f"{output_dir}/{dict_name}")
    
    with open(config.temp_dict_fullpath, encoding="UTF-8") as file:
        temp_dict = json.loads(file.read())
        
    # Path to your JMdict XML file
    jmdict_path = config.jmdict_path

    # Parse the JMdict XML file
    parser = etree.XMLParser(load_dtd=True, resolve_entities=True, dtd_validation=False)
    tree = etree.parse(jmdict_path, parser=parser)
    root = tree.getroot()
    dtd = tree.docinfo.internalDTD
    tag_bank = TagBank()

    def create_span_element(content, style={}, data=""):
            default_style = {"fontSize": "65%", "verticalAlign": "middle"}
            final_style = style if style != {} else default_style
            return create_html_element(
                "span",
                content,
                style=final_style,
                data=data,
            )

    def get_reference(xref, ref_gloss) -> None:
        xref_parsed = config.parse_xref(xref)
        ref_kanji = xref_parsed["ref_kanji"]
        ref_sense_position = xref_parsed["ref_sense_position"]
        
        if ref_sense_position != None:
            ref_gloss = f" {ref_sense_position}. " + ref_gloss
        else:
            ref_gloss = " " + ref_gloss
            
        ref_content = create_html_element("li", [
            create_span_element("Xem "),
            create_html_element(
                "a",
                ref_kanji,
                href=f"?query={ref_kanji}\u0026wildcards=off",
                ),
            create_span_element(ref_gloss, data={"content": "refGlosses"})
        ])

        references = create_html_element(
            "ul", 
            [ref_content], 
            style={"listStyleType": "'➡️ '"},
            data={"content": "references"}
        )
                    
        return references            

    def loop_kanji_elements(kanji_elements, reading_elements, sequence = 0) -> None:
        for kanji_ele in kanji_elements:   
            kanji = kanji_ele.find('keb').text
            
            loop_reading_elements(kanji, reading_elements, sequence)

    def loop_reading_elements(kanji="", reading_elements = [], sequence = 0) -> None:
        for reading_ele in reading_elements:
            reading = reading_ele.find('reb').text
            
            if kanji == "": kanji = reading
            loop_sense_elements(kanji, reading, sense_elements, sequence)

    def loop_sense_elements(kanji, reading, sense_elements, sequence = 0) -> None:
        sense_count = 0
        for sense in sense_elements:
            sense_count += 1 
            dict_entry = create_dict_entry(kanji, reading, sense, sense_count, sequence)
            dictionary.add_entry(dict_entry); 

    def create_dict_entry(kanji, reading, sense, sense_count, sequence = 0):
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
                
        tag_bank.build(str(sense_count))
        tag = str(sense_count) + " " + tag.strip()      
        
        # Defifition content                    
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
                content.append(definition) 
                                
        except Exception as ex:
            print(f"definition of {kanji} has error: ", ex)
            print("definition: ", definition)
                                                    
        # Note
        note_elements = sense.findall("s_inf")
        if len(note_elements) > 0:
            for note_ele in note_elements:
                note = create_html_element("ul", 
                                           [create_html_element("li", note_ele.text)], 
                                           style={"listStyleType": "'📝 '"}, 
                                           data={"content": "notes"}
                                           )               
                content.append(note)
                            
        # References                                                    
        if len(sense.findall("xref")) > 0:
            for xref in sense.findall("xref"):
                xref_list = temp_dict[str(sequence)]["xref_list"] 
                if xref.text in xref_list:
                    ref_gloss = xref_list[xref.text]
                    references = get_reference(xref.text, ref_gloss)   
                    content.append(references)  
                
                        
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
        dict_entry = DicEntry(
            kanji, 
            reading, 
            tag, 
            sequence_number=sequence
        )
        
        try:                                 
            dict_entry.add_element(create_html_element("div", content))
        except Exception as ex:
            print("Error when create new dict entry: ", ex)
            print("Definition content: ")
            print(content)
        
        return dict_entry

    def create_form(kanji_elements, reading_elements, sequence) -> None:
        form = []
        if len(kanji_elements) > 1:
            form = [kanji_ele.find('keb').text for kanji_ele in kanji_elements]
            
            for kanji_ele in kanji_elements:
                for reading_ele in reading_elements:
                    dictionary.add_entry(DicEntry(kanji_ele.find('keb').text, reading_ele.find('reb').text, "forms", form, sequence_number=sequence))
        
        elif len(reading_elements) > 1:
            form = [reading_ele.find('reb').text for reading_ele in reading_elements]
            
            for reading_ele in reading_elements:
                dictionary.add_entry(DicEntry(reading_ele.find('reb').text, reading_ele.find('reb').text, "forms", form, sequence_number=sequence))

    print("Parsing JMdict.xml file components ... ")
    # Iterate through each entry in the JMdict XML

    for entry in root.findall("entry"):
        # Sequence number
        sequence = int(entry.findall("ent_seq")[0].text)
        
        # Extract relevant information from the entry
        kanji_elements = entry.findall("k_ele")
        reading_elements = entry.findall("r_ele")
        sense_elements = entry.findall("sense")

        if len(kanji_elements) > 0:
            loop_kanji_elements(kanji_elements, reading_elements, sequence)

        elif len(reading_elements) > 0:
            loop_reading_elements(reading_elements=reading_elements, sequence=sequence)

        create_form(kanji_elements, reading_elements, sequence) 

    # clear output folder
    print("Creating new dictionary ...")
    config.delete_all_item_inside_dir(output_dir) 
    
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
                      
    dictionary.export(index)
    tag_bank.write()

    dictionary.zip()
    print('Success !!')
