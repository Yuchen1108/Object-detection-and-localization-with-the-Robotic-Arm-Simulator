from vrep import vrep_env
import random
import os
from collect_data.random_env.random_objects import SceneObj
from collect_data.random_env.random_light import Light
from collect_data.random_env.random_texture import Texture
from collect_data.random_env.recorder import Recorder


class RandomEnv(vrep_env.VrepEnv):
    """Randomly change the environment in V-Rep, then collect image and data."""

    def __init__(self,
                 server_addr='127.0.0.1',
                 server_port=19997,
                 scene_directory=None,
                 scene_file=None,
                 texture_directory=None,
                 texture_num=125,
                 version=0):
        """

        :param server_addr: Address which is used to connect python and V-Rep.
        :param server_port: Port which is used to connect python and V-Rep.
        :param scene_directory: Path of the `.ttt` files.
        :param scene_file: Scene file of the task.
        :param texture_directory: Path of the texture files.
        :param texture_num: Amount of the texture files.
        :param version: A int value for a version mark.
        """

        assert scene_directory, 'scene directoy must be provided'
        scene_path = os.path.join(scene_directory, scene_file)
        scene_path = os.path.abspath(scene_path)
        print('loading scene from {}'.format(scene_path))
        vrep_env.VrepEnv.__init__(self, server_addr, server_port, scene_path)

        self._scene_obj = SceneObj(self.cid)
        self._light = Light(self.cid)
        self._texture = Texture(self.cid, texture_directory, texture_num)

        self.handle_vision = self.get_object_handle('Camera')

        self.recorder = Recorder('random_dataset_V' + str(version))

        self.step_num = 0
        self.target_pos = []

        self.camera_pos = []
        self.camera_ori = []
        self.image = None

    def _multi_step(self, nstep=5):
        """Simulate every once in a while in V-Rep.

        :param nstep: The time interval.
        :type nstep: int value.

        `nstep` is int value for the time interval between two simulations in V-rep.
        """

        for i in range(nstep):
            self.step_simulation()

    def run(self):
        """Run the collecting program. Domain randomization and collecting process."""

        self.step_num += 1
        self.camera_pos, self.camera_ori = self._scene_obj.random_camera()
        self._scene_obj.random_plate()
        self._light.random_light()

        self._scene_obj.init_multi_obj()
        self.target_pos, chosen_obj_id = self._scene_obj.random_obj()

        self._texture.random_texture(['plate', 'plane', 'table', 'tar_objs'], tar_objs_id=chosen_obj_id)
        self._texture.delete_texture()

        self.image = self.obj_get_vision_image(self.handle_vision)
        self._recoder()

    def reset(self):
        """Reset V-Rep"""

        if self.sim_running:
            self.stop_simulation()
        self.start_simulation()
        self.step_num = 0
        self._multi_step()

    def seed(self, seed=None):
        """Random seed.

        :param seed: Random seed.
        :type seed: int value.
        """

        random.seed()

    def _recoder(self):
        """Record data to make tf-record."""

        record = {'step_num': self.step_num, 'image': self.image, 'camera_ori': self.camera_ori,
                  'camera_pos': self.camera_pos, 'target_location': self.target_pos}
        self.recorder.add_record(record)
