import os

with open("test_file.bin", "wb") as f:
    f.write(os.urandom(5 * 1024 * 1024))  # 5MB of random bytes

print("created test_file.bin, 5MB")
