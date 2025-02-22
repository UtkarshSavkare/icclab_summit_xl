#!/usr/bin/env python3

# used code as ref from https://hotblackrobotics.github.io/en/blog/2018/01/29/action-client-py/

import psutil
import rospy
import rosnode

# Brings in the SimpleActionClient
import actionlib

# Brings in the .action file and messages used by the move base action
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import PoseStamped

def movebase_client():
    # Create an action client called "move_base" with action definition file "MoveBaseAction"
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)

    # Waits until the action server has started up and started listening for goals.
    rospy.loginfo("Waiting for move_base action server...")
    wait = client.wait_for_server(timeout=rospy.Duration(300.0)) # takes a while for sim environment to bring up
    if not wait:
        rospy.logerr("Action server not available!")
        rospy.logerr("Navigation test failed!")
        rospy.signal_shutdown("Action server not available!")
        kill_gzserver()
        return
    rospy.loginfo("Connected to move base server")
    rospy.loginfo("Starting goals achievements ...")

    # Creates a new goal with the MoveBaseGoal constructor
    def goal_callback(msg):
        goal = MoveBaseGoal()
        goal.target_pose = msg
        goal.target_pose.header.stamp = rospy.Time.now()

        # Sends the goal to the action server.
        client.send_goal(goal)

        # Waits for the server to finish performing the action.
        client.wait_for_result()

    rospy.loginfo("Subscribing to /summit_xl/move_base/current_goal topic...")
    rospy.Subscriber('/summit_xl/move_base/current_goal', PoseStamped, goal_callback)
    rospy.spin()   
      
    

# kills gazebo
def kill_gzserver():
    PROC_NAME = "gzserver"
    rospy.loginfo("Killing gzserver")
    for proc in psutil.process_iter():
        if proc.name() == PROC_NAME:
            proc.kill()

# If the python node is executed as main process (sourced directly)
if __name__ == '__main__':
    try:
       # Initializes a rospy node to let the SimpleActionClient publish and subscribe
        rospy.init_node('movebase_client_py')
        result = movebase_client()
        if result:
            rospy.loginfo("Goal execution done; success!")
            nodes = rosnode.get_node_names()
            rospy.loginfo("Killing all nodes")
            rosnode.kill_nodes(nodes)
            kill_gzserver()
    except rospy.ROSInterruptException:
            rospy.loginfo("Navigation test finished.")
