import pygame
import cv2
import os
import sys

class IntroManager:
    def __init__(self, screen, video_path):
        self.screen = screen
        self.active = True
        self.current_surface = None
        
        # Dosya yolunu garantile
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        abs_path = os.path.join(base_dir, video_path)
        
        if not os.path.exists(abs_path):
            abs_path = os.path.join(os.path.dirname(base_dir), video_path)

        print(f"DEBUG: Video Path: {abs_path}")
        
        self.cap = cv2.VideoCapture(abs_path)
        
        if not self.cap.isOpened():
            print("CRITICAL ERROR: Video file could not be opened.")
            self.active = False
            return

        # İlk kareyi zorla yükle
        success, frame = self.cap.read()
        if success:
            self.process_frame(frame)
        else:
            print("ERROR: Could not read first frame.")
            self.active = False

    def process_frame(self, frame):
        try:
            # Get target screen dimensions
            target_w, target_h = self.screen.get_size()
            
            # Renk Dönüşümü BGR -> RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize using OpenCV (Much faster than Pygame scale)
            frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            
            # 1. ADIM: Standart Dönüşüm (Bu 'Tepetaklak' veriyor demiştin)
            frame = cv2.transpose(frame)
            frame = cv2.flip(frame, -1) 
            
            # Yüzeye Çevir
            surface = pygame.surfarray.make_surface(frame)

            # 2. ADIM: Tepetaklak görüntüyü 180 derece çevirip düzeltiyoruz
            self.current_surface = pygame.transform.rotate(surface, 180)
        except Exception as e:
            print(f"Frame processing error: {e}")

    def update(self):
        if not self.active:
            return False

        ret, frame = self.cap.read()
        if not ret:
            self.active = False
            return False
        
        self.process_frame(frame)
        return True

    def draw(self):
        if self.current_surface:
            self.screen.blit(self.current_surface, (0, 0))

    def close(self):
        if self.cap:
            self.cap.release()