from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='joy',
            executable='joy_node',
            name='joystick',
            output='screen'
        ),
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy_node',
            parameters=[{
                'axis_linear.x': 1,
                'axis_angular.yaw': 2,
                'scale_linear.x': 0.5,
                'scale_angular.yaw': 0.5,
            }],
            remappings=[
                ('cmd_vel', '/cmd_vel'),
            ]
        ),
    ])
