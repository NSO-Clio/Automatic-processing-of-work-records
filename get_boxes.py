import keras_ocr


class GetTextBoxes:
    def __init__(self) -> None:
        self.pipeline = keras_ocr.pipeline.Pipeline()
    
    def get_box(self, img_path: str) -> list:
        image = keras_ocr.tools.read(img_path)
        predictions = self.pipeline.recognize([image])[0]
        return [box for _, box in predictions]
