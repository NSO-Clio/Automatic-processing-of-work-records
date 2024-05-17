import keras_ocr


class GetTextBoxes:
    def __init__(self) -> None:
        """
        Инициализирует объект GetTextBoxes, создавая экземпляр конвейера для распознавания текста.
        """
        self.pipeline = keras_ocr.pipeline.Pipeline()
    
    def get_box(self, img_path: str) -> list:
        """
        Возвращает список текстовых областей (bounding boxes) для текста, найденного на изображении.

        Параметры:
        img_path (str): Путь к изображению, на котором нужно распознать текст.

        Возвращает:
        list: Список координат областей, содержащих текст.
        """
        image = keras_ocr.tools.read(img_path)  # Чтение изображения с указанного пути
        predictions = self.pipeline.recognize([image])[0]  # Распознавание текста на изображении
        return [box for _, box in predictions]  # Возврат списка координат текстовых областей

    def crop_rectangle(self, image: np.ndarray, box: np.ndarray) -> np.ndarray:
        """
        Вырезает прямоугольник из изображения по координатам четырех углов.

        Параметры:
        image (np.ndarray): Изображение, из которого нужно вырезать прямоугольник.
        box (np.ndarray): Массив координат четырех углов прямоугольника.

        Возвращает:
        np.ndarray: Вырезанный прямоугольник.
        """
        # Находим размер вырезаемого прямоугольника
        width = int(np.linalg.norm(box[0] - box[1]))
        height = int(np.linalg.norm(box[1] - box[2]))

        # Определяем целевые точки (прямоугольник с найденными размерами)
        dst_pts = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype="float32")

        # Вычисляем матрицу перспективного преобразования
        M = cv2.getPerspectiveTransform(box.astype("float32"), dst_pts)

        # Применяем преобразование и вырезаем прямоугольник
        cropped_image = cv2.warpPerspective(image, M, (width, height))

        return cropped_image
