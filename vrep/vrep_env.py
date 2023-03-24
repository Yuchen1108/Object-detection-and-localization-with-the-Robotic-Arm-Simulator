from vrep import sim
import numpy as np

BLOCKING = sim.simx_opmode_blocking


class VrepEnv:
    def __init__(self,
                 server_addr='127.0.0.1',
                 server_port=19997,
                 scene_path=None,
                 cid=-1):

        self.sim_running = False
        if cid == -1:
            self.cid = sim.simxStart(server_addr, server_port, True, True, 5000, 5)
        else:
            self.cid = cid
            self.sim_running = True

        sim.simxLoadScene(self.cid, scene_path, -1, BLOCKING)

    def start_simulation(self):
        if self.sim_running:
            raise RuntimeError('Simulation is already running.')
        sim.simxStartSimulation(self.cid, BLOCKING)
        self.sim_running = True

    def stop_simulation(self):
        if not self.sim_running:
            raise RuntimeError('Simulation is not running.')
        sim.simxStopSimulation(self.cid, BLOCKING)
        self.sim_running = False

    def step_simulation(self):
        sim.simxSynchronousTrigger(self.cid)

    def get_object_handle(self, name):
        _, handle = sim.simxGetObjectHandle(self.cid, name, BLOCKING)
        return handle

    def obj_get_position(self, handle, relativeToObjectHandle=-1):
        _, pos = sim.simxGetObjectPosition(self.cid, handle, relativeToObjectHandle, BLOCKING)
        return pos

    def obj_set_position(self, handle, position, relativeToObjectHandle=-1):
        sim.simxSetObjectPosition(self.cid, handle, relativeToObjectHandle, position, BLOCKING)

    def obj_get_orientation(self, handle, relativeToObjectHandle=-1):
        _, ori = sim.simxGetObjectOrientation(self.cid, handle, relativeToObjectHandle, BLOCKING)
        return ori

    def obj_set_orientation(self, handle, orientation, relativeToObjectHandle=-1):
        sim.simxSetObjectOrientation(self.cid, handle, relativeToObjectHandle, orientation, BLOCKING)

    def call_childscript_function(self, script_name, func_name, inData):
        outData = sim.simxCallScriptFunction(self.cid, script_name, 1, func_name, inData[0], inData[1], inData[2], inData[3], BLOCKING)
        return outData

    def obj_get_vision_image(self, handle):
        _, resolution, image = sim.simxGetVisionSensorImage(self.cid, handle, 0, BLOCKING)
        dim, im = resolution, image
        nim = np.array(im, dtype='uint8')
        nim = np.reshape(nim, (dim[1], dim[0], 3))
        nim = np.flip(nim, 0)  # horizontal flip
        return nim

    def obj_get_joint_angle(self, handle):
        _, angle = sim.simxGetJointPosition(self.cid, handle, BLOCKING)
        return angle

    def obj_set_position_target(self, handle, angle):
        sim.simxSetJointTargetPosition(self.cid, handle, -np.deg2rad(angle), BLOCKING)

    def get_path(self, points_num=30):
        emptyBuff = bytearray()
        inData = [[points_num], [], [], emptyBuff]
        outdata = self.call_childscript_function('RemotePyApi', 'pyGetPath', inData)
        return outdata[2]
