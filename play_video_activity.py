import cv2
import time
from collections import deque
import argparse
import os 

class VideoLoader:
    def __init__(self, file_path, max_buffered_frames=100):
        self.video=cv2.VideoCapture(file_path)

        fpc=self.video.get(cv2.CAP_PROP_FRAME_COUNT) 
        fps = self.video.get(cv2.CAP_PROP_FPS)
        self.duration = fpc/fps
        self.delay=self.duration/fpc 
        print(f'fps={fps}, fpc={fpc}  duration={self.duration} seconds delay={self.delay} seconds')

        self.buffer=deque(maxlen=max_buffered_frames)
        self.current_sec=0

        #load first frame
        while(self.video.isOpened()):
            ret, frame = self.video.read()
            #current time
            self.current_sec=self.video.get(cv2.CAP_PROP_POS_MSEC)/1000.0
            self.buffer.append(frame)
            break 

        self.current_frame_id=0
        self.count=-1

    def current_frame(self):
        return self.buffer[self.current_frame_id]
    
    def next_frame(self):
        """
        load next frame in the buffer
        """
        self.current_frame_id+=1
        self.count+=1

        if self.current_frame_id<len(self.buffer): # buffer has the frame
            return True
        elif len(self.buffer)<self.buffer.maxlen: # buffer is not fully loaded
            ret=False
            if self.video.isOpened():
                ret, frame = self.video.read()
                self.current_sec=self.video.get(cv2.CAP_PROP_POS_MSEC)/1000.0
            
            if ret==False: return False
            self.buffer.append(frame) 
            
            return True
        else:                                      # buffer is full and requested frame is ahead of buffer
            ret=False
            if self.video.isOpened():
                ret, frame = self.video.read()
                self.current_sec=self.video.get(cv2.CAP_PROP_POS_MSEC)/1000.0
            
            if ret==False: return False
            self.buffer.append(frame)
            self.current_frame_id-=1               # move back the current frame id
            return True
        
    def prev_frame(self):
        if self.current_frame_id>0:
            self.current_frame_id-=1
            if self.count>0:  self.count-=1
            return True 
        else:
            return False
            

    def close(self):
        self.video.release()

#python play_video_activity.py -a noteating -f "C:\Users\noush\Downloads\Eating\Dain Eating 1.mp4"

def main(args):

    file_path=args['file']
    activity_name=args['activity']

    #file_name
    file_name=os.path.basename(file_path)
    file_name=file_name.split('.')[0]
    # print('file name=', file_name)
    
    #file path
    fp=os.path.abspath(file_path)
    fp=fp.replace(fp.split("\\")[-1], "")
    # print('file path=', fp)

    txt_file=fp+file_name+'.txt'
    print('txt file=', txt_file)

    file_txt=open(txt_file, 'a+')
    file_txt.write('-'*10+'\n')
    file_txt.write(activity_name+'\n')


    print('activity name=', activity_name)

    if not os.path.exists(file_path):
        print(f'file {file_path} does not exist')
        return 

    vl=VideoLoader(file_path, max_buffered_frames=500)

    closed=False
    key_pressed=None 
    paused=False

    frame_ids=[]

    while True:
        img=vl.current_frame().copy()

        if vl.current_frame().shape[0]>700:
            w,h,_=vl.current_frame().shape
            scale=0.5
            img=cv2.resize(vl.current_frame(), (int(h*scale), int(w*scale)))

        # frame_no=vl.current_frame_id
        frame_no=vl.count

        if frame_no==1: paused=True


        font = cv2.FONT_HERSHEY_SIMPLEX
        text = 'Frame: ' + str(frame_no)
        cv2.putText(img, text, (10, 50), font, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

        info=f"space: pause/play \nq: quit \na: previous frame \nd: next frame\ns: save frame\nty: -+t\nx: delete last key\ndelay: {vl.delay:.4f} seconds\nloaded_t: {vl.current_sec:0.2f}"
        y0, dy = 100, 20
        for i, line in enumerate(info.split('\n')):
            y = y0 + i*dy
            cv2.putText(img, line, (10, y ), font, 0.7, (0, 255, 255), 1, cv2.LINE_AA)
            # cv2.putText(img, line, (100, y ), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)

        
        cv2.imshow(f'Video activity [start,stop] extraction.  {vl.duration:0.2f} seconds', img)
        #get key pressed
        key_pressed=cv2.waitKey(1)

        
        if not paused and key_pressed & 0xFF == ord(' '):
            paused=True 
        elif paused and key_pressed & 0xFF == ord(' '):
            paused=False
        elif key_pressed & 0xFF == ord('a'):
            # if not vl.prev_frame(): break 
            vl.prev_frame() 
            
        elif key_pressed & 0xFF == ord('d'):
            vl.next_frame()
            # if not vl.next_frame(): break
        
        elif key_pressed & 0xFF == ord('t'):
            vl.delay -= 0.005
            if vl.delay <0.001: vl.delay=0.001
            
        elif key_pressed & 0xFF == ord('y'):
            vl.delay += 0.005
        elif key_pressed & 0xFF == ord('x'): 
            if len(frame_ids)>0:  del frame_ids[-1]
            print(f'frame_ids={frame_ids}')

        elif key_pressed & 0xFF == ord('s'):
            frame_ids.append(frame_no)
            print(f'frame_ids={frame_ids}')

        if key_pressed & 0xFF == ord('q'): 
            break 

        if not paused:
            if not vl.next_frame(): break
        time.sleep(vl.delay)

    file_txt.write(str(frame_ids)+'\n')
    cv2.destroyAllWindows()  


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play video and save frame ids for activity recognition')
    parser.add_argument('-f','--file', help='video file', required=True) 
    parser.add_argument('-a','--activity', help='activity name', default='activity')
    args = vars(parser.parse_args())
    # print(args)

    main(args)

