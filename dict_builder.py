import json
import os
import shutil
from yomitandic import DicEntry, Dictionary

class DictEntry(DicEntry):
    def __init__(self, word, reading, tag="", deinflection="", definition=None, sequence_number=0):
        super().__init__(word, reading, tag, definition)
        self.sequence_number = sequence_number
        self.deinflection = deinflection
        
    def to_list(self):
        if self.structured_content:
            content = [{"type": "structured-content", "content": self.content}]
        else:
            content = self.content
            
        return [
            self.word,
            self.reading,
            self.tag,
            self.deinflection,
            0,
            content,
            self.sequence_number,
            ""
        ]
        
class Dictionary(Dictionary):
    def __init__(self, dictionary_name):
        super().__init__(dictionary_name)
        self.index_json = {}
    
    def set_index(self, index_json = {}):
        if index_json != {}:
            self.index_json = index_json
        else :
            self.index_json = {
                "title": self.dictionary_name,
                "format": 3,
                "revision": "1"
            }
        
    def export(self):
        folder_name = self.dictionary_name
        
        # Remove the existing folder if it already exists
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
        
        os.makedirs(folder_name, exist_ok=True)
            
        index_file = os.path.join(folder_name, "index.json")
        with open(index_file, 'w', encoding='utf-8') as out_file:
            json.dump(self.index_json, out_file, ensure_ascii=False)

        file_counter = 1
        entry_counter = 0
        dictionary = []
    

        for entry in self.entries:
            entry_list = entry.to_list()
            dictionary.append(entry_list)
            entry_counter += 1
           
            if entry_counter >= 10000:
                output_file = os.path.join(folder_name, f"term_bank_{file_counter}.json")
                with open(output_file, 'w', encoding='utf-8') as out_file:
                    json.dump(dictionary, out_file, ensure_ascii=False)
                dictionary = []
                file_counter += 1
                entry_counter = 0

        if dictionary:
            output_file = os.path.join(folder_name, f"term_bank_{file_counter}.json")
            with open(output_file, 'w', encoding='utf-8') as out_file:
                json.dump(dictionary, out_file, ensure_ascii=False)
        

        