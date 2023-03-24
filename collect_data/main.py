from random_env.image_collecting import RandomEnv
import sys


def main():
    scene_file = 'UR5_pick_env.ttt'
    # server_port = int(sys.argv[1])
    server_port = 19997

    env = [RandomEnv(server_port=server_port,
                       scene_directory='/home/zoker/COMP6445/Group_project/collect_data/scenes',
                       scene_file=scene_file,
                       texture_directory='/home/zoker/COMP6445/Group_project/collect_data/pictures_new',
                       texture_num=125)]
    env[0].reset()
    while True:
        env[0].run()


if __name__ == '__main__':
    main()