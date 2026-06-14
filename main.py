import cv2
import mediapipe as mp

# Inisialisasi modul MediaPipe untuk deteksi tangan dan menggambar titik (landmarks)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Buka akses ke Webcam (angka 0 artinya kamera bawaan Mac lo)
cap = cv2.VideoCapture(0)

# Setup model MediaPipe Hands
with mp_hands.Hands(
    min_detection_confidence=0.5, # Toleransi minimal keyakinan AI kalau itu tangan
    min_tracking_confidence=0.5) as hands:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Kamera ga kebaca bro.")
            break

        # Balik gambar secara horizontal (biar kayak ngaca)
        image = cv2.flip(image, 1)
        
        # Konversi warna dari BGR (bawaan OpenCV) ke RGB (yang dibutuhkan MediaPipe)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Proses deteksi tangan di frame ini
        results = hands.process(rgb_image)

        # Kalau tangan terdeteksi, gambar titik dan garisnya
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS)

        # Tampilkan hasil gambarnya di window baru
        cv2.imshow('Kinematic Hand Tracking', image)
        
        # Tekan tombol 'q' di keyboard untuk keluar dari program
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Bersihkan dan tutup akses kamera kalau program berhenti
cap.release()
cv2.destroyAllWindows()