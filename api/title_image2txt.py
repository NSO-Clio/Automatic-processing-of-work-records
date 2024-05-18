from pymystem3 import Mystem
import re
from shiftlab_ocr.doc2text.reader import Reader
import cv2
from PIL import Image
import pytesseract
import os
import warnings
warnings.simplefilter('ignore')


class TitleInformation:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.reader = Reader()
    
    def get_texts(self, img_path, se=15):
        img = cv2.imread(img_path)
        c = len(img) // se
        pt = 10
        tekst_ruk = []
        tekst_peh = []
        for i in range(len(img) // c):
            if i > 0 and i < len(img) // c:
                st = i * c - pt
                en = (i + 1) * c + pt
            else:
                st = i * c
                en = (i + 1) * c
            part = img[st: en]
            tru = pytesseract.image_to_string(part, lang='rus')
            tekst_peh.append(tru)
            src = r'temp/1.jpg'
            Image.fromarray(part).save(src)
            trk = self.reader.doc2text(src)[0] 
            tekst_ruk.append(trk)
        return tekst_ruk, tekst_peh

    @staticmethod
    def find_FIO(text):
        m = Mystem()
        second_name = first_name = middle_name = None
        analyse = m.analyze(text)
        for word in analyse:
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
    def is_month(txt):
        mnths = ['январ', 'феврал', 'март', 'апрел', 'май', 'мая', 'июн', 'июл', 'август', 'сентябр', 'октябр', 'ноябр', 'декабр']
        for m in mnths:
            if m in txt:
                return m
        return False

    @staticmethod
    def just_year(txt):
        pattern = r'\b\d{4}г'
        matches = re.findall(pattern, txt)
        return matches

    def get_dates(self, txt):
        dates = []
        for x in txt:
            rt = self.is_month(x)
            dt = self.extract_date(x)
            je = self.just_year(x)
            if dt:
                dates.extend(dt)
            elif rt:
                i = 0
                sp = x.split()
                for p, o in enumerate(sp):
                    if rt in o:
                        i = p
                dates.append(' '.join(sp[i - 1 if i - 1 >= 0 else i: i + 2]))
            elif je:
                dates.extend(je)
        return dates
    
    @staticmethod
    def get_numer_series(img_path):
        series = ['AT-VIII', 'AT-VII', 'AT-VI', 'AT-IV', 'AT-V', 'AT-III', 'AT-II', 'AT-I', 'AT-IX', 'AT-X', 'TK-III', 'TK-II', 'TK-I', 'TK']
        img = cv2.imread(img_path)
        txt = pytesseract.image_to_string(Image.fromarray(img[:img.shape[0] // 5, img.shape[1] // 2:]))
        final_ser = None
        for ser in series:
            if ser in txt:
                final_ser = ser
        num = None
        if ''.join(list(filter(str.isdigit, list(txt)))):
            num = ''.join(list(filter(str.isdigit, list(txt))))
        return num, final_ser
    
    @staticmethod
    def get_graduate(txt):
        obrz = ['высшее', 'среднее', 'начальное']
        for x in txt.split():
            for ob in obrz:
                if ob in x:
                    return x
        return 'Не определено'

    def get_information(self, img_path, u=15):
        tekst_ruk, tekst_peh = self.get_texts(img_path, u)
        tekst_peh = list(map(str.strip, tekst_peh))
        tekst_ruk = list(map(str.strip, tekst_ruk))
        txt_ruk = ' '.join(tekst_ruk)
        txt_peh = ' '.join(tekst_peh)
        fio = self.find_FIO(txt_ruk)
        dates = self.get_dates(tekst_ruk)
        brn = None
        data = None
        if dates:
            brn = dates[0]
        if len(dates) > 1:
            data = dates[-1]
        num, ser = self.get_numer_series(img_path)
        grad = self.get_graduate(txt_ruk + txt_peh)
        dct = {'Фамилия': fio[0], 'Имя': fio[1], 'Отчество': fio[2], 'Дата рождения': brn, 'Дата заполнения': data, 'Серия': ser, 'Номер': num, 'Образование': grad}
        return dct, all(dct.values())
    
    def get_full_info(self, img_path):
        past_info = None
        c_lst = [15, 17, 14]
        for i in c_lst:
            info, flag = self.get_information(img_path, i)
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
