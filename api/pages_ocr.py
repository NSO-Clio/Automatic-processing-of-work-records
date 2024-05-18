import cv2
from shiftlab_ocr.doc2text.reader import Reader


class Ocr_of_secondary_pages:
    def __init__(self) -> None:
        self.ocr_reader = Reader()

    @staticmethod
    def calculate_y_distances(boxes: list, y_max: float, flag: bool = False) -> list:
        distances = []
        for i in range(len(boxes) - 1):
            box1_top_y = boxes[i][0][1]
            box1_bottom_y = boxes[i][1][1]
            box2_top_y = boxes[i + 1][0][1]
            box2_bottom_y = boxes[i + 1][1][1]
            if box1_bottom_y < box2_top_y:
                distance = box2_top_y - box1_bottom_y
            elif box2_bottom_y < box1_top_y:
                distance = box1_top_y - box2_bottom_y
            else:
                distance = 0
            if distance > 0:
                distances.append((box1_top_y, box2_top_y))
            if flag and distance == 0:
                distances.append((0, 0))
        distances.append((boxes[-1][0][1], y_max))
        return distances

    @staticmethod
    def remove_duplicates(input_list: list) -> list:
        seen = set()
        result = []
        for item in input_list:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    def get_data(self, img_path: str) -> dict:
        img = cv2.resize(cv2.imread(img_path), (2232, 1652))
        cv2.imwrite('elem.jpg', img[int(1652 * 0.26):, int(2232 * 0.086):int(2232 * 0.24)])
        result = self.ocr_reader.doc2text("elem.jpg")
        data = {
            'data': [],
            'work': [],
            'job_title': [],
            'description': []
        }
        images = result[1]
        print(result[0])
        dt = result[0].split()
        dt_box, text_dt = [], {}
        k = 0
        for i in range(len(images) - 1):
            if dt[i].replace('.', '').replace(')', '').isdigit():
                dt_box.append(images[i].points)
                if self.calculate_y_distances(
                        [images[i].points, images[i + 1].points],
                        img[int(1652 * 0.26):, :].shape[0],
                        flag=True
                )[0][0] == 0:
                    if k not in text_dt:
                        text_dt[k] = [dt[i], dt[i + 1]]
                    else:
                        text_dt[k].append(dt[i])
                        text_dt[k].append(dt[i + 1])
                else:
                    k += 1
        print(text_dt)
        text_dt = [' '.join(self.remove_duplicates(text_dt[i])) for i in text_dt]
        print(text_dt)
        print(self.calculate_y_distances(dt_box, img[int(1652 * 0.26):, :].shape[0]))

        for i, elem in enumerate(self.calculate_y_distances(dt_box, img[int(1652 * 0.26):, :].shape[0])):
            img_tmp = img[int(1652 * 0.26):, :]
            img_tmp = img_tmp[int(round(elem[0])):int(round(elem[1])), :]
            print(int(round(elem[0])), int(round(elem[1])), '-----')
            col_1, col_2 = (img_tmp[:, int(2232 * 0.22):int(2232 * 0.8)],
                            img_tmp[:, int(2232 * 0.8):])
            cv2.imwrite(f'col_{i}.jpg', col_1)
            cv2.imwrite('col__2.jpg', col_2)
            result_1, result_2 = (self.ocr_reader.doc2text(f'col_{i}.jpg'),
                                  self.ocr_reader.doc2text("col__2.jpg"))
            data['data'].append(text_dt[i] if len(text_dt) > i else "notFound")
            data['job_title'].append(
                result_1[0].lower().split('на должность')[-1].strip() if 'на должность' in result_1[0].lower()
                else "notFound")
            data['work'].append(result_1[0])
            data['description'].append(result_2[0])
        return data