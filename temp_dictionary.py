import xml.etree.ElementTree as ET
import config
import json

class TempDictionaryCreator:
    def __init__(self):
        self.output = config.temp_dict_output
        self.fullpath = config.temp_dict_fullpath
        self.temp_dict = {}
    
    def create(self):
        self.create_temp_dict()
        self.add_ref_gloss()
        
        if (self.temp_dict != {}):
            try:
                json_temp_dict = json.dumps(self.temp_dict, ensure_ascii=False)
                config.delete_all_item_inside_dir(self.output)
                with open(self.fullpath, "w", encoding="UTF-8") as file:
                    file.write(json_temp_dict)
                print("Create temp dictionary success!")
            except Exception as ex:    
                print("Error when create temp dictionary: ", ex)
           
    def create_temp_dict(self):
        print("Creating temp dictionary ... ")
        
        for event, elem in ET.iterparse(config.jmdict_path, events=('start', 'end')):
            if elem.tag == "entry" and event == "end":
                entry = elem
                sequence = entry.findall("ent_seq")[0].text 
                has_xref = False
                xref_list = []
                for sense in entry.findall("sense"):
                    for xref in sense.findall("xref"):
                        if xref.text not in xref_list:
                            xref_list.append(xref.text)
                
                if xref_list != []:
                    has_xref = True
                                      
                self.temp_dict[sequence] = {
                    "kanjis": [k_ele.findall("keb")[0].text for k_ele in entry.findall("k_ele")],
                    "readings": [r_ele.findall("reb")[0].text for r_ele in entry.findall("r_ele")],
                    "senses_numb": len(entry.findall("sense")),
                    "has_xref": has_xref,
                    "xref_list": xref_list,
                    "glosses": [[gloss.text for gloss in sense.findall("gloss") if gloss.text != None and gloss.text != ""] for sense in entry.findall("sense")]
                }
                
                elem.clear()

    def get_ref_gloss_in_temp_dict(self, ref_kanji, ref_reading, ref_sense_position) -> str:   
        ref_gloss = ""
        
        for sequence_numb in self.temp_dict:
            match_kanji = False       
            if len(self.temp_dict[sequence_numb]["kanjis"]) > 0:
                if ref_kanji in self.temp_dict[sequence_numb]["kanjis"]:
                    match_kanji = True
                else:
                    continue
            elif ref_kanji in self.temp_dict[sequence_numb]["readings"]:
                match_kanji = True
            else:
                continue
            
            if ref_reading == None:
                match_reading = True
            else:
                match_reading = True if ref_reading in self.temp_dict[sequence_numb]["readings"] else False
                    
            if ref_sense_position == None:
                match_sense_position = True
            else:
                match_sense_position = True if ref_sense_position <= self.temp_dict[sequence_numb]["senses_numb"] else False
                
            if match_kanji and match_reading and match_sense_position:
                index = ref_sense_position - 1 if ref_sense_position != None else 0                    
                ref_gloss_list = self.temp_dict[sequence_numb]["glosses"][index]
                ref_gloss = "; ".join(ref_gloss_list)
                break;
                
        return ref_gloss
        
    def add_ref_gloss(self):
        count = 0
        for sequence in self.temp_dict:
            entry = self.temp_dict[sequence]

            if entry["has_xref"] == False:
                continue
            
            xref_list = entry["xref_list"]
            xref_list_with_gloss = {}                  
            for xref in xref_list:              
                xref_parsed = config.parse_xref(xref)
                ref_kanji = xref_parsed["ref_kanji"]
                ref_reading = xref_parsed["ref_reading"]
                ref_sense_position = xref_parsed["ref_sense_position"]
                            
                ref_gloss = self.get_ref_gloss_in_temp_dict(ref_kanji, ref_reading, ref_sense_position)
                xref_list_with_gloss[xref] = ref_gloss
                            
            if xref_list_with_gloss != {}:
                self.temp_dict[sequence]["xref_list"] = xref_list_with_gloss
                count += 1
                print(f"{count} items created")

        