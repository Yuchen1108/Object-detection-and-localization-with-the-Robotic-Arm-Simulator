from vrep import vrep_env
import numpy as np
import random
import math


class SceneObj(vrep_env.VrepEnv):
    """Randomly set scene objects in V-Rep environment."""

    def __init__(self, cid):
        """
        :param cid: Remote V_Rep simulation window's id.
        :type cid: int value.
        """

        vrep_env.VrepEnv.__init__(self, cid=cid)

        self.handle_UR5 = self.get_object_handle('UR5')
        self.handle_camera = self.get_object_handle('Camera')
        self.camera_pos = self.obj_get_position(self.handle_camera, self.handle_UR5)
        self.camera_ori = self.obj_get_orientation(self.handle_camera, self.handle_UR5)

        self.handle_plate = self.get_object_handle('plate')
        self.plate_pos = self.obj_get_position(self.handle_plate)
        self.plate_ori = self.obj_get_orientation(self.handle_plate)

        self.obj_names = ['obj0', 'obj1', 'obj2', 'obj3', 'obj4']
        self.handle_objs = list(map(self.get_object_handle, self.obj_names))

    def init_multi_obj(self):
        """For all objects, set the orientation to the default orientation and move out of the camera."""

        z = -0.15
        for handle in self.handle_objs:
            self.obj_set_position(handle, [0, 0, z])
            self.obj_set_orientation(handle, [0, -np.pi/2, 0])

    def _is_reasonable_distancec(self, x, y, pos_list, threshold=0.04):
        if len(pos_list) == 0:
            return True
        for i in range(len(pos_list)):
            dist = np.linalg.norm(np.array([x, y]) - np.array(pos_list[i]))
            if dist < threshold:
                return False
        return True

    def random_obj(self):
        """Randomly choose objects and randomly set the position and orientation of chosen objects.

        :return: cube_pos, chosen_obj_id

        'cube_pos' is a list, which save the position of the target object (cube).
        'chosen_obj_id' is a list, which save the chosen objects' id.
        """

        cube_pos = []
        chosen_obj_num = random.randint(1, len(self.obj_names))
        chosen_obj_id = random.sample(range(len(self.obj_names)), chosen_obj_num)
        block_id = random.sample(range(9), chosen_obj_num)
        objs_pos = []
        for coid, bid in zip(chosen_obj_id, block_id):
            x, y = self._random_block_pos(bid)
            while self._is_reasonable_distancec(x, y, objs_pos) is False:
                x, y = self._random_block_pos(bid)
            objs_pos.append([x, y])
            self.obj_set_position(self.handle_objs[coid], [x, y, 0], self.handle_plate)
            self._rotate_obj(self.handle_objs[coid], 'z')
            if coid == 0:
                cube_pos = [x, y]
        return cube_pos, chosen_obj_id

    def _random_block_pos(self, block_id):
        """Divide the work area into 9 blocks. Randomly select a location([x, y]) within a block.

        :param block_id: The block's id.
        :type block_id: int value.
        :return: x, y

        `x` is float value for a random position's X-axis coordinate.
        `y` is float value for a random position's Y-axis coordinate.
        """
        blocked_x = [-0.2, -0.07, 0.07, 0.2]
        blocked_y = [-0.2, -0.07, 0.07, 0.2]
        r = int(block_id % 3)
        c = int(block_id / 3)
        x = random.uniform(blocked_x[r], blocked_x[r + 1])
        y = random.uniform(blocked_y[c], blocked_y[c + 1])
        return x, y

    def _rotate_obj(self, handle, axis):
        """Rotating an object around a world coordinate axis.

        :param handle: Handle of the target object in V-Rep.
               axis: Rotary axis.
               input_radian: A given rotation angle.
        :type handle: int value.
              axis: string.
              input_radian: float value.
        :return: radian

        `input_radian` is a float value for rotation angle. `radian` is `None` when there's no specified value.
        `axis` is a string and must be 'x', 'y' or 'z'.
        """

        radian = random.uniform(-math.radians(180), math.radians(180))
        inInts = [handle]
        inFloats = [radian]
        inStrings = [axis]
        emptyBuff = bytearray()
        inData = [inInts, inFloats, inStrings, emptyBuff]
        self.call_childscript_function('RemotePyApi', 'pyObjRotation', inData)
        return radian

    def random_plate(self):
        """Move the plate in V-Rep randomly.
        """

        pos = list(self.plate_pos)
        ori = list(self.plate_ori)
        pos[0] += random.uniform(-0.03, 0.03)
        pos[1] += random.uniform(-0.03, 0.03)
        ori[2] = random.uniform(math.radians(-5), math.radians(5))
        self.obj_set_position(self.handle_plate, pos)
        self.obj_set_orientation(self.handle_plate, ori)

    def random_camera(self):
        """Move the camera in V-Rep randomly.

        :return: pos, ori

        The type of `pos` is list, length=3 for camera's position relative to Viper.
        The type of `ori` is list, length=3 for camera's orientation relative to Viper
        """

        ori = [0, 0, 0]
        pos = [0, 0, 0]
        for i in range(3):
            ori[i] = self.camera_ori[i] + random.uniform(math.radians(-3), math.radians(3))
            pos[i] = self.camera_pos[i] + random.uniform(-0.01, 0.01)
        self.obj_set_orientation(self.handle_camera, ori, self.handle_UR5)
        self.obj_set_position(self.handle_camera, pos, self.handle_UR5)
        return pos, ori