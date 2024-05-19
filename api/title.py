import pytesseract
from shiftlab_ocr.doc2text.reader import Reader
from pymystem3 import Mystem

import re
import cv2
from PIL import Image

from os import sep
import warnings


class TitleInformation:
    def __init__(self):
        warnings.simplefilter('ignore')
        pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        self.reader = Reader()

    def get_texts(self, img_path, val=15):
        img = cv2.imread(img_path)
        cnt = len(img) // val
        handwrtn_text = []
        printed_text = []
        for i in range(len(img) // cnt):
            if i == 0:
                start = i * cnt
                end = (i + 1) * cnt
            else:
                start = i * cnt - 10
                end = (i + 1) * cnt + 10
            part = img[start:end]
            printed_text.append(pytesseract.image_to_string(part, lang='rus'))
            Image.fromarray(part).save(fr'temp{sep}1.jpg')
            handwrtn_text.append(self.reader.doc2text(fr'temp{sep}1.jpg')[0])
        return handwrtn_text, printed_text

    @staticmethod
    def find_fio(text):
        mystem = Mystem()
        second_name, first_name, middle_name = None, None, None
        analyze = mystem.analyze(text)
        for word in analyze:
            try:
                analysis = word['analysis'][0]
            except:
                continue
            if 'имя' in analysis['gr']:
                first_name = word['text'].capitalize()
            elif 'фам' in analysis['gr']:
                second_name = word['text'].capitalize()
            elif 'отч' in analysis['gr']:
                middle_name = word['text'].capitalize()
        return second_name, first_name, middle_name

    @staticmethod
    def extract_date(text):
        text_new = ''.join(list(filter(lambda x: x != 'г', list(text))))
        date_pattern = re.compile(r'\b(?:\d{1,4}[-/.]\d{1,2}[-/.]\d{2,4}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\b')
        dates = re.findall(date_pattern, text_new)
        return dates

    @staticmethod
    def is_month(text):
        months = ['январ', 'феврал', 'март', 'апрел', 'май', 'мая', 'июн', 'июл', 'август', 'сентябр', 'октябр',
                  'ноябр', 'декабр']
        for month in months:
            if month in text:
                return month
        return False

    @staticmethod
    def check_year(text):
        return re.findall(r'\b\d{4}г', text)

    def get_dates(self, text):
        dates = []
        for word in text:
            rt = self.is_month(word)
            dt = self.extract_date(word)
            je = self.check_year(word)
            if dt:
                dates.extend(dt)
            elif rt:
                i = 0
                sp = word.split()
                for p, o in enumerate(sp):
                    if rt in o:
                        i = p
                dates.append(' '.join(sp[i - 1 if i - 1 >= 0 else i: i + 2]))
            elif je:
                dates.extend(je)
        return dates

    @staticmethod
    def get_numer_series(img_path):
        series = ['AT-VIII', 'AT-VII', 'AT-VI', 'AT-IV', 'AT-V', 'AT-III', 'AT-II', 'AT-I', 'AT-IX', 'AT-X', 'TK-III',
                  'TK-II', 'TK-I', 'TK']
        img = cv2.imread(img_path)
        text = pytesseract.image_to_string(Image.fromarray(img[:img.shape[0] // 5, img.shape[1] // 2:]))
        final_ser = None
        for ser in series:
            if ser in text:
                final_ser = ser
        num = None
        if ''.join(list(filter(str.isdigit, list(text)))):
            num = ''.join(list(filter(str.isdigit, list(text))))
        return num, final_ser

    @staticmethod
    def get_education(text):
        eds = ['высшее', 'среднее', 'начальное']
        for word in text.split():
            for ed in eds:
                if ed in word:
                    return word
        return 'не определено'

    def get_information(self, img_path, val=15):
        handwrtn_text, printed_text = self.get_texts(img_path, val=val)
        handwrtn_text = list(map(str.strip, handwrtn_text))
        printed_text = list(map(str.strip, printed_text))
        handwrtn_txt = ' '.join(handwrtn_text)
        printed_txt = ' '.join(printed_text)
        fio = self.find_fio(handwrtn_txt)
        dates = self.get_dates(handwrtn_text)
        birthday = None
        fill_date = None
        if dates:
            birthday = dates[0]
        if len(dates) > 1:
            fill_date = dates[-1]
        num, ser = self.get_numer_series(img_path)
        education = self.get_education(handwrtn_txt + printed_txt)
        dct = {'service_record_series': ser, 'service_record_number': num, 'last_name': fio[0], 'first_name': fio[1],
               'middle_name': fio[2], 'education': education, 'birthday': birthday, 'fill_date': fill_date}
        return dct, all(dct.values())

    def get_full_info(self, img_path):
        past_info = None
        val_lst = [15, 17, 14]
        for v in val_lst:
            info, flag = self.get_information(img_path, val=v)
            if flag:
                past_info = info.copy()
                break
            if past_info is None:
                past_info = info.copy()
                continue
            for x, y in past_info.items():
                if y is None and info[x]:
                    past_info[x] = info[x]
        return past_info
