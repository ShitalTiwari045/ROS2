import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():  
    bumperbot_bringup_dir = get_package_share_directory('bumperbot_bringup')
    bumperbot_controller_dir = get_package_share_directory('bumperbot_controller')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bumperbot_bringup_dir, 'launch', 'gazebo.launch.py')
        )
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        parameters=[os.path.join(bumperbot_controller_dir, 'config', 'joy_config.yaml')]
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy_node',
        parameters=[os.path.join(bumperbot_controller_dir, 'config', 'joy_teleop.yaml')],
        remappings=[('/cmd_vel', '/cmd_vel')]
    )

    return LaunchDescription([
        gazebo_launch,
        joy_node,
        teleop_node,
    ])
