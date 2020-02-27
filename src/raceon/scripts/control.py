#!/usr/bin/env python
# license removed for brevity

import rospy
from geometry_msgs.msg import Pose
from raceon.msg import AckermannDrive

class Controller():
    
    def __init__(self):
        self.topic_name_pos_err = rospy.get_param("topic_name_position_error", "position/error")
        self.topic_name_control = rospy.get_param("topic_name_control", "control")
        
        # Parameters for control
        self.motor_speed = rospy.get_param("~motor_speed", 200)
        self.target = rospy.get_param("~target", 0)
        self.kp = rospy.get_param("~kp", 1)
    
    def start(self):
        self.sub_pos_err = rospy.Subscriber(self.topic_name_pos_err, Pose, self.pos_err_callback)
        self.pub_control = rospy.Publisher(self.topic_name_control, AckermannDrive, queue_size=10)
        rospy.spin()

    def pos_err_callback(self, pos_err_msg):
        pos_err = self.target - pos_err_msg.position.x
        
        rospy.loginfo("Current error: pos_err = " + str(pos_err))
        
        servo_pos = self.control_servo(pos_err)
        motor_speed = self.motor_speed
        
        rospy.loginfo("Control command: servo_pos = " + str(servo_pos) + ", motor_speed = " + str(motor_speed))
        
        control_msg = AckermannDrive()
        control_msg.speed = motor_speed
        control_msg.steering_angle = servo_pos
        self.pub_control.publish(control_msg)
        
    # TODO: Implement PID
    def pid(self, error):
        if abs(error) > 20:
            return error * self.kp * 1
        if abs(error) > 30:
            return error * self.kp * 10
        if abs(error) > 40:
            return error * self.kp * 20
        return error * self.kp

    def control_servo(self, error):
        correction = self.pid(error)
        servo_pos = correction

        return int(servo_pos)

if __name__ == "__main__":
    rospy.init_node("control")
    controller = Controller()
    try:
        controller.start()
    except rospy.ROSInterruptException:
        pass
