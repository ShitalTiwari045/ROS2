from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    config_path = os.path.join(
        get_package_share_directory('bumperbot_controller'),
        'config',
        'ps3.config.yaml'  # Your PS3 joystick config
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen'
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy',
        parameters=[config_path],
        remappings=[('/cmd_vel', '/cmd_vel')],
        output='screen'
    )

    return LaunchDescription([
        joy_node,
        teleop_node
    ])
