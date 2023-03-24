from vrep import vrep_env
import numpy as np
import random
import os


class Texture(vrep_env.VrepEnv):
    """Randomly set texture in V-Rep environment."""

    def __init__(self, cid,
                 texture_directory=None,
                 texture_num=None):

        """
        :param cid: Remote V_Rep simulation window's id.
        :type cid: int value.
        """

        vrep_env.VrepEnv.__init__(self, cid=cid)

        self.original_color = [0, 0, 0]
        self.texture_num = texture_num
        self.resolution = [256, 256]
        self.texture_path = []
        for i in range(texture_num):
            texture_path = os.path.join(texture_directory, 'p'+str(i) + '.jpeg')
            self.texture_path.append(os.path.abspath(texture_path))
        self.handle_pyapi = self.get_object_handle('RemotePyApi')
        self.handle_plate_texture = self.get_object_handle('plate_texture')
        self.handle_plane_texture = self.get_object_handle('plane')
        self.handle_table_texture = self.get_object_handle('table')

        self.obj_num = 0
        self.handle_tar_objs_texture = []

    def random_texture(self, obj, tar_objs_id=None):
        """Randomly assign color and textures to objects. For inserting task, the bases only change color.

        :param obj: List of object names.
               tar_objs_id: List of target objects' id.
               tar_obj_id: The id of some objects which need multiple textures in their corresponding list.
        :type obj: list.
              tar_objs_id: list.
              tar_obj_id: int value.

        The type of `obj` is list. elements in `obj` must be in
        ['plate', 'plane', 'table', 'tar_objs'].
        The type of `tar_objs_id` is list. When changing the textures and color of multiple objects at one time,
        it would be needed to find these objects' handle.
        `tar_obj_id` is int value. When changing the color of one or multiple parts of a same object at one time,
        it would be needed to find the parts' handle.
        """

        if 'tar_objs' in obj:
            self.obj_num = len(obj) + len(tar_objs_id) - 1
        else:
            self.obj_num = len(obj)
        self._create_texture()

        for i in range(len(obj)):
            if obj[i] == 'plate':
                self._set_texture(self.handle_plate_texture, id=i)
                self._set_color(self.handle_plate_texture)
            elif obj[i] == 'plane':
                self._set_texture(self.handle_plane_texture, id=i)
                self._set_color(self.handle_plane_texture, isTransparent=False)
            elif obj[i] == 'table':
                self._set_texture(self.handle_table_texture, id=i)
                self._set_color(self.handle_table_texture)
            elif obj[i] == 'tar_objs':
                self.handle_tar_objs_texture = []
                for j in range(len(tar_objs_id)):
                    handle_tar_obj_texture = self.get_object_handle('obj'+str(tar_objs_id[j])+'_texture0')
                    self.handle_tar_objs_texture.append(handle_tar_obj_texture)
                    self._set_texture(handle_tar_obj_texture, id=i)
                    self._set_color(handle_tar_obj_texture, isTransparent=False)

    def delete_texture(self):
        """Delete the textures that were entered into V_Rep and free up memory space"""

        obj_names = []
        for i in range(self.obj_num):
            if i == 0:
                obj_names.append('Plane')
            else:
                obj_names.append('Plane' + str(i - 1))
        texture_handles = list(map(self.get_object_handle, obj_names))
        for handle in texture_handles:
            self.call_childscript_function('RemotePyApi', 'pyRemoveObj', [[handle], [], [], bytearray()])

    def _create_texture(self):
        """Make pictures enter into V-Rep and automatically generate corresponding handles of textures in V-Rep"""

        inInts = [random.randint(0, 15), self.resolution[0], self.resolution[1]]
        inFloats = []
        emptyBuff = bytearray()
        self.texture_id = []
        texture_id = random.sample(range(self.texture_num), self.obj_num)
        for t_id in texture_id:
            inInts[0] = random.randint(0, 15)
            while True:
                inStrings = [self.texture_path[t_id]]
                inData = [inInts, inFloats, inStrings, emptyBuff]
                ret = self.call_childscript_function('RemotePyApi', 'pyCreateTexture', inData)
                if ret[1][0] == -1:
                    t_id += 1
                else:
                    self.texture_id.append(ret[1][0])
                    break

    def _set_texture(self, handle, id=0, isRemove=False):
        """Set or remove a texture to an object.

        :param handle: Handle of the target object in V-Rep.
               id: The id of the texture entered into V-Rep.
               isRemove: Add or remove the object's texture.
        :type handle: int value.
              id: int value.
              isRemove: bool.

        `isRemove` is bool value. `isRemove` is `True` when remove the texture of the object, `False` otherwise.
        """

        inInts = [handle]
        if isRemove:
            texture = -1
        else:
            texture = self.texture_id[id]
        inInts.append(texture)
        inInts.append(random.randint(0, 15))
        inInts += list(np.random.randint(-180, 180, size=3))
        inFloats = list(np.random.uniform(-1.0, 1.0, size=3))
        inStrings = []
        emptyBuff = bytearray()
        inData = [inInts, inFloats, inStrings, emptyBuff]
        self.call_childscript_function('RemotePyApi', 'pySetTexture', inData)

    def _set_color(self, handle, isTransparent=True, rgb=None):
        """Set a color to an object.

        :param handle: Handle of the target object in V-Rep.
               isTransparent: The object could be transparent or not.
               rgb: A set of given RGB values.
        :type handle: int value.
              isTransparent: bool.
              rgb: list, length=3.

        The type of `isTransparent` is bool.
            `isTransparent` is `True` when the object could be transparent, `False` otherwise.
        The type of `rgb` is list, length=3 for R, G and B in (0.0, 1.0). `rgb` is `None` if there's no given values.
        """

        inInts = [handle]
        if rgb is None:
            inFloats = list(np.random.uniform(0., 1.0, size=3))
        else:
            inFloats = list(rgb)
        if random.uniform(0, 1.0) > 0.5 or isTransparent is not True:
            inFloats.append(1.0)
        else:
            inFloats.append(random.uniform(0, 1.0))
        inStrings = []
        emptyBuff = bytearray()
        inData = [inInts, inFloats, inStrings, emptyBuff]
        self.call_childscript_function('RemotePyApi', 'pySetColor', inData)
