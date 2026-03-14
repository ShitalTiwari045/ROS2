from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, OpaqueFunction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.conditions import UnlessCondition, IfCondition

# For teleop joy
from launch.substitutions import ThisLaunchFileDir
import os

def noisy_controller(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time")  
    use_python = LaunchConfiguration("use_python")
    wheel_radius = float(LaunchConfiguration("wheel_radius").perform(context))
    wheel_separation = float(LaunchConfiguration("wheel_separation").perform(context))
    wheel_radius_error = float(LaunchConfiguration("wheel_radius_error").perform(context))
    wheel_separation_error = float(LaunchConfiguration("wheel_separation_error").perform(context))

    noisy_controller_py = Node(
        package="bumperbot_controller",
        executable="noisy_controller.py",
        parameters=[
            {"wheel_radius": wheel_radius + wheel_radius_error,
             "wheel_separation": wheel_separation + wheel_separation_error,
             "use_sim_time": use_sim_time}],
        condition=IfCondition(use_python),
    )

    noisy_controller_cpp = Node(
        package="bumperbot_controller",
        executable="noisy_controller",
        parameters=[
            {"wheel_radius": wheel_radius + wheel_radius_error,
             "wheel_separation": wheel_separation + wheel_separation_error,
             "use_sim_time": use_sim_time}],
        condition=UnlessCondition(use_python),
    )

    return [
        noisy_controller_py,
        noisy_controller_cpp,
    ]

def generate_launch_description():
    # Declare Launch Args
    use_sim_time_arg = DeclareLaunchArgument("use_sim_time", default_value="True")
    use_simple_controller_arg = DeclareLaunchArgument("use_simple_controller", default_value="True")
    use_python_arg = DeclareLaunchArgument("use_python", default_value="False")
    wheel_radius_arg = DeclareLaunchArgument("wheel_radius", default_value="0.033")
    wheel_separation_arg = DeclareLaunchArgument("wheel_separation", default_value="0.17")
    wheel_radius_error_arg = DeclareLaunchArgument("wheel_radius_error", default_value="0.005")
    wheel_separation_error_arg = DeclareLaunchArgument("wheel_separation_error", default_value="0.02")
    joy_config_arg = DeclareLaunchArgument(
        "joy_config", 
        default_value="/absolute/path/to/joy_config.yaml",  # <<< CHANGE this to your actual file
        description="Path to teleop_twist_joy config file"
    )

    # Launch Configs
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_simple_controller = LaunchConfiguration("use_simple_controller")
    use_python = LaunchConfiguration("use_python")
    wheel_radius = LaunchConfiguration("wheel_radius")
    wheel_separation = LaunchConfiguration("wheel_separation")
    joy_config = LaunchConfiguration("joy_config")

    # Controllers
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    wheel_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["bumperbot_controller", "--controller-manager", "/controller_manager"],
        condition=UnlessCondition(use_simple_controller),
    )
    joy_node = Node(
    package='joy',
    executable='joy_node',
    name='joy_node',
    parameters=[LaunchConfiguration('joy_config')],
    output='screen',
)

    teleop_node = Node(
    package='teleop_twist_joy',
    executable='teleop_node',
    name='teleop_twist_joy',
    parameters=[LaunchConfiguration('joy_config')],
    remappings=[('/cmd_vel', '/your_robot_namespace/cmd_vel')],
    output='screen',
)

    simple_controller = GroupAction(
        condition=IfCondition(use_simple_controller),
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["simple_velocity_controller", "--controller-manager", "/controller_manager"]
            ),
            Node(
                package="bumperbot_controller",
                executable="simple_controller.py",
                parameters=[
                    {"wheel_radius": wheel_radius,
                     "wheel_separation": wheel_separation,
                     "use_sim_time": use_sim_time}],
                condition=IfCondition(use_python),
            ),
            Node(
                package="bumperbot_controller",
                executable="simple_controller",
                parameters=[
                    {"wheel_radius": wheel_radius,
                     "wheel_separation": wheel_separation,
                     "use_sim_time": use_sim_time}],
                condition=UnlessCondition(use_python),
            ),
        ]
    )

    # Controller manager
    controller_manager_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {"use_sim_time": use_sim_time},
            "/path/to/your/urdf_file.urdf",
            "/path/to/your/controllers.yaml"
        ],
        output="screen"
    )

    # 🕹️ Add GameSir joy + teleop twist joy
    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        output="screen"
    )

    teleop_twist_joy_node = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        name="teleop_twist_joy_node",
        parameters=[joy_config],
        output="screen"
    )

    # Noisy controller
    noisy_controller_launch = OpaqueFunction(function=noisy_controller)

    return LaunchDescription([
        use_sim_time_arg,
        use_simple_controller_arg,
        use_python_arg,
        wheel_radius_arg,
        wheel_separation_arg,
        wheel_radius_error_arg,
        wheel_separation_error_arg,
        joy_config_arg,
        controller_manager_node,
        joint_state_broadcaster_spawner,
        wheel_controller_spawner,
        simple_controller,
        noisy_controller_launch,
        joy_node,
        teleop_twist_joy_node
    ])
