from typing import Dict, List, Sequence
import numpy as np
import json
import onnxruntime as rt
from pydantic import BaseModel
from src.configurations import ModelConfigurations
from src.ml.data import Data
from logging import getLogger

logger = getLogger(__name__)


class Classifier(object):
    def __init__(
        self,
        model_filepath: str,
        label_filepath: str,
    ):
        self.model_filepath: str = model_filepath
        self.label_filepath: str = label_filepath
        self.classifier = None
        self.label: Dict[str, str] = {}
        self.input_name: str = ""
        self.output_name: str = ""

        self.load_model()
        self.load_label()

    def load_model(self):
        logger.info(f"load model in {self.model_filepath}")
        self.classifier = rt.InferenceSession(self.model_filepath)
        self.input_name = self.classifier.get_inputs()[0].name
        self.output_name = self.classifier.get_outputs()[0].name
        logger.info(f"initialized model")

    def load_label(self):
        logger.info(f"load label in {self.label_filepath}")
        with open(self.label_filepath, "r") as f:
            self.label = json.load(f)
        logger.info(f"label: {self.label}")

    async def predict(self, data: List[List[int]]) -> np.ndarray:
        np_data = np.array(data).astype(np.float32)
        prediction = self.classifier.run(None, {self.input_name: np_data})
        output = np.array(list(prediction[1][0].values()))
        logger.info(f"predict proba {output}")
        return output

    async def predict_label(self, data: List[List[int]]) -> str:
        prediction = await self.predict(data=data)
        argmax = int(np.argmax(np.array(prediction)[0]))
        return self.label[str(argmax)]


classifier = Classifier(
    model_filepath=ModelConfigurations().model_filepath,
    label_filepath=ModelConfigurations().label_filepath,
)
