import requests #meow
import pandas as pd
from enum import Enum

url1 = 'https://www.drugs.com/condition/anesthesia.html'
url2 = 'https://www.drugs.com/condition/anesthesia.html?page_number=2'
url3 = 'https://www.drugs.com/condition/anesthesia.html?page_number=3'
url4 = 'https://www.drugs.com/condition/anesthesia.html?page_number=4'
url5 = 'https://www.drugs.com/condition/anesthesia.html?page_number=5'

total_urls = [url1, url2, url3, url4, url5]

class SectionSeprators (Enum):
    OUTTERSECTIONSEPRATOR = 'condition-table__drug-name valign-middle'
    INNERSECTIONSEPRATOR = 'condition-table__'

class ResultMapper (Enum):
    results_mapper = {'RX' : ('rx-otc', 'drugInfo', '"'),
                     'CSA' : ('csa','drugInfo', '"'),
                     'Pregnancy' : ('pregnancy', 'drugInfo', '"'),
                     'Alcochol' : ('alcohol', 'drugInfo', '"'),
                     '# reviews' : ('rating valign-middle', 'Based on ', ' '),
                     'Rating' : ('rating valign-middle', '"large">\n        ', ' '),
                     'Activity' : ('popularity valign-middle','width:', '%'),
                     'Genric name' : ('generic-name','</b>&nbsp;',' '),
                     'Brand name' : ('brand-names__brand-name', '\n      ','<'),
                     'Drug class' : ('drug-classes', '/drug-class/','.')
                     }

class DrugComScrapper ():
    def __init__ (self, url_addresses_list, outter_section_seprator, inner_section_sperator, results_mapper):
        import requests
        self.url_addresses_list = url_addresses_list
        self.resp_list = [requests.get(url_address) for url_address in self.url_addresses_list]
        self.resp_status_codes = [resp.status_code for resp in self.resp_list]
        self.outter_section_seprator = outter_section_seprator
        self.inner_section_sperator = inner_section_sperator
        self.results_mapper = results_mapper
    
    def print_url_addresses(self):
        for url_address in self.url_addresses_list:
            print(url_address)

    def check_resp_status(self):
        import numpy as np
        if int(np.mean(self.resp_status_codes)) == 200:
            print('All responses were loaded successfully!')

    def get_results_df(self):
        results_list = [self.get_results_from_response(resp) for resp in self.resp_list]
        result_df = pd.concat([pd.DataFrame(result) for result in results_list], ignore_index=True)
        return result_df

    def get_results_from_response(self, resp):
        section_results, current_index =  [], 0
        while resp.text.find(self.outter_section_seprator, current_index) > -1:
            text_section, current_index = self.get_section_from_text(resp.text, current_index) 
            text_section_split_result = text_section.split(self.inner_section_sperator)
            section_results.append(self.analyze_text_section(text_section_split_result))
        return section_results

    def get_section_from_text(self, text, inital_index):
        section_begin_index = text.find(self.outter_section_seprator, inital_index)
        section_end_index = text.find(self.outter_section_seprator, section_begin_index+1)
        text_section = text[section_begin_index:section_end_index]
        return text_section, section_end_index

    def analyze_text_section(self, text):
        result_dic = {}
        for text_line in text:
            result_dic.update({category : self.extract_value(text_line, category, split2, split3) for category, (split1, split2, split3) in self.results_mapper.items() if text_line.startswith(split1)})
        return result_dic

    def extract_value(self, text_line, category, split2, split3):
        if category in ('Pregnancy', 'Alcochol') and text_line.find(split2) == -1:
            return 'None'
        return text_line.split(split2)[1].split(split3)[0]

web_scrapper = DrugComScrapper(url_addresses_list = total_urls,
                               outter_section_seprator = SectionSeprators.OUTTERSECTIONSEPRATOR.value,
                               inner_section_sperator = SectionSeprators.INNERSECTIONSEPRATOR.value,
                               results_mapper = ResultMapper.results_mapper.value)

web_scrapper.get_results_df()
