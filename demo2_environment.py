import glob
import carla
import sys
import os
import numpy as np
import pygame
from numpy import random

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass




class CarManager(object):
    def __init__(self, world):  # world = client.get_world()
        self.world = world
        self.ego_vehicle = None

        blueprint_library = world.get_blueprint_library()
        self.ego_vehicle_bp = blueprint_library.find('vehicle.audi.tt')
        self.ego_vehicle_bp.set_attribute('color', '0, 0, 0')
        transform = random.choice(world.get_map().get_spawn_points())
        # transform = carla.Transform(carla.Location(x=-78.034149, y=12.967159, z=0.6), carla.Rotation(yaw=-179.84079))

        self.ego_vehicle = self.world.spawn_actor(self.ego_vehicle_bp, transform)
        self.ego_vehicle.set_autopilot(False)

        print(self.ego_vehicle.bounding_box)

class SensorManager(object):
    def __init__(self, world, car):  # world = client.get_world()    car = CarManager(world)
        self.surface = None
        self.world = world
        self.car = car
        # 添加RGB相机，相机的图像大小记得和pygame窗口一样哦
        blueprint_library = world.get_blueprint_library()
        self.camera_bp = blueprint_library.find('sensor.camera.rgb')
        self.camera_bp.set_attribute('image_size_x', '1920')
        self.camera_bp.set_attribute('image_size_y', '1080')
        self.camera_bp.set_attribute('fov', '110')
        #camera_transform = carla.Transform(carla.Location(x=0, y=0, z=0))
        camera_transform = carla.Transform(car.ego_vehicle.bounding_box.location)
        # +x前 +y右 +z 上
        self.camera = self.world.spawn_actor(self.camera_bp, camera_transform, attach_to=self.car.ego_vehicle)
        # 设置监听传感器的处理函数
        self.camera.listen(lambda image: self._parse_image(image))

    # 这个函数是绘制图像的，提供给pygame来显示
    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))

    # 对传感器的raw图像进行处理
    def _parse_image(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1920,1080),pygame.HWSURFACE)
    try:
        client = carla.Client('127.0.0.1',2000)
        world = client.get_world()
        pygame.display.set_caption("Camera Vision")
        car = CarManager(world)
        sensor = SensorManager(world,car)

        clock = pygame.time.Clock()
        while True:
            clock.tick_busy_loop(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                world.wait_for_tick()
                sensor.render(screen)# screen.blit() 将画面家在到窗口，暂时不画画
                pygame.display.flip()
    finally:
        car.ego_vehicle.destroy()
        sensor.camera.stop()
        sensor.camera.destory()
        print('done')
        pygame.quit()
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('- Exit by user')
