#! /usr/bin/env python
'''
@author: Sammy Pfeiffer

Node to interact with screen messages to activate
or deactivate joints to do learning by demonstration
'''
import rospy
from learn_from_robot.msg import JointActivation
from pal_control_msgs.srv import CurrentLimit, CurrentLimitRequest

ACTIVATION_TOPIC = '/active_joints'
CURRENT_LIMIT_SRV = '/current_limit_controller/set_current_limit'

ACTIVATED = 1.0
DEACTIVATED = 0.01

class activation_manager():
    def __init__(self):
        rospy.loginfo("Subscribing to '" + ACTIVATION_TOPIC + "'")
        self.activation_subs = rospy.Subscriber(ACTIVATION_TOPIC, JointActivation, self.activation_cb)
        
        rospy.loginfo("Trying to connect to service'" + CURRENT_LIMIT_SRV + "'...")
        self.current_limit_srv = rospy.ServiceProxy(CURRENT_LIMIT_SRV, CurrentLimit)
        self.current_limit_srv.wait_for_service()
        
        self.head = ['head_1_joint', 'head_2_joint'] # Does not work :( motors are different
        self.torso = ['torso_1_joint', 'torso_2_joint']
        self.left_arm = ['arm_left_1_joint', 'arm_left_2_joint', 'arm_left_3_joint',
                           'arm_left_4_joint', 'arm_left_5_joint', 'arm_left_6_joint',
                           'arm_left_7_joint']
        self.right_arm = ['arm_right_1_joint', 'arm_right_2_joint', 'arm_right_3_joint',
                           'arm_right_4_joint', 'arm_right_5_joint', 'arm_right_6_joint',
                           'arm_right_7_joint']
        self.left_hand = ['hand_left_index_joint', 'hand_left_middle_joint', 'hand_left_thumb_joint'] # Only the actuated
        self.right_hand = ['hand_right_index_joint', 'hand_right_middle_joint', 'hand_right_thumb_joint'] # Only the actuated
        
        self.group_names = ['head', 'torso', 'left_arm', 'right_arm', 'left_hand', 'right_hand']
        rospy.loginfo("Finished initialization.")

        
    def activation_cb(self, data):
        # Check if we got a group or a single joint to activate/deactivate
        joints = str(data.joints.data)
        if joints in self.group_names:
            list_of_joints = getattr(self, joints)
        else:
            list_of_joints = [joints]
        
        # Set the mode of the joint
        for joint in list_of_joints:
            req = CurrentLimitRequest()
            req.actuator_name = joint.replace('joint', 'motor')
            if data.active.data: # If True, activate
                rospy.loginfo("Setting joint '" + joint + "' to ACTIVE")
                req.current_limit = ACTIVATED
            else:
                rospy.loginfo("Setting joint '" + joint + "' to DEACTIVATED")
                req.current_limit = DEACTIVATED
            self.current_limit_srv.call(req)

        
        
if __name__ == '__main__':
    rospy.init_node('activation_manager_')
    am = activation_manager()
    rospy.spin()