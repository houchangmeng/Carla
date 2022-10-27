#!/usr/bin/env python

import numpy as np
import random
import carla
import pygame
import os

# 设置客户端端口
client = carla.Client(host='127.0.0.1',port=2000) 
# 设置客户端延时
client.set_timeout(2)
# 获取仿真世界
world = client.get_world()
# 加载仿真地图
# world = client.load_world('Town01')
# 获取仿真世界中的blueprint库 
blueprint_library = world.get_blueprint_library()
# 获取奥迪A2的blueprint
ego_vehicle_bp = random.choice(blueprint_library.filter('*vehicle*'))
# 在blueprint上作画（设置参数）每个blueprint都有set 和get 方法
#ego_vehicle_bp.set_attribute('color','0,0,0')
# 随即生成一个落脚点
# transform = random.choice(world.get_map().get_spawn_points())
#print(transform)
# 将奥迪blueprint实例化为仿真世界中的一个actor
# +x 倒车
transform = carla.Transform(carla.Location(x=106.377342, y=-1.649443, z=0.600000), \
                            carla.Rotation(pitch=0.0, yaw=0, roll=0))# -180 横着的
# +x 侧向
ego_vehicle = world.spawn_actor(ego_vehicle_bp,transform)
# 每个actor 都有set方法和get方法
# location = ego_vehicle.get_location()
# location.x+=10
# ego_vehicle.set_location(location)
# ego_vehicle.set_autopilot(True)
# 注销Actor
# ego_vehicle.destory()
# 批处理注销
# client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

# 创建传感器 相机
camera_bp = blueprint_library.find('sensor.camera.rgb')
camera_relative_transform = carla.Transform(carla.Location(x=10,y=0,z=0),carla.Rotation(pitch=0,yaw=0,roll=0))
# 把相机放在车上（相对坐标）
camera = world.spawn_actor(camera_bp, camera_relative_transform, attach_to=ego_vehicle)
# 设置回调函数
#camera.listen(lambda image: image.save_to_disk('/home/ubuntu-1/Study/Carla/%06d.png' % image.frame))

# 创建激光雷达 设置属性
lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
lidar_bp.set_attribute('channels', str(32))
lidar_bp.set_attribute('points_per_second', str(90000))
lidar_bp.set_attribute('rotation_frequency', str(40))
lidar_bp.set_attribute('range', str(20))
# 成成雷达，放在车上
lidar_relative_transform = carla.Transform(carla.Location(x=0, y=0, z=2), carla.Rotation(pitch=0,yaw=0,roll=0))
lidar = world.spawn_actor(lidar_bp, lidar_relative_transform, attach_to=ego_vehicle)
# 设置回调函数
# lidar.listen(lambda point_cloud: point_cloud.save_to_disk('/home/ubuntu-1/Study/Carla/%06d.ply' % point_cloud.frame))
# 设置观察者位置
spectator = world.get_spectator()
transform = ego_vehicle.get_transform()
spectator.set_transform(carla.Transform(transform.location + carla.Location(z=20),carla.Rotation(pitch=-90)))


