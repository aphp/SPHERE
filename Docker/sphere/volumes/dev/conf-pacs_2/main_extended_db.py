""" Create file all dicom elements and extended database file"""
# pylint: disable=invalid-name, line-too-long, import-error
import os
import sys
import csv
import json
import subprocess
from urllib.request import urlopen

import ruamel.yaml
# pylint: disable=no-name-in-module,
from settings import LOG_EXTENDED, load_config_file

# http://www.dimitripianeta.fr/documents/traitements/Lexiques%20DICOM%20(fr).pdf
# https://northstar-www.dartmouth.edu/doc/idl/html_6.2/Value_Representations.html
# http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_6.2.html
# http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
# https://pydicom.github.io/pydicom/stable/guides/element_value_types.html
SIZE_VR = {
    "AE": 128,  # String (16 bytes maximum)
    "AS": 32,  # String (4 bytes maximum)
    "AT": 32,  # Ulong (4 bytes fixed)
    "CS": 128,  # String (4 bytes maximum)
    "DA": 64,  # String (4 bytes fixed)
    "DL": 64,  #jjj
    "DS": 128,  # String (16 bytes maximum)
    "DT": 208,  # String (26 bytes maximum)
    "FL": 32,  # Float (4 bytes fixed)
    "FD": 64,  # Double (8 bytes fixed)
    "IS": 96,  # String (12 bytes maximum)
    "LO": 512,  # String (64 chars maximum)
    "LT": 'Text',  # String (10240 chars maximum)
    "OB": 64,  # Byte (See Transfer Syntax definition)
    "OD": 64,  # 2 32 -8 bytes maximum
    "OF": 128,  # Float (2 32-4 maximum) not sure ?
    "OL": 64,  # equal OB
    "OV": 64,  # see Transfer Syntax definition
    "OW": 64,  # Int (See Transfer Syntax definition)
    "PN": 512,  # String (64 chars maximum)
    "SH": 128,  # String (16 chars maximum)
    "SL": 32,  # Long (4 bytes fixed)
    "SQ": 128,  # Long (Not applicable) not sure ?
    "SS": 16,  # Int (2 bytes fixed)
    "ST": 'Text',  # String (1024 chars maximum)
    "TM": 128,  # String (16 bytes maximum)
    "UC": 64,  # Equal OB
    "UI": 512,  # String (64 bytes maximum)
    "UL": 32,  # Ulong (4 bytes fixed)
    "UN": 64,  # Byte (Any length valid for any of the other DICOM VRs )
    "UR": 64,  # Equal OB
    "US": 16,  # Uint (2 bytes fixed)
    "UT": 'Text',  # String (2 32 -2 Note - Limited only by the size of the maximum unsigned integer representable in a 32 bit VL field minus one, since)

}

DICT_TAG_COVID = {
    'patient': ['00101020', '00101030', '00101010'],
    'study': ['00080030', '00101010', '00101020', '00101030', '00101022'],
    'series': ['00080031', '00180010', '00200011', '00280002', '00280004',
               '00280103'],
    'instance': ["00080008", "00200012", '00200013', '00200032', '00201002',
                 '00280010', '00280011', '00280030', '00280101', '00281103',
                 '00281053', '00281054', '00180050', '00189361', '00201041',
                 '00281040', '00200037', '00281052', '00281041', '00181063',
                 '00181065', '00280008', '00280014', '00281101', '00281102']
}


DICT_TAG_CLARITI = {
    'patient': ['00101020', '00101030'],
    'study': ['00080030'],
    'series': ['00080031', '00185100', '00541321'],
    'instance': ['00080022', '00080023', '00080024', '00080025', '00080032',
                 '00080033', '00180050', '00181210', '00200032', '00200037',
                 '00201041', '00280004', '00280030', '00280051', '00280106',
                 '00280107', '00281050', '00281051', '00281052', '00281053',
                 '00281054', '00540081', '00180031', '00181072', '00181074',
                 '00181075', '00181078', '00541001', '00541002', '00541101']
}

DICT_TAG_EXTENDED = {
    'patient': ['00101020', '00101030'],
    'study': ['00200010', '00080030', '00080061'],

    'series': ['00189073', '00180020', '00321060', '00181316', '00180010',
               '00181040', '00180084', '00180023', '00180025', '00180050',
               '00180080', '00180081', '00180082', '00180083', '00180084',
               '00180085', '00180086', '00180087', '00180088', '00180089',
               '00180090', '00180091', '00180093', '00180094', '00180095',
               '00181100', '00181310', '00181312', '00181314'],
    'instance': ['00201041', '00200032', '00200037', '00280008', '00280010',
                 '00280011', '00280030', '00540080', '00540081']
}

# tags not exists in list of website:  [tag, attribute_name, keyword, VR]
# example of list:
# ["00101022", "Patient's Body Mass Index", "PatientBodyMassIndex", "DS"]

LIST_TAG = [
]

# The names of the fields to be used in the database
LIST_NAME_USED_DATABASE = [
    'patient_id', 'study_id', 'series_id', 'instance_id', 'storage_status',
    'file_storage_metadata_dicom_id', 'storage_method', 'file_path', 'filesize',
    'd8ins', 'd8maj', 'd8del']


class AllDicomElementsInCsv:
    """ Create file csv  of all dicom elements """
    def __init__(self, list_website, csv_file_name, column_names):
        self.list_website = list_website
        self.csv_file_name = csv_file_name
        self.column_names = column_names
        self.list_all_dicom_elements = []
        self.list_all_line_csv = []

    def all_dicom_elements(self):
        """ list of All DICOM elements """
        for website in self.list_website:
            with urlopen(website) as response:
                webpage = response.read()
                soup = BeautifulSoup(webpage, 'html.parser')
                tbody = soup.find('tbody')
                for row in tbody.findAll("tr"):
                    tag_keyword_att = []  # list tag, keyword, attribute Name and VR
                    cells = row.findAll("td")
                    for td in cells[:4]:
                        if td.find("span"):
                            value = td.find('span').contents
                        else:
                            value = td.find('p').contents
                        if value:
                            tag_keyword_att.append(value[-1])
                        else:
                            LOG_EXTENDED.warning("No name of this tag %s. I "
                                                 "will not add it to the file",
                                                 tag_keyword_att[0])
                            tag_keyword_att = []
                            break
                    if tag_keyword_att:
                        self.list_all_dicom_elements.append(tag_keyword_att)

        self.list_all_dicom_elements = self.list_all_dicom_elements + LIST_TAG

    def create_field_name(self, attribute_name, list_dicom_elements):
        """
        Create field name of table

        :param attribute_name: Attribute name
        :type attribute_name: str
        :param list_dicom_elements: list of dicom elements
        :type list_dicom_elements: list
        :return: Return name of champs
        :rtype: str
        """
        field_name = attribute_name.lower().replace('(s)', 's')
        for ch in ['/', "'", ',', '(', ')', '&', '-', 'µ']:
            if ch in field_name:
                field_name = field_name.replace(ch, ' ')

        field_name = '_'.join(field_name.split())
        field_name = field_name.replace("2d", "tow_d").replace("3d", "three_d")
        if field_name in LIST_NAME_USED_DATABASE:
            list_word = field_name.split('_')
            list_word.insert(1, "dcm")
            new_field_name = "_".join(list_word)
            LOG_EXTENDED.info("New field_name = '%s' because the "
                              "name '%s' of the field to use in the "
                              "database", new_field_name, field_name)
            field_name = new_field_name
        if field_name and field_name in [li[4] for li in
                                           self.list_all_line_csv]:
            LOG_EXTENDED.warning("This  name '%s' exists. "
                                 "list_dicom_elements = %s",
                                 field_name, list_dicom_elements)
        return field_name

    def create_all_line_csv(self):
        """ Create all line of csv file """
        self.all_dicom_elements()
        for list_dicom_elements in self.list_all_dicom_elements:
            list_elements = []
            tag = list_dicom_elements[0]
            attribute_name = list_dicom_elements[1].replace('\u200b', '').replace('\n', '')
            keyword = list_dicom_elements[2].replace('\u200b', '').replace('\n', '')
            vr = list_dicom_elements[3].replace('\n', '')

            if tag[0] == '(' and tag[5] == ',' and tag[10] == ')':  # ex: (0018,9361)
                tag = tag.replace('(', '').replace(')', '').replace(',', '')
                list_elements.append(tag)
            else:
                list_elements.append(tag)
            list_elements.append(keyword)
            list_elements.append(attribute_name)
            list_elements.append(vr)
            try:
                field_name = self.create_field_name(attribute_name, list_dicom_elements)

                list_elements.append(field_name)

                # For example if vr ='OB or OW'; vr = 'OB' et not 'OW'
                if "or" in vr and vr not in SIZE_VR:
                    vr = vr[:2]
                elif vr not in SIZE_VR:
                    if vr:
                        LOG_EXTENDED.warning("This VR '%s' not exists in "
                                             "list VR", vr)
                    else:
                        LOG_EXTENDED.warning("VR does not exist in this tag "
                                             "'%s'", tag)
                if vr in SIZE_VR:
                    if isinstance(SIZE_VR[vr], int):
                        list_elements = list_elements + ["String", SIZE_VR[vr]]
                    elif SIZE_VR[vr] == "Text":
                        list_elements.append(SIZE_VR[vr])
                    else:
                        print('We must add this VR in SIZE_VR')
                else:
                    LOG_EXTENDED.warning("No value representations of this "
                                         "tag %s. I will not add the line it "
                                         "to the file", tag)
                    list_elements = []
                if list_elements:
                    self.list_all_line_csv.append(list_elements)
            except Exception as exc:
                LOG_EXTENDED.exception(exc)
                LOG_EXTENDED.error("There is a problem with this listing %s",
                                   list_elements)
            # list_all_line_csv.append(list_elements)
        LOG_EXTENDED.debug("We have %s tags ", len(self.list_all_line_csv))
        return self.list_all_line_csv

    def create_file_csv(self):
        """ Create file csv"""
        self.create_all_line_csv()
        with open(self.csv_file_name, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(self.column_names)
            for i in self.list_all_line_csv:
                writer.writerow(i)


class ExtendedDb:
    """ Create file extended_db"""
    def __init__(self, path_file, yaml_file_name, dict_tag):
        self.path_file = path_file
        self.yaml_file_name = yaml_file_name
        self.dict_tag = dict_tag
        self.dict_all_dicom_elements = {}
        self.json_extended_db = {}

    def read_file_csv(self):
        """ Read file csv and add result in dict_all_dicom_elements"""
        with open(self.path_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.dict_all_dicom_elements[row[0]] = row[1:]

    def add_in_dic(self, dic_parm_tag, tag_child, parent_tags_list=None):
        """
        create dict of parents, keyword, value_representations,
        field_name, type and size

        :param dic_parm_tag: Children of the tag
        :type dic_parm_tag: dict
        :param tag_child: The tag child
        :type tag_child: str
        :param parent_tags_list: The parent tags list
        :type parent_tags_list: list[str]
        """
        keyword = self.dict_all_dicom_elements[tag_child][0]
        value_representations = self.dict_all_dicom_elements[tag_child][2]
        field_name = self.dict_all_dicom_elements[tag_child][3]
        type_value = self.dict_all_dicom_elements[tag_child][4]
        if value_representations == "SQ":
            LOG_EXTENDED.error(
                "We will not add this attribute '%s' because we "
                "are not processing the  value representations"
                " 'SQ'", keyword)
        else:
            if len(self.dict_all_dicom_elements[tag_child]) == 6:
                size_max = self.dict_all_dicom_elements[tag_child][5]
                dict_child = {
                    "keyword": keyword,
                    "value_representations": value_representations,
                    "field_name": field_name,
                    "type": type_value,
                    "size": int(size_max)
                }
            else:
                dict_child = {
                    "keyword": keyword,
                    "value_representations": value_representations,
                    "field_name": field_name,
                    "type": type_value
                }
            if parent_tags_list:  # If parent tag exists
                dict_parents = {"parents": ','.join(parent_tags_list)}
                dic_parm_tag[tag_child] = {**dict_parents, **dict_child}
            else:
                dic_parm_tag[tag_child] = dict_child

    def create_json_extended_db(self):
        """ Create the data from the cvs file in json format."""
        self.read_file_csv()
        for model in self.dict_tag.keys():
            list_tags = self.dict_tag[model]
            dic_parm_tag = {}
            for tag in list_tags:
                tag = str(tag)
                if tag in self.dict_all_dicom_elements:
                    self.add_in_dic(dic_parm_tag, tag)
                elif ',' in tag:  # parents and child separate by comma Ex: tag = '00409096,00409224'
                    tags_list = tag.split(',')
                    parent_tags_list = tags_list[:-1]
                    tag_child = tags_list[-1]
                    self.add_in_dic(dic_parm_tag, tag_child, parent_tags_list)

                else:
                    LOG_EXTENDED.error("This tag '%s' does not exist in file "
                                       "'%s' so add it manually in the "
                                       "part'%s'", tag, self.path_file, model)

            self.json_extended_db[model] = dic_parm_tag

    def json_to_yaml(self):
        """ Json to Yaml"""
        self.create_json_extended_db()
        yes_no_mo = ''
        if os.path.exists(self.yaml_file_name):
            while yes_no_mo not in ["yes", 'no']:
                yes_no_mo = input("Are you sure you want to modified the old "
                                  "file '{}' 'yes' or 'no':".format(
                                      self.yaml_file_name))
        if yes_no_mo in ['', 'yes']:
            # to keep the order when creating the yaml file
            yaml = ruamel.yaml.YAML()
            yaml.indent(mapping=4, sequence=4, offset=2)

            with open(self.yaml_file_name, 'w') as file:
                _documents = yaml.dump(self.json_extended_db, file)
            if yes_no_mo == "yes":
                print("The '{}' file is modified".format(self.yaml_file_name))
            else:
                print("You created a new file '{}'".format(self.yaml_file_name))
        else:
            print("The file '{}' is not modified ".format(self.yaml_file_name))

    def create_file_json(self, path_copy_extended):
        """
        Create file json

        :param path_copy_extended: Path of copy extended
        :type path_copy_extended: str
        """
        try:
            with open(path_copy_extended, 'w') as f:
                json.dump(self.json_extended_db, f)
        except Exception as exc:
            print("I did not create the copy_extended_db file. \n {}".format(exc))


if __name__ == '__main__':
    BASE_DIR = (os.path.dirname(os.path.abspath(__file__)))
    CSV_FILE_NAME = os.path.join(BASE_DIR, 'all_dicom_elements.csv')
    if os.path.exists(CSV_FILE_NAME):
        yes_no = input("Do you want to overwrite the file '{}' "
                       "'yes' or 'no':".format(CSV_FILE_NAME))
        while yes_no not in ["yes", 'no']:
            yes_no = input("You have to type 'yes' or 'no':")
    else:
        yes_no = 'yes'
    if yes_no == 'yes':
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", 'beautifulsoup4'])
        finally:
            from bs4 import BeautifulSoup
        # Registry of DICOM Data Elements
        URL_DATA_ELEMENTS = "http://dicom.nema.org/medical/dicom/current/output/chtml/part06/chapter_6.html"
        # Registry of DICOM File Meta Elements
        URL_FILE_META_ELEMENTS = "http://dicom.nema.org/dicom/2013/output/chtml/part06/chapter_7.html"
        # Registry of DICOM Directory Structuring Elements
        URL_DIRECTORY_ELEMENTS = "http://dicom.nema.org/dicom/2013/output/chtml/part06/chapter_8.html"
        LIST_WEBSITE = [URL_FILE_META_ELEMENTS, URL_DIRECTORY_ELEMENTS, URL_DATA_ELEMENTS]

        #CSV_FILE_NAME = 'all_dicom_elements.csv'
        COLUMN_NAMES = ["Tag", "Keyword", "Attribute name", "VR",
                        "Field name of a table", "Type", "Size if settings"]

        all_dicom_elements_in_csv = AllDicomElementsInCsv(LIST_WEBSITE,
                                                          CSV_FILE_NAME,
                                                          COLUMN_NAMES)
        all_dicom_elements_in_csv.create_file_csv()

        # uninstall beautifulsoup4
        subprocess.check_call(
            [sys.executable, "-m", "pip", "uninstall", 'beautifulsoup4', '-y'])

    EXTENDED_FILE_NAME = os.path.join(BASE_DIR, "extended_db.yml")
    TAGS_FILE_NAME = os.path.join(BASE_DIR, "tags.yml")
    PATH_COPY_EXTENDED = os.path.join(BASE_DIR, '.copy_extended.json')
    dict_tag_extended = load_config_file(TAGS_FILE_NAME)
    if dict_tag_extended:
        extended_db = ExtendedDb(CSV_FILE_NAME, EXTENDED_FILE_NAME, dict_tag_extended)
        extended_db.json_to_yaml()
        extended_db.create_file_json(PATH_COPY_EXTENDED)
    else:
        LOG_EXTENDED.warning("This file '%s' is empty so I will not create "
                             "the empty 'extended_db.yml' file", TAGS_FILE_NAME)
