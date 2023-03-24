from vrep import vrep_env
import numpy as np
import os


class Demo(vrep_env.VrepEnv):

    def __init__(self,
                 server_addr='127.0.0.1',
                 server_port=19997,
                 scene_directory=None,
                 scene_file=None):

        assert scene_directory, 'scene directoy must be provided'
        scene_path = os.path.join(scene_directory, scene_file)
        scene_path = os.path.abspath(scene_path)
        print('loading scene from {}'.format(scene_path))
        vrep_env.VrepEnv.__init__(self, server_addr, server_port, scene_path)

        self.step_num = 0
        joint_names = ['UR5_joint' + str(i + 1) for i in range(6)]
        self.handle_joints = list(map(self.get_object_handle, joint_names))
        self.handle_camera = self.get_object_handle('Camera')

        self.handle_target = self.get_object_handle("Target")

    def _multi_step(self, nstep=5):
        """Simulate every once in a while in V-Rep.

        :param nstep: The time interval.
        :type nstep: int value.

        `nstep` is int value for the time interval between two simulations in V-rep.
        """

        for i in range(nstep):
            self.step_simulation()

    def open_gripper(self):
        """Open the gripper."""
        emptyBuff = bytearray()
        inData = [[], [], [], emptyBuff]
        self.call_childscript_function('ROBOTIQ_85', 'open_paw', inData)
        self._multi_step(50)

    def close_gripper(self):
        """Close the gripper."""
        emptyBuff = bytearray()
        inData = [[], [], [], emptyBuff]
        self.call_childscript_function('ROBOTIQ_85', 'close_paw', inData)
        self._multi_step(50)

    def move_on_path(self, points_num=30):
        """Generate a path and move the end of the robotic arm along the path.

        :param points_num: Number of way points on the path
        """
        path = self.get_path(points_num)
        for i in range(0, len(path), 6):
            for j in range(6):
                self.obj_set_position_target(self.handle_joints[j], -np.rad2deg(path[i + j]))

    def move2pos(self, pos, points_num=30):
        """Move the end of the robotic arm to the specified position.

        :param pos: The target position
        :param points_num: Number of way points on the path
        """
        self.obj_set_position(self.handle_target, pos)
        self._multi_step()
        self.move_on_path(points_num)
        self._multi_step()

    def get_state(self):
        """Get current joint state of UR5.

        :return: state
        `state` is list, length=6 for current joint state (in radian) of UR5.
        """
        radian_action = []
        for i in range(6):
            radian_action.append(self.obj_get_joint_angle(self.handle_joints[i]))
        return radian_action

    def set_pose(self, pose):
        """Set the pose of the robotic arm to a specified value.

        :param pose: The target pose
        """
        for i_h, i_p in zip(self.handle_joints, pose):
            self.obj_set_position_target(i_h, -i_p)

    def move2pose(self, pose, points_num=30):
        """Move the robotic arm to a specified pose.

        :param pose: The target pose
        :param points_num: Number of way points on the path
        """
        current_pose = self.get_state()
        current_pose = np.array(self.radian_to_angle(current_pose))
        target_pose = np.array(pose)
        pose_step = (target_pose - current_pose) / points_num
        for i in range(points_num):
            self.set_pose(current_pose + (i + 1) * pose_step)

    def run(self):
        self.step_num += 1
        pos1 = [0.65, -0.075, 1]
        pos2 = [0.65, -0.075, 0.73]
        self.move2pos(pos1, 30)
        self.move2pos(pos2, 20)
        self.close_gripper()
        self.move2pos(pos1, 20)
        pose = self.get_state()
        pose[0] += np.pi / 2
        pose = self.radian_to_angle(pose)
        self.move2pose(pose)
        self.open_gripper()

    def reset(self):
        """Reset V-Rep"""

        if self.sim_running:
            self.stop_simulation()
        self.start_simulation()
        self.step_num = 0
        self._multi_step()

    @staticmethod
    def angle_to_radian(joint_angles):
        """
        Convert an angle list of joints to the corresponding radian list of joints.

        :param joint_angles: Angel value list of joints.
        :type joint_angles: 1-D numpy.array, length>0
        :return: rad

        The type of `rad` is a 1-D numpy.array, length equals to `joint_angles`.
        """

        n = len(joint_angles)
        rad = np.zeros(n)
        for i in range(n):
            rad[i] = joint_angles[i] / 180.0 * np.pi
        return list(rad)

    @staticmethod
    def radian_to_angle(rad_list):
        """
        Convert a radian list of joints to the corresponding angle list of joints.

        :param rad_list: Radian value list of joints.
        :type rad_list: 1-D numpy.array, length>0
        :return: joint_angles

        The type of `joint_angles` is a 1-D numpy.array, length equals to `rad_list`.
        """

        n = len(rad_list)
        joint_angles = np.zeros(n)
        for i in range(6):
            joint_angles[i] = rad_list[i] * 180.0 / np.pi
        return list(joint_angles)


def main():
    scene_file = 'UR5_demo.ttt'
    server_port = 19997

    env = [Demo(server_port=server_port,
                scene_directory='/home/zoker/COMP6445/Group_project/demo/scenes',
                scene_file=scene_file)]
    env[0].reset()
    while True:
        env[0].run()


if __name__ == '__main__':
    main()