import json
import config

class TagBank:
    def __init__(self) -> None:
        self.jmdict_tag_bank_file = f"{config.input_dir}/tag_bank_1.json"
        self.jmdict_tag_bank = self.get_jmdict_tag_bank()
        self.tag_bank = []
        self.ouput_file = f"{config.output_dir}/{config.dict_name}/tag_bank_1.json"

    def get_jmdict_tag_bank(self):
        try:
            file =  open(self.jmdict_tag_bank_file, 'r', encoding='utf-8')
            jmdict_tag_bank = json.load(file)
            file.close()
            return jmdict_tag_bank
        except Exception as ex:
            print("Error load jmdict tag bank: ", ex)
            
    def exists(self, tag) -> bool:
        exists = False
        for tag_available in self.tag_bank:
            if (tag == tag_available[0]):
                exists = True
                break
            
        return exists
    
    def build(self, tag) -> None:
        exists = self.exists(tag)
        
        if tag != None and tag != '' and not exists:
            jmdict_tag_content = []
            for jmdict_tag in self.jmdict_tag_bank:
                if (tag == jmdict_tag[0]):
                    jmdict_tag_content = jmdict_tag
                    break;

            if jmdict_tag_content != []:
                self.tag_bank.append(jmdict_tag_content)
            else:
                self.tag_bank.append([tag, "", 0, tag, 0])

    def write(self) -> None:
        try:
            if self.tag_bank != []:
                file = open(self.ouput_file, 'x')
                file.write(json.dumps(self.tag_bank))
                file.close()
        except Exception as ex:
            print("Error when create tag bank file: ", ex)
            