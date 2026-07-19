import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import cv2
import mediapipe as mp
import numpy as np
import random
import time
import pygame
import customtkinter as ctk
from PIL import Image, ImageTk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AeroMotionGameUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AeroMotion - Gesture Game Edition")
        self.geometry("450x400") 
        self.resizable(False, False)
        
        # --- UI LAYOUT ---
        left_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1e2530")
        left_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(left_frame, text="Vision Processing Stream", font=("Helvetica", 14, "bold"), text_color="#a0aab2").pack(anchor="w", padx=20, pady=15)
        
        self.video_display = ctk.CTkLabel(left_frame, text="Tracking Camera Window Active", text_color="#566270")
        self.video_display.pack(expand=True, fill="both", padx=20, pady=(0, 20))

def main():
    state = {
        "running": True,
        "hand_x": 320,
        "is_pinching": False
    }

    ui_app = AeroMotionGameUI()
    
    cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_MSMF)
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    pygame.init()
    g_width, g_height = 600, 600
    screen = pygame.display.set_mode((g_width, g_height))
    pygame.display.set_caption("AeroMotion Space Game")
    clock = pygame.time.Clock()
    
    player_x = g_width // 2
    player_y = g_height - 80
    
    asteroids = []
    lasers = []
    score = 0
    game_over = False
    laser_cooldown = 0
    
    # Track spawn frame protection buffer
    spawn_grace_timer = time.time() + 3.0 
    
    while state["running"]:
        clock.tick(60)
        screen.fill((11, 15, 25))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state["running"] = False
        
        if cap.isOpened():
            success, frame = cap.read()
            if success:
                frame = cv2.flip(frame, 1)
                small_frame = cv2.resize(frame, (320, 240))
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        landmarks = hand_landmarks.landmark
                        
                        thumb = (int(landmarks[4].x * 320), int(landmarks[4].y * 240))
                        index = (int(landmarks[8].x * 320), int(landmarks[8].y * 240))
                        
                        state["hand_x"] = int(landmarks[8].x * 640)
                        
                        dist = np.hypot(index[0] - thumb[0], index[1] - thumb[1])
                        state["is_pinching"] = (dist < 30) # Calibrated for better sensitivity
                else:
                    state["is_pinching"] = False
                
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img_tk = ImageTk.PhotoImage(image=img)
                ui_app.video_display.configure(image=img_tk, text="")
                ui_app.video_display.image = img_tk

        if not game_over:
            target_x = int(np.interp(state["hand_x"], [50, 590], [0, g_width]))
            player_x += (target_x - player_x) // 3
            player_x = max(20, min(g_width - 50, player_x))
            
            if laser_cooldown > 0:
                laser_cooldown -= 1
            if state["is_pinching"] and laser_cooldown == 0:
                lasers.append([player_x + 17, player_y])
                laser_cooldown = 15
            
            # Spawn obstacles only after the initial 3-second grace period ends
            if time.time() > spawn_grace_timer and random.random() < 0.03:
                asteroids.append([random.randint(20, g_width - 40), 0, random.randint(3, 6)])
            
            for ast in asteroids[:]:
                ast[1] += ast[2]
                if pygame.Rect(player_x, player_y, 35, 35).colliderect(pygame.Rect(ast[0], ast[1], 30, 30)):
                    game_over = True
                if ast[1] > g_height:
                    asteroids.remove(ast)
                    score += 1

            for las in lasers[:]:
                las[1] -= 12
                if las[1] < 0:
                    lasers.remove(las)
                    continue
                for ast in asteroids[:]:
                    if pygame.Rect(las[0], las[1], 6, 15).colliderect(pygame.Rect(ast[0], ast[1], 30, 30)):
                        if ast in asteroids: asteroids.remove(ast)
                        if las in lasers: lasers.remove(las)
                        score += 5
            
            # Visual design rendering
            pygame.draw.polygon(screen, (52, 152, 219), [(player_x + 17, player_y), (player_x, player_y + 35), (player_x + 35, player_y + 35)])
            pygame.draw.circle(screen, (231, 76, 60), (player_x + 17, player_y + 32), 6)
            
            for las in lasers:
                pygame.draw.rect(screen, (241, 196, 15), (las[0], las[1], 6, 15))
            for ast in asteroids:
                pygame.draw.circle(screen, (149, 165, 166), (ast[0] + 15, ast[1] + 15), 15)
                
            # Show a structural countdown message if spawn protection is active
            if time.time() < spawn_grace_timer:
                lbl_font = pygame.font.SysFont("Helvetica", 24, bold=True)
                ready_msg = lbl_font.render(f"GET READY! GET HAND IN FRAME", True, (241, 196, 15))
                screen.blit(ready_msg, (g_width // 2 - 160, g_height // 2 - 20))
        else:
            font = pygame.font.SysFont("Helvetica", 36, bold=True)
            go_txt = font.render("GAME OVER", True, (231, 76, 60))
            score_txt = font.render(f"Final Score: {score}", True, (255, 255, 255))
            hint_txt = pygame.font.SysFont("Helvetica", 18).render("Pinch fingers together to Restart", True, (52, 152, 219))
            
            screen.blit(go_txt, (g_width // 2 - 90, g_height // 2 - 60))
            screen.blit(score_txt, (g_width // 2 - 80, g_height // 2))
            screen.blit(hint_txt, (g_width // 2 - 125, g_height // 2 + 60))
            
            if state["is_pinching"]:
                asteroids.clear()
                lasers.clear()
                score = 0
                game_over = False
                spawn_grace_timer = time.time() + 3.0 # Reset grace timer on restart
                time.sleep(0.4)

        score_banner = pygame.font.SysFont("Helvetica", 20, bold=True).render(f"SCORE: {score}", True, (46, 204, 113))
        screen.blit(score_banner, (20, 20))
        pygame.display.flip()
        
        try:
            ui_app.update_idletasks()
            ui_app.update()
        except Exception:
            state["running"] = False

    cap.release()
    pygame.quit()

if __name__ == "__main__":
    main()