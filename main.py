import logging
import cv2


import hand_coded_lane_follower
from Servo import *
from Motor import *
#from camera_opencv import Camera

_SHOW_IMAGE = True

class Ivision(object):

    __INITIAL_SPEED = 40
    __SCREEN_WIDTH = 320
    __SCREEN_HEIGHT = 240

    def __init__(self):
        """ Init camera and wheels"""
        logging.info('Creating a Ivision Car...')

        #logging.debug('Set up camera')
        self.camera = cv2.VideoCapture(-1)
        self.camera.set(3, self.__SCREEN_WIDTH)
        self.camera.set(4, self.__SCREEN_HEIGHT)
        _, self.img = self.camera.read()
        self.frame = cv2.rotate(self.img, cv2.ROTATE_180)
        cv2.imwrite('/share/Code/test_img.png', self.frame)

        #logging.debug('Set up front wheels')
        self.front_wheels = Motor()
        self.front_wheels.setMotorModel(0, 0) # Speed Range is 0 (stop) - 40 (fastest)

        #Lane_line_detection
        self.lane_follower = hand_coded_lane_follower.HandCodedLaneFollower(self)
        self.combo_image = self.lane_follower.follow_lane(frame=self.frame)

        #Servo angle control
        self.pan_servo = Servo()
        self.pan_servo.setServoPwm('4', self.lane_follower.curr_steering_angle)

        #logging.info('Created a Ivision Car')

    '''def create_video_recorder(self, path):
        return cv2.VideoWriter(path, self.fourcc, 20.0, (self.__SCREEN_WIDTH, self.__SCREEN_HEIGHT))'''

    def __enter__(self):
        """ Entering a with statement """
        return self

    def __exit__(self, _type, value, traceback):
        """ Exit a with statement"""
        if traceback is not None:
            # Exception occurred:
            logging.error('Exiting with statement with exception %s' % traceback)

        self.cleanup()

    def cleanup(self):
        """ Reset the hardware"""
        #logging.info('Stopping the car, resetting hardware.')
        self.front_wheels.setMotorModel(0, 0)
        self.pan_servo.setServoPwm('4' , 90)
        self.camera.release()
        cv2.destroyAllWindows()

    def drive(self, speed=__INITIAL_SPEED):
        """ Main entry point of the car, and put it in drive mode

        Keyword arguments:
        speed -- speed of front wheel, range is 0 (stop) - 40 (fastest)
        """

        #logging.info('Starting to drive at speed %s...' % speed)

        self.front_wheels.setMotorModel(speed, speed, -18, 0)
        i = 0
        while self.camera.isOpened():
            _, images = self.camera.read()
            image_lane = cv2.rotate(images, cv2.ROTATE_180)
            #cv2.imwrite('/share/Code/test_img.png', self.frame)
            image_objs = image_lane.copy()
            i += 1

            image_lane = self.follow_lane(image_lane)
            cv2.imwrite('/share/Code/lane_line_img.png', image_lane)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cleanup()
                break

    def follow_lane(self, image):
        img = self.lane_follower.follow_lane(image)
        return img


############################
# Utility Functions
############################
#def show_image(title, frame, show=_SHOW_IMAGE):
 #   if show:
  #      cv2.imshow(title, frame)


def main():
    with Ivision() as car:
        car.drive(40)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, format='%(levelname)-5s:%(asctime)s: %(message)s')
    main()
