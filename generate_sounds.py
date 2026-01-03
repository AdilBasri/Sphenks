# generate_sounds.py
import wave
import math
import struct
import random
import os

# Ses Ayarları
SAMPLE_RATE = 44100

def save_wav(filename, data):
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    
    # Veriyi 16-bit integer'a çevir
    packed_data = b''
    for v in data:
        # Clipping önleme
        v = max(-1.0, min(1.0, v))
        packed_data += struct.pack('<h', int(v * 32767))
    
    with wave.open(f"sounds/{filename}", 'w') as f:
        f.setnchannels(1) # Mono
        f.setsampwidth(2) # 16-bit
        f.setframerate(SAMPLE_RATE)
        f.writeframes(packed_data)
    print(f"Generated: sounds/{filename}")

def generate_noise(duration):
    return [random.uniform(-1, 1) * (1 - t/duration) for t in [i/SAMPLE_RATE for i in range(int(duration*SAMPLE_RATE))]]

def generate_square(freq, duration):
    data = []
    for i in range(int(duration * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        # Decay (Sönümlenme)
        val *= (1 - t/duration)
        data.append(val * 0.5)
    return data

def generate_sine(freq, duration):
    data = []
    for i in range(int(duration * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        val = math.sin(2 * math.pi * freq * t)
        val *= (1 - t/duration)
        data.append(val * 0.5)
    return data

def generate_coin():
    # Çift tonlu (High-High)
    part1 = generate_square(1200, 0.1)
    part2 = generate_square(1600, 0.2)
    return part1 + part2

def generate_hit():
    # Düşük frekanslı kare dalga + noise
    data = []
    duration = 0.15
    for i in range(int(duration * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        freq = 200 - (t * 1000) # Pitch drop
        val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        val *= (1 - t/duration)
        data.append(val * 0.5)
    return data

def generate_explosion():
    # Uzun noise
    return generate_noise(0.4)

def generate_gameover():
    # Azalan ton
    data = []
    duration = 1.0
    for i in range(int(duration * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        freq = 300 * (1 - t/duration)
        val = math.sin(2 * math.pi * freq * t)
        if i % 100 < 50: val = 0 # Tremolo
        data.append(val * 0.5)
    return data

def generate_place():
    # Kısa "tık" sesi
    return generate_sine(400, 0.05)

def generate_select():
    return generate_sine(600, 0.05)

if __name__ == "__main__":
    print("Generating SFX...")
    save_wav("place.wav", generate_place())
    save_wav("clear.wav", generate_coin())      # Satır silme
    save_wav("explosion.wav", generate_explosion()) # Büyük patlama
    save_wav("gameover.wav", generate_gameover())
    save_wav("select.wav", generate_select())   # Buton sesi
    save_wav("hit.wav", generate_hit())         # Hata/Yerleşememe
    print("Done! 'sounds' folder ready.")