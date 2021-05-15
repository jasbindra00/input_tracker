from pynput import mouse
from pynput import keyboard
from threading import Thread
from enum import Enum
import time
import queue


#             _____          _ _____      _         
#            |____ |        | |  _  |    | |        
#   _____   __   / /_ __ ___| | |/' | ___| | ___ __ 
#  / _ \ \ / /   \ \ '__/ __| |  /| |/ __| |/ / '__|
# | (_) \ V /.___/ / | | (__| \ |_/ / (__|   <| |   
#  \___/ \_/ \____/|_|  \___|_|\___/ \___|_|\_\_|   
# I am not responsible for anything that you do with my code. All code made by me is for educational purposes.

                                                  

class EventType(Enum):
    NONE = -1
    KEYPRESSED = 0
    KEYRELEASED = 1
    SCROLL_UP = 2
    SCROLL_DOWN = 3
    SCROLL_LEFT = 4
    SCROLL_RIGHT = 5
    MOUSECLICKED = 6
    MOUSERELEASED = 7
    MOUSEMOVED = 8

class EventInfo:
    
    def __init__(self, event_type, event_info, tplus):
        self.event_type = event_type
        self.event_info = event_info
        self.tplus = tplus
    
    def __str__(self):
        return self.event_type.name + " " + str(self.event_info) + " " + str(self.tplus)
    
class InputTracker:




    def __init__(self):
        self.event_queue = queue.Queue()
        self.file_buffer = ""
        self.active = False

    def writeFile(self, file_name, file_contents):
        file = open(file_name, "w")
        file.write(file_contents)
        file.close()
   

    def registerEvent(self, event_type, event_info):
        if event_type == None: return
        self.event_queue.put(EventInfo(event_type, event_info, time.time()-self.start_time ))
    
    def processEventQueue(self):
        while self.active:
            event = self.event_queue.get()
            if event == None: continue
            event_info = event.__str__()
            if self.print_events:
                print(event_info)
            self.file_buffer = self.file_buffer + event_info + "\n"
            

    
    def on_move(self,x, y):
        self.registerEvent(EventType.MOUSEMOVED, (x,y))
        return self.active

    def on_click(self,x, y, button, pressed):
        self.registerEvent(EventType.MOUSECLICKED, (x,y))
        return self.active
     
 

    def on_scroll(self,x, y, dx, dy):
        scroll_y = EventType.SCROLL_UP if dy > 0 else EventType.SCROLL_DOWN if dy < 0 else EventType.NONE
        scroll_x = EventType.SCROLL_LEFT if dx < 0 else EventType.SCROLL_RIGHT if dx > 0 else EventType.NONE

        self.registerEvent(scroll_x, dx)
        self.registerEvent(scroll_y, dy)
        return self.active

        


    def on_press(self,key):
        if key == keyboard.Key.f11 and self.previous_button == keyboard.Key.ctrl_l: self.active = False
        else: self.registerEvent(EventType.KEYPRESSED, key)

        self.previous_button = key
        return self.active

    def on_release(self, key):
        self.registerEvent(EventType.KEYRELEASED, key)
        return self.active
    
    def startTracking(self, track_mouse = True, track_keyboard = True, print_events = True, write_events_path = None):
        self.write_events_path = write_events_path
        self.print_events = print_events

        if track_mouse:
            #create listening thread
            self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll)
            self.mouse_listener.start()


        if track_keyboard:
            self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)

            self.keyboard_listener.start()
            self.previous_button = None
         
        self.active = True  
        self.start_time = time.time()
        queue_processor = Thread(target=self.processEventQueue)
        queue_processor.start()

        
        if track_mouse: self.mouse_listener.join()
        if track_keyboard: self.keyboard_listener.join()

        if write_events_path is not None:
            self.writeFile(write_events_path, self.file_buffer)


    



    def __del__(self):


        print("destructing")

tracker = InputTracker()
write_file = "./trackingres.txt"
tracker.startTracking(track_mouse=True, track_keyboard=True, print_events=True, write_events_path=write_file)



