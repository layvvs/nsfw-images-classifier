import tensorflow as tf
from keras.utils import image_dataset_from_directory
import os
import numpy as np
from pathlib import Path


MIN_SIZE = 10000 # 10 kb


class DataPreprocessing:
    def __init__(self, data_dir: Path, image_size: tuple(int), batch_size: int):
        self.data_dir = data_dir
        self.image_size = image_size
        self.batch_size = batch_size


    def preprocess_data(self) -> tuple(tf.data.Dataset):
        self._clean_data()
        raw_data = image_dataset_from_directory(self.data_dir)
        scaled_data = self._scale_data(raw_data)
        splitted_data = self._split_data(scaled_data)
        return splitted_data


    def _clean_data(self) -> None:
        for image_class in os.listdir(self.data_dir):
            for image in os.listdir(self.data_dir/image_class):
                image_path = Path(self.data_dir/image_class/image)
                try:
                    if image_path.stat().st_size <= MIN_SIZE:
                        os.remove(image_path)      
                except Exception as error:
                    print(f'Issue with image {image_path}')    


    def _scale_data(self, data: tf.data.Dataset) -> tf.data.Dataset:
        return data.map(lambda x,y: (x/self.image_size, y))


    def _split_data(self, data: tf.data.Dataset) -> tuple(tf.data.Dataset):
        train_size = int(len(data)*.7)
        val_size = int(len(data)*.2)
        test_size = int(len(data)*.1)

        train_data = data.take(train_size)
        val_data = data.skip(train_size).take(val_size)
        test_data = data.skip(train_size+val_size).take(test_size)

        return (
            train_data,
            val_data,
            test_data
        )
