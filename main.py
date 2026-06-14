import cv2
import mediapipe as mp
import math
import random
import time
import numpy as np
import os
import pygame

# --- INISIALISASI AUDIO (FIX LATENCY) ---
# Buffer dikecilin ke 512 supaya suara instan, ga ada delay dari gerakan
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

def load_sound(file_path):
    if os.path.exists(file_path):
        return pygame.mixer.Sound(file_path)
    return None

sfx_slash = load_sound('assets/slash.wav')
sfx_hit = load_sound('assets/hit.wav')
sfx_bomb = load_sound('assets/bomb.wav')

# --- FUNGSI HIGH SCORE ---
SCORE_FILE = "highscore.txt"

def get_high_score():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            try: return int(f.read())
            except: return 0
    return 0

def save_high_score(score):
    with open(SCORE_FILE, "w") as f:
        f.write(str(score))

# --- FUNGSI OVERLAY GAMBAR TRANSPARAN ---
def overlay_transparent(background, overlay, x, y):
    bg_h, bg_w, _ = background.shape
    ol_h, ol_w = overlay.shape[0], overlay.shape[1]

    if x >= bg_w or y >= bg_h or x + ol_w <= 0 or y + ol_h <= 0:
        return background

    bg_x1, bg_x2 = max(0, x), min(bg_w, x + ol_w)
    bg_y1, bg_y2 = max(0, y), min(bg_h, y + ol_h)
    ol_x1, ol_x2 = max(0, -x), min(ol_w, bg_w - x)
    ol_y1, ol_y2 = max(0, -y), min(ol_h, bg_h - y)

    if overlay.shape[2] == 4:
        alpha_s = overlay[ol_y1:ol_y2, ol_x1:ol_x2, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        for c in range(3):
            background[bg_y1:bg_y2, bg_x1:bg_x2, c] = (
                alpha_s * overlay[ol_y1:ol_y2, ol_x1:ol_x2, c] +
                alpha_l * background[bg_y1:bg_y2, bg_x1:bg_x2, c]
            )
    else:
        background[bg_y1:bg_y2, bg_x1:bg_x2] = overlay[ol_y1:ol_y2, ol_x1:ol_x2]
    return background

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.3)
        self.mp_drawing = mp.solutions.drawing_utils
        self.prev_x, self.prev_y = 0, 0

    def process_frame(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_image)

    def get_index_finger(self, image):
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                h, w, _ = image.shape
                idx_tip = hand_landmarks.landmark[8]
                return int(idx_tip.x * w), int(idx_tip.y * h)
        return None, None

class FallingObject:
    def __init__(self, frame_w, obj_type, image=None):
        self.size = 80
        self.x = random.randint(50, frame_w - self.size - 50)
        self.y = -self.size
        self.speed = random.randint(5, 12) 
        self.obj_type = obj_type
        self.image = image

    def update(self):
        self.y += self.speed

    def draw(self, frame):
        if self.image is not None:
            overlay_transparent(frame, self.image, self.x, self.y)
        else:
            color = (0, 255, 0) if self.obj_type == 'fruit' else (0, 0, 0)
            cv2.circle(frame, (self.x + self.size//2, self.y + self.size//2), self.size//2, color, cv2.FILLED)

    def check_hit(self, cx, cy):
        center_x, center_y = self.x + self.size//2, self.y + self.size//2
        distance = math.hypot(cx - center_x, cy - center_y)
        return distance <= (self.size // 2 + 30)

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    
    fruit_img = cv2.imread('assets/apel.png', cv2.IMREAD_UNCHANGED)
    bomb_img = cv2.imread('assets/bom.png', cv2.IMREAD_UNCHANGED)
    if fruit_img is not None: fruit_img = cv2.resize(fruit_img, (80, 80))
    if bomb_img is not None: bomb_img = cv2.resize(bomb_img, (80, 80))

    high_score = get_high_score()

    def reset_game():
        return 0, time.time(), False, [], False

    score, start_time, game_over, active_objects, score_saved = reset_game()
    game_duration = 30
    SLASH_THRESHOLD = 100
    slash_cooldown = 0 # Mencegah suara pedang nge-spam

    while cap.isOpened():
        success, image = cap.read()
        if not success: break

        image = cv2.flip(image, 1)
        h, w, _ = image.shape

        if not game_over:
            time_left = int(game_duration - (time.time() - start_time))
            if time_left <= 0:
                time_left = 0
                game_over = True
            
            if len(active_objects) < 5 and random.random() < 0.1:
                tipe = 'fruit' if random.random() < 0.8 else 'bomb'
                img_ref = fruit_img if tipe == 'fruit' else bomb_img
                active_objects.append(FallingObject(w, tipe, img_ref))

        # Rendering Header
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), cv2.FILLED)
        cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)
        
        cv2.putText(image, f"SKOR: {score}", (20, 55), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 2)
        cv2.putText(image, f"HIGH SCORE: {high_score}", (w//2 - 150, 55), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 165, 0), 2)
        cv2.putText(image, f"WAKTU: {time_left}s", (w - 280, 55), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 255), 2)

        tracker.process_frame(image)
        cx, cy = tracker.get_index_finger(image)

        if not game_over:
            # --- DETEKSI TEBASAN GLOBAL (Dipisah dari objek) ---
            is_slashing = False
            if slash_cooldown > 0:
                slash_cooldown -= 1

            if cx is not None and cy is not None and tracker.prev_x != 0:
                dist_slash = math.hypot(cx - tracker.prev_x, cy - tracker.prev_y)
                if dist_slash > SLASH_THRESHOLD:
                    is_slashing = True
                    # Cuma puter suara pedang kalau cooldown udah kelar
                    if sfx_slash and slash_cooldown == 0:
                        pygame.mixer.Sound.play(sfx_slash)
                        slash_cooldown = 7 # Jeda 7 frame sebelum bisa bunyi lagi

            # --- VALIDASI TABRAKAN OBJEK ---
            objects_to_keep = []
            for obj in active_objects:
                obj.update()
                obj.draw(image)
                
                is_slashed_obj = False
                # Cek tabrakan cuma kalau lagi nebas
                if is_slashing and obj.check_hit(cx, cy):
                    is_slashed_obj = True
                    if obj.obj_type == 'fruit':
                        score += 1
                        if sfx_hit: pygame.mixer.Sound.play(sfx_hit)
                    elif obj.obj_type == 'bomb':
                        if sfx_bomb: pygame.mixer.Sound.play(sfx_bomb)
                        game_over = True 

                if not is_slashed_obj and obj.y < h:
                    objects_to_keep.append(obj)

            active_objects = objects_to_keep

            # --- RENDER TRACKING JARI ---
            if cx is not None and cy is not None:
                if tracker.prev_x != 0 and tracker.prev_y != 0:
                    cv2.line(image, (tracker.prev_x, tracker.prev_y), (cx, cy), (255, 255, 255), 5)
                cv2.circle(image, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
                tracker.prev_x, tracker.prev_y = cx, cy
            else:
                tracker.prev_x, tracker.prev_y = 0, 0

        else:
            if not score_saved:
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                score_saved = True

            cv2.putText(image, "GAME OVER", (w//2 - 250, h//2 - 50), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 8)
            cv2.putText(image, "Tekan 'R' untuk Restart", (w//2 - 200, h//2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

        cv2.imshow('Kinematic Hand Tracking', image)
        
        key = cv2.waitKey(5) & 0xFF
        if key == ord('q'): break
        elif key == ord('r'):
            score, start_time, game_over, active_objects, score_saved = reset_game()
            tracker.prev_x, tracker.prev_y = 0, 0

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()