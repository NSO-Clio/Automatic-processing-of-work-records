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
