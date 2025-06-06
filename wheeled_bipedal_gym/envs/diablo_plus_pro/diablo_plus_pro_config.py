'''
Description: 
Version: 2.0
Author: Dandelion
Date: 2025-02-25 21:17:59
LastEditTime: 2025-03-13 22:20:42
FilePath: /wheeled_bipedal_gym/wheeled_bipedal_gym/envs/diablo_plus_pro/diablo_plus_pro_config.py
'''
# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2021 ETH Zurich, Nikita Rudin

from wheeled_bipedal_gym.envs.base.wheeled_bipedal_config import (
    WheeledBipedalCfg,
    WheeledBipedalCfgPPO,
)
import math


class DiabloPlusProCfg(WheeledBipedalCfg):
    class env(WheeledBipedalCfg.env):
        num_envs = 4096
        num_observations = 27
        num_privileged_obs = (num_observations + 7 * 11 + 3 + 6 * 5 + 3 + 3)

    # 设置地形参数
    class terrain(WheeledBipedalCfg.terrain):
        mesh_type = "trimesh"
        # mesh_type = "plane"
        # mesh_type = "trimesh"  # "heightfield" # none, plane, heightfield or trimesh
        horizontal_scale = 0.1  # [m]
        vertical_scale = 0.005  # [m]
        border_size = 25  # [m]
        curriculum = True
        static_friction = 0.4
        dynamic_friction = 0.6
        restitution = 0.5
        # rough terrain only:
        measure_heights = True
        measured_points_x = [-0.5,-0.4,-0.3,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4,0.5]  # 1mx1.6m rectangle (without center line)
        measured_points_y = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3]
        selected = False  # select a unique terrain type and pass all arguments
        terrain_kwargs = None  # Dict of arguments for selected terrain
        max_init_terrain_level = 5  # starting curriculum state
        terrain_length = 15 #地形长度，单位：米
        terrain_width = 15 #地形宽度，单位：米  
        num_rows = 20  # number of terrain rows (levels)
        num_cols = 20  # number of terrain cols (types)
        # terrain types: [smooth slope, rough slope, stairs up, stairs down, discrete]
        terrain_proportions = [0.0, 0.1, 0.2, 0.35, 0.2, 0.15]#分别对应上面地形的比例
        # terrain_proportions = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0]#分别对应上面地形的比例
        # trimesh only:
        slope_treshold = (
            0.75  # slopes above this threshold will be corrected to vertical surfaces
        )

    class commands(WheeledBipedalCfg.commands):
        curriculum = True
        basic_max_curriculum = 2.5
        advanced_max_curriculum = 1.5
        curriculum_threshold = 0.7 #机器人在达到一定的性能水平后，会逐渐面临更高难度的任务，从而实现课程学习的目标。
        num_commands = 3  # default: lin_vel_x, lin_vel_y, ang_vel_yaw, heading (in heading mode ang_vel_yaw is recomputed from heading error)
        resampling_time = 5.0  # time before command are changed[s]
        heading_command = False  # if true: compute ang vel command from heading error

        class ranges(WheeledBipedalCfg.commands.ranges):
            lin_vel_x = [-1.2, 1.2]  # min max [m/s]
            ang_vel_yaw = [-0.5, 0.5]  # min max [rad/s]
            height = [0.18, 0.35]
            heading = [-0.2, 0.2]

    # 定义机器人的初始离地位姿 & 初始线速度角速度和default_joint_angles
    class init_state(WheeledBipedalCfg.init_state):
        # pos = [0.0, 0.0, 0.17]  # x,y,z [m] #匍匐的时候
        pos = [0.0, 0.0, 0.35]  # x,y,z [m] #默认是站立的
        rot = [0.0, 0.0, 0, 1.0]  # x,y,z,w [quat]
        default_joint_angles = {  # target angles when action = 0.0
            "left_hip_joint": 0.184481302,
            "left_knee_joint": 1.194677873,
            "left_wheel_joint": 0.0,
            "right_hip_joint": 0.184481302,
            "right_knee_joint": 1.194677873,
            "right_wheel_joint": 0.0,
        }  # 这个要和urdf内部的joint对应，并且其顺序决定了joint的顺序

    # 底层控制器的选取和PD参数的设置
    class control(WheeledBipedalCfg.control):
        control_type = "P"  # P: position, V: velocity, T: torques 
        # PD Drive parameters:
        stiffness = {
            "hip": 40.0,
            "knee": 40.0,
            "wheel": 0,
        }  # [N*m/rad]
        damping = {
            "hip": 1.0,
            "knee": 1.0,
            "wheel": 1.0,
        }  # [N*m*s/rad]
        # action scale: target angle = actionScale * action + defaultAngle
        action_scale = 0.5 #通过缩放，可以确保策略网络输出的动作在合理范围内
        pos_action_scale = 0.25
        vel_action_scale = 8.0

        # decimation: Number of control action updates @ sim DT per policy DT
        decimation = 2  # 它表示每个仿真间隔dt内policy的更新次数，它和sim里面的dt联合决定了这个控制模型的频率。为dt*decimation
        feedforward_force = 60.0

    # 定义机器人模型内容，例如URDF和一些上下限
    class asset(WheeledBipedalCfg.asset):
        file = "{WHEELED_BIPEDAL_GYM_ROOT_DIR}/resources/robots/diablo_plus_pro/urdf/diablo_plus_pro.urdf"
        name = "diablo_plus_pro"
        foot_name = "wheel"
        foot_radius = 0.16
        hip_link_init_angle = math.pi - 0.930609557
        knee_link_init_angle = -math.pi + 1.761037215
        offset = 0.0
        l1 = 0.2
        l2 = 0.2
        self_collisions = 0  # 1 disable; 0 enable
        penalize_contacts_on = [
            "left_hip_link",
            "left_knee_link",
            "right_hip_link",
            "right_knee_link",
            "base_link",
        ]  # 碰到地面会收到惩罚的name of Link
        terminate_after_contacts_on = [
            "base_link",
            "knee_link",
        ]  # 碰到地面达到一定条件（接触力&时间）后会直接提前结束当前轮的envs

    # 通过增加各种随机值来增加机器人的鲁棒性，
    # 例如随机地面摩擦力，随机机器人质量，质心位置，随机push机器人等。
    class domain_rand(WheeledBipedalCfg.domain_rand):
        randomize_friction = True
        friction_range = [0.2, 2.0]
        randomize_restitution = True
        restitution_range = [0.0, 1.0]
        randomize_base_mass = True
        added_mass_range = [-0.5, 2.0]
        randomize_inertia = True
        randomize_inertia_range = [0.8, 1.2]
        randomize_base_com = True
        rand_com_vec = [0.05, 0.05, 0.05]
        push_robots = True
        push_interval_s = 7
        max_push_vel_xy = 2.0
        randomize_Kp = True
        randomize_Kp_range = [0.9, 1.1]
        randomize_Kd = True
        randomize_Kd_range = [0.9, 1.1]
        randomize_motor_torque = True
        randomize_motor_torque_range = [0.9, 1.1]
        randomize_default_dof_pos = False
        randomize_default_dof_pos_range = [-0.3, 0.3]
        randomize_action_delay = True
        delay_ms_range = [0, 10]

    class rewards(WheeledBipedalCfg.rewards):

        class scales(WheeledBipedalCfg.rewards.scales):
            tracking_lin_vel = 20.0
            tracking_lin_vel_enhance = 10.0
            tracking_ang_vel = 5.0

            base_height = 5.0
            base_height_enhance = 0.0 #off
            nominal_state = -0.5
            # wheel_adjustment = 1.0
            lin_vel_z = 0.0 #off
            ang_vel_xy = -0.0
            orientation = -5.0 # 很重要，不加的话会导致存活时间下降（FROM 逐迹）

            dof_vel = -5e-5
            dof_acc = -2.5e-7
            torques = -1e-5
            torque_limits = -0.1
            action_rate = -0.05
            action_smooth = -0.03

            collision = -100.0
            dof_pos_limits = -0.1
            dof_vel_limits = -0.1
            # stand_still = -1.0

            theta_limit = -0.1
            same_l = 0.0
            wheel_vel = -1.0
            no_fly = 0.0
            # theta0_in_range = 1.0
            survival = 0.0
            termination = -100.0
            stumble = -5.0
            stand_still = 0.0
            no_stagnation = 0.0

        only_positive_rewards = False  # if true negative total rewards are clipped at zero (avoids early termination problems)
        clip_single_reward = 1
        tracking_sigma = 0.25  # tracking reward = exp(-error^2/sigma) #这个值越小跟踪效果反而越好，因为这样只有当速度非常接近v_set的时候奖励才会最大
        soft_dof_pos_limit = 1.0 # percentage of urdf limits, values above this limit are penalized       
        soft_dof_vel_limit = 0.95
        soft_torque_limit = 0.95
        base_height_target = 0.25 # [m]
        max_contact_force = 100.0  # forces above this value are penalized

    class normalization(WheeledBipedalCfg.normalization):

        class obs_scales(WheeledBipedalCfg.normalization.obs_scales):
            lin_vel = 2.0
            ang_vel = 0.25
            dof_pos = 1.0
            dof_vel = 0.05
            dof_acc = 0.0025
            height_measurements = 5.0
            torque = 0.05

        clip_observations = 100.0
        clip_actions = 100.0

    class noise(WheeledBipedalCfg.noise):
        add_noise = True
        noise_level = 0.5  # scales other values

        class noise_scales(WheeledBipedalCfg.noise.noise_scales):
            dof_pos = 0.01
            dof_vel = 1.5
            lin_vel = 0.1
            ang_vel = 0.2
            gravity = 0.05
            height_measurements = 0.1

    # viewer camera:
#TO READ

class DiabloPlusProCfgPPO(WheeledBipedalCfgPPO):
    class runner(WheeledBipedalCfgPPO.runner):
        # logging
        experiment_name = "diablo_plus_pro"
        max_iterations = 10000
