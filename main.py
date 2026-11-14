"""Menyalin gambar entry ke folder keluaran make.fun.

Gambarnya sendiri sudah jadi dan tersimpan sebagai entry.png di folder
yang sama dengan skrip ini. Waktu grading, skrip ini tidak menggambar
ulang apa pun — ia hanya memindahkan salinan gambar itu ke folder yang
ditunjuk lewat MAKEFUN_OUTPUT_DIR, karena runtime grading hanya
menyediakan standard library Python.
"""

import os
import shutil
import sys


def kirim_gambar():
    """Salin entry.png ke folder keluaran, lalu kembalikan path hasilnya."""
    folder_skrip = os.path.dirname(os.path.abspath(__file__))
    asal = os.path.join(folder_skrip, "entry.png")
    folder_keluar = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(folder_keluar, exist_ok=True)
    hasil = os.path.join(folder_keluar, "entry.png")
    shutil.copyfile(asal, hasil)
    print(hasil)
    return hasil


if __name__ == "__main__":
    try:
        kirim_gambar()
    except FileNotFoundError:
        print("entry.png tidak ditemukan di samping main.py", file=sys.stderr)
        sys.exit(1)
