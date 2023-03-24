from vrep import vrep_env
import numpy as np
import random


class Light(vrep_env.VrepEnv):
    """Randomly set light in V-Rep environment."""

    def __init__(self, cid):
        """
        :param cid: Remote V_Rep simulation window's id.
        :type cid: int value.
        """

        vrep_env.VrepEnv.__init__(self, cid=cid)

        self.dirlt_num = 4
        self.spotlt_num = 4
        self.omnidirlt_num = 4
        self.original_light = [0.4, 0.4, 0.4, 0.2]

        dirlt_names = []
        spotlt_names = []
        omnidirlt_names = []
        for i in range(self.dirlt_num):
            dirlt_names += ['Directional_light' + str(i)]
        for i in range(self.spotlt_num):
            spotlt_names += ['Spot_light' + str(i)]
        for i in range(self.omnidirlt_num):
            omnidirlt_names += ['Omnidirectional_light' + str(i)]
        self.handle_dirlt = list(map(self.get_object_handle, dirlt_names))
        self.handle_spotlt = list(map(self.get_object_handle, spotlt_names))
        self.handle_omnidirlt = list(map(self.get_object_handle, omnidirlt_names))

    def random_light(self):
        """Set light in V-Rep randomly."""

        self._turnOfflights()
        self._random_lighton()
        self._random_lightpos()
        self._turnOnlights()

    def default_light(self):
        """Restore to default light in V-Rep."""

        self._turnOfflights()
        self._random_lighton()
        self._random_lightpos(original=True)
        self._turnOnlights(original=True)

    def _turnOfflights(self):
        """Turn off all lights in V-Rep."""

        inInts = [0]
        for light in self.handle_dirlt + self.handle_spotlt + self.handle_omnidirlt:
            inInts.append(light)
        inFloats = []
        inStrings = []
        emptyBuff = bytearray()
        inData = [inInts, inFloats, inStrings, emptyBuff]
        self.call_childscript_function('RemotePyApi', 'pySetLights', inData)

    def _turnOnlights(self, original=False):
        """Turn on chosen lights in V-Rep randomly.

        :param original: Use default light in V-Rep or not.
        :type original: bool

        The type of `original` is bool. `original` is `True` when use default light in V-Rep, `False` otherwise.
        """

        # turn on the selected lights
        inInts = [1]
        inFloats = []
        if original:
            inInts += self.handle_dirlt[:4]
            for i in range(3):
                for j in range(3):
                    inFloats.append(self.original_light[i])
            for i in range(3):
                inFloats.append(self.original_light[3])
        else:
            inInts += self.handle_dirlton + self.handle_spotlton + self.handle_omnidirlton
            for i in range(len(inInts)-1):
                for j in range(3):
                    inFloats.append(np.random.uniform(0.0, 1.0))
        inStrings = []
        emptyBuff = bytearray()
        inData = [inInts, inFloats, inStrings, emptyBuff]
        self.call_childscript_function('RemotePyApi', 'pySetLights', inData)

    def _random_lighton(self):
        """Choose lights to turn on randomly."""

        self.handle_dirlton = []
        self.handle_spotlton = []
        self.handle_omnidirlton = []
        for i in range(random.randint(0, self.dirlt_num)):
            self.handle_dirlton.append(self.handle_dirlt[random.randint(0, self.dirlt_num-1)])
        # print('directional light: ', len(self.handle_dirlton))
        for i in range(random.randint(0, self.spotlt_num)):
            self.handle_spotlton.append(self.handle_spotlt[random.randint(0, self.spotlt_num-1)])
        # print('spot light: ', len(self.handle_spotlton))
        for i in range(random.randint(0, self.omnidirlt_num)):
            self.handle_omnidirlton.append(self.handle_omnidirlt[random.randint(0, self.omnidirlt_num-1)])
        # print('omnidirectional light: ', len(self.handle_omnidirlton))

    def _random_lightpos(self, original=False):
        """Set the position and direction of the lights in V-Rep randomly .

        :param original: Use default light position in V-Rep or not.
        :type original: bool

        The type of `original` is bool. `original` is `True` when use default light position in V-Rep, `False` otherwise.
        """

        if original:
            return
        # random orientation for directional lights
        dir_pos = []
        for lt in self.handle_dirlton:
            dirlt_oris = np.random.randint(-180, 180, size=3)
            dir_pos.append(list(dirlt_oris))
            self.obj_set_orientation(lt, dirlt_oris)
        # random position and orientation for spot lights
        spot_pos = []
        for lt in self.handle_spotlton:
            x = y = random.uniform(-2.5, 2.5)
            z = random.uniform(0, 5.0)
            spotlt_oris = np.random.randint(-180, 180, size=3)
            spot_pos.append([[x,y,z], list(spotlt_oris)])
            self.obj_set_orientation(lt, spotlt_oris)
            self.obj_set_position(lt, [x, y, z])
        # random position for omnidirectional lights
        omni_pos = []
        for lt in self.handle_omnidirlton:
            x = y = random.uniform(-2.5, 2.5)
            z = random.uniform(0, 5.0)
            omni_pos.append([x, y, z])
            self.obj_set_position(lt, [x, y, z])
