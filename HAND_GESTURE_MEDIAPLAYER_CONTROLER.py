import cv2
import random
import imutils
import sys

from package.HANDS import HAND_TRACKING
from package.COLORS import COLORS_ as COLORS
from package.FunctionHandler import FUNCTION_HANDLER

from collections import deque

import numpy as np


class YT_VLC_CONTROL_HAND_TRACKING:
    """
    WebCam sources
    """
    #__mobile_web_cam_url = 'https://192.168.0.100:8080/video'
    __hCam, __wCam = 600, 600
    __START_CAM = True
    __ESCAPE = 'q'
    __frame = None
    
    """
    OpenCv text font style
    """
    __TEXT_FONT = cv2.FONT_HERSHEY_PLAIN
    
    """
    Current action
    """
    __CURRENT_ACTION = "NONE"
    __CURRENT_ACTION_COLOR = [COLORS.RED,
                    COLORS.PINK,
                    COLORS.GREEN,
                    COLORS.YELLOW,
                    COLORS.WHITE]#(209,239,173)
    __CURRENT_ACTION_COORDINATES = (30, 30)
    __CURRENT_ACTION_TEXT_THICKNESS = 2
    __CURRENT_ACTION_TEXT_FONTSCALE = 1
    
    """
    Min and Max Degree
    """
    __DEGREE_MIN = -130
    __DEGREE_MAX = -60
    
    """
    Max and Min area of hand
    """
    __MAX_AREA = 900
    __MIN_AREA = 100

    """
    Selection choices
    """
    # Thumb Finger
    __THUMB_FINGERUP = [0, 1, 1, 1, 1]
    __PLAY_PAUSE_FINGER_NUM = [4, 13]

    # All Close
    __CLOSE_FINGERUP = [0, 0, 0, 0, 0]

    # Forward 
    __FORWARD_FINGERUP = [0, 1, 1, 0, 0]

    # Backward
    __BACKWARD_FINGERUP = [1, 0, 0, 0, 0]

    # Volume Up
    __VOLUME_UP = [1, 1, 0, 0, 1]

    # Volume Down
    __VOLUME_DOWN = [0, 1, 0, 0, 1]

    # Skip Ads
    __SKIP_ADS= [1, 1, 1, 1, 0]

    """
    Swipe Actions
    """
    __SWIPE_ACTION = None
    __START_SWIPE = False
    __BUFFER = 20
    __DIRECTION = None
    __PTS = deque(maxlen = __BUFFER)
    __COUNTER = 0
    __MAX_MOVE_SWIPE = 87
    __SWIPECOUNTER = 0
    __DX, __DY = (0, 0)
    __FX, __FY = (0, 0)
    __DIRECTIONS = ('EAST', 'WEST', 'NORTH', 'SOUTH')

    """
    Swipe Fingers
    """
    __WRIST_IDX = 0

    """
    Swipe Select
    """
    __SWIPE_PINKY = [0, 1, 1, 0, 1]

    """
    Swipe Forward / Backward
    """
    __SWIPE_XPOS, __SWIPE_YPOS = [], []
        
    def __init__(self, CHOICE = 'youtube', WEB_CAM_SOURCE = 0, swipe=False):
        print("[~] INITIALISING...")
        """
        Init
        """ 
        self.__CHOICE = CHOICE
        self.__WEB_CAM_SOURCE = WEB_CAM_SOURCE
        self.__SWIPE = swipe
        
        """
        Hand tracking module inputes
        """
        self.__MIN_DETECTION_CONFIDENCE = 0.75
        self.__MAX_HAND = 1
        self.__MIN_TRACKING_CONFIDENCE = 0.5

        """
        Initialise Modules
        """
        print("[~] INITIALISING WEBCAM....")
        ###WebCam input
        self.__CAP = cv2.VideoCapture(self.__WEB_CAM_SOURCE)
        self.__CAP.set(3, self.__wCam)
        self.__CAP.set(4, self.__hCam)

        """
        Initialize HAND TRACKING MODULE
        """
        self.__hand_track = HAND_TRACKING(min_detection_confidence=self.__MIN_DETECTION_CONFIDENCE,
                                maxHands=self.__MAX_HAND,
                                min_tracking_confidence=self.__MIN_TRACKING_CONFIDENCE)
        self.__function_handler = FUNCTION_HANDLER(choice=self.__CHOICE)

    def __del__(self):
        self.__CAP.release()
        cv2.destroyAllWindows()

    def __check_choice(self):
        if self.__CHOICE in ['youtube', 'vlc']:
            return True
        if self.__CHOICE not in ['youtube', 'vlc']:
            return False

    def __getDirection(self) -> str:
        if len(self.__PTS) >= 10:
            for p in range(1, len(self.__PTS)):
                if self.__COUNTER >= 10:
                    self.__DX = self.__PTS[0][0] - self.__PTS[p][0]   
                    self.__DY = self.__PTS[0][1] - self.__PTS[p][1]   
                    (dirX, dirY) = ('', '')    

            if np.abs(self.__DX) > self.__MAX_MOVE_SWIPE:
                dirX  = self.__DIRECTIONS[0] if np.sign(self.__DX) == 1 else self.__DIRECTIONS[1]
            if np.abs(self.__DY) > self.__MAX_MOVE_SWIPE:
                dirY = self.__DIRECTIONS[3] if np.sign(self.__DY) == 1 else self.__DIRECTIONS[2]
            self.__DIRECTION = dirX if dirX != '' else dirY
        return self.__DIRECTION

    def start(self):
        __VALID_CHOICE = self.__check_choice()
        if __VALID_CHOICE:
            print("\t[~] STARTING WEBCAM....\n")
            while self.__START_CAM:
                s, self.__frame = self.__CAP.read()
                try:

                    # resize the frame with width = 600
                    self.__frame = imutils.resize(self.__frame, width=600)

                except AttributeError as e:print("[!] Connect webcam....") ;sys.exit()

                if not s:
                    print('[~] Check WebCam.')
                    

                self.__frame = cv2.flip(self.__frame, 1)

                self.__frame = self.__hand_track.getKeyPointsWithFrame(image=self.__frame)

                __lmList, __bbox, __area = self.__hand_track.findPosition(img = self.__frame)

                """
                If Hand Detected!
                """
                if len(__lmList) != 0:
                    self.__frame, self.FRAME_RECTANGLE_COLOR = self.__hand_track.draw(
                                                img = self.__frame,
                                                bbox = __bbox,
                                                draw_hand = True,
                                                draw_fancy = True,
                                                style_type='with_border_2.0'
                                            )

                    """
                    List of Fingers
                    1 - Up
                    0 - Down
                    """
                    __fingerDown = self.__hand_track.fingersUp()
                    #print(__fingerDown)

                    """
                    If Degree is in range of -130 to -60.
                    """
                    __degree = int(self.__hand_track.findDegree())

                    #"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    #print(f"[~](LOG): FINGER UP/DOWN: {fingerDown}, AREA: {area}, DEGREE: {degree}, LAST ACTION: {self.CURRENT_ACTION}")
                    #"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    
                    if (self.__MIN_AREA < __area < self.__MAX_AREA) and (self.__DEGREE_MIN < __degree < self.__DEGREE_MAX):

                        if self.__SWIPE == False:
                            """
                            Play Pause
                            """
                            if __fingerDown == self.__THUMB_FINGERUP:
                                __is_play_pause_clicked = self.__hand_track.advanceSelection(fingerNO=self.__PLAY_PAUSE_FINGER_NUM[0], 
                                                                fingerNO2 = self.__PLAY_PAUSE_FINGER_NUM[1], max_len=20) 
                                print(__is_play_pause_clicked)
                                if __is_play_pause_clicked:
                                    self.__CURRENT_ACTION = self.__function_handler.run_play_pause()
                                    print(self.__CURRENT_ACTION)
                                    __is_play_pause_clicked = False   
                            
                            """
                            Full Screen
                            """
                            if __fingerDown == self.__CLOSE_FINGERUP:
                                __is_full_screen = self.__hand_track.advanceSelection(is_single_finger=True, max_len=30)
                                print(__is_full_screen) 
                                if __is_full_screen:
                                    self.__CURRENT_ACTION = self.__function_handler.fullScreen()
                                    print(self.__CURRENT_ACTION)
                                    __is_full_screen = False

                            """
                            Backward
                            """
                            if __fingerDown == self.__BACKWARD_FINGERUP:
                                __is_backward = self.__hand_track.advanceSelection(is_single_finger=True, max_len=10)
                                print(__is_backward) 
                                if __is_backward:
                                    self.__CURRENT_ACTION = self.__function_handler.backward()
                                    print(self.__CURRENT_ACTION)
                                    __is_backward = False
                            
                            """
                            Forward
                            """
                            if __fingerDown == self.__FORWARD_FINGERUP:
                                __is_forward = self.__hand_track.advanceSelection(is_single_finger=True, max_len=10)
                                print(__is_forward) 
                                if __is_forward:
                                    self.__CURRENT_ACTION = self.__function_handler.forward()
                                    print(self.__CURRENT_ACTION)
                                    __is_forward = False
                            
                            """
                            Volume Up
                            """
                            if __fingerDown == self.__VOLUME_UP:
                                __is_volumeup = self.__hand_track.advanceSelection(is_single_finger=True, max_len=10)
                                print(__is_volumeup) 
                                if __is_volumeup:
                                    self.__CURRENT_ACTION = self.__function_handler.vol_inc()
                                    print(self.__CURRENT_ACTION)
                                    __is_volumeup = False
                            
                            """
                            Volume Down
                            """
                            if __fingerDown == self.__VOLUME_DOWN:
                                __is_volumedown = self.__hand_track.advanceSelection(is_single_finger=True, max_len=10)
                                print(__is_volumedown) 
                                if __is_volumedown:
                                    self.__CURRENT_ACTION = self.__function_handler.vol_dec()
                                    print(self.__CURRENT_ACTION)
                                    __is_volumedown = False
                            
                            """
                            Skip Ads
                            """
                            if __fingerDown == self.__SKIP_ADS:
                                __is_skipads = self.__hand_track.advanceSelection(is_single_finger=True, max_len=10)
                                print(__is_skipads) 
                                if __is_skipads:
                                    self.__CURRENT_ACTION = self.__function_handler.skip_ads()
                                    print(self.__CURRENT_ACTION)
                                    __is_skipads = False

                        if self.__SWIPE:
                            """
                            Forward/Backward
                            """
                            __wrist_coord = self.__hand_track.getFindegCoordinate(lmList=__lmList,
                                                                                fingerNo=self.__WRIST_IDX)
                                
                            self.__PTS.appendleft(__wrist_coord)

                            if __fingerDown == self.__FORWARD_FINGERUP:
                                self.__SWIPE_ACTION = 'F/B'
                            
                                self.__frame, self.FRAME_RECTANGLE_COLOR = self.__hand_track.draw(
                                            img = self.__frame,
                                            bbox = None,
                                            is_swipe=True,
                                            draw_hand = False,
                                            draw_fancy = False,
                                            is_swipe_type = "F/B"
                                        )

                                self.__DIRECTION = self.__getDirection()
                                print(self.__DIRECTION)

                                if self.__DIRECTION == self.__DIRECTIONS[0]:
                                    self.__CURRENT_ACTION = self.__function_handler.forward()
                                    self.__SWIPE_ACTION = None

                                if self.__DIRECTION == self.__DIRECTIONS[1]:
                                    self.__CURRENT_ACTION = self.__function_handler.backward()
                                    self.__SWIPE_ACTION = None
                            
                            if __fingerDown == self.__VOLUME_UP:
                                self.__SWIPE_ACTION = 'VOL-(U/D)'
                            
                                self.__frame, self.FRAME_RECTANGLE_COLOR = self.__hand_track.draw(
                                            img = self.__frame,
                                            bbox = None,
                                            is_swipe=True,
                                            draw_hand = False,
                                            draw_fancy = False,
                                            is_swipe_type = "VOL"
                                        )

                                self.__DIRECTION = self.__getDirection()
                                print(self.__DIRECTION)

                                if self.__DIRECTION == self.__DIRECTIONS[2]:
                                    self.__CURRENT_ACTION = self.__function_handler.vol_inc()
                                    self.__SWIPE_ACTION = None

                                if self.__DIRECTION == self.__DIRECTIONS[3]:
                                    self.__CURRENT_ACTION = self.__function_handler.vol_dec()
                                    self.__SWIPE_ACTION = None

                            
                            if __fingerDown == self.__SWIPE_PINKY and self.__SWIPE_ACTION != None:
                                if self.__START_SWIPE == False:
                                    self.__START_SWIPE = True
                                if self.__START_SWIPE:
                                    self.__START_SWIPE = False






                            """
                            Play Pause
                            """
                            if __fingerDown == self.__THUMB_FINGERUP:
                                __is_play_pause_clicked = self.__hand_track.advanceSelection(fingerNO=self.__PLAY_PAUSE_FINGER_NUM[0], 
                                                                fingerNO2 = self.__PLAY_PAUSE_FINGER_NUM[1], max_len=20) 
                                #print(__is_play_pause_clicked)
                                if __is_play_pause_clicked:
                                    self.__CURRENT_ACTION = self.__function_handler.run_play_pause()
                                    #print(self.__CURRENT_ACTION)
                                    __is_play_pause_clicked = False  

                            """
                            Full Screen
                            """
                            if __fingerDown == self.__CLOSE_FINGERUP:
                                __is_full_screen = self.__hand_track.advanceSelection(is_single_finger=True, max_len=30)
                                #print(__is_full_screen) 
                                if __is_full_screen:
                                    self.__CURRENT_ACTION = self.__function_handler.fullScreen()
                                    #print(self.__CURRENT_ACTION)
                                    __is_full_screen = False

                            """
                            Skip Ads
                            """
                            if __fingerDown == self.__SKIP_ADS:
                                __is_skipads = self.__hand_track.advanceSelection(is_single_finger=True, max_len=10)
                                #print(__is_skipads) 
                                if __is_skipads:
                                    self.__CURRENT_ACTION = self.__function_handler.skip_ads()
                                    #print(self.__CURRENT_ACTION)
                                    __is_skipads = False


                """
                Show the Last action
                """
                cv2.putText(img = self.__frame,
                            text = f"{self.__CURRENT_ACTION}",
                            org = self.__CURRENT_ACTION_COORDINATES,
                            fontFace = self.__TEXT_FONT,
                            fontScale = self.__CURRENT_ACTION_TEXT_FONTSCALE,
                            color = random.choice(self.__CURRENT_ACTION_COLOR),
                            thickness = self.__CURRENT_ACTION_TEXT_THICKNESS)

                """
                Display the Frame.
                """
                cv2.imshow("LIVE...", self.__frame)
                if self.__SWIPE:
                    self.__COUNTER += 1

                """
                Check for exit
                """
                self.__check_exit()

        if not __VALID_CHOICE:
            print('\n\n\t[!] Enter correct Choice [youtube/vlc]\n\n')
            try:quit()
            except:exit()

    def __check_exit(self):
        if cv2.waitKey(1) == ord(self.__ESCAPE):
            self.__START_CAM = False
