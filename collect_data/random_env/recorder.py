import datetime
import json
import os
from matplotlib.pyplot import imsave
import uuid


class Recorder(object):
    def __init__(self, save_path):
        self.save_path = save_path
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)

    def add_record(self, record):
        image = record['image']
        step_num = record['step_num']
        camera_ori = record['camera_ori']
        camera_pos = record['camera_pos']
        target_location = record['target_location']

        record_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')+uuid.uuid4().hex
        image_path = os.path.join(self.save_path, record_id+'.jpg')
        json_file = open(os.path.join(self.save_path, record_id+'.json'), 'w')
        record = {'id': record_id, 'image_path': image_path, 'step_num': step_num,
                  'camera_ori': camera_ori, 'camera_pos': camera_pos, 'target_location': target_location}
        json.dump(record, json_file)
        json_file.close()
        imsave(image_path, image)
