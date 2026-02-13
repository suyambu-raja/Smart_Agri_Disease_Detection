"""Test disease prediction API with a sample image."""
import requests
from PIL import Image
import io

# Create a test leaf-like image (green with some brown spots)
img = Image.new('RGB', (256, 256), color=(50, 150, 50))
# Add some variation
import numpy as np
arr = np.array(img)
# Add brown spots to simulate disease
for _ in range(20):
    x, y = np.random.randint(30, 226, 2)
    arr[y-10:y+10, x-10:x+10] = [139, 90, 43]
img = Image.fromarray(arr)

# Save to buffer
buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)

# Send to API
print("Sending test image to /api/disease/predict/...")
r = requests.post(
    'http://127.0.0.1:8000/api/disease/predict/',
    files={'image': ('test_leaf.jpg', buf, 'image/jpeg')},
)

print("Status:", r.status_code)
print("Response:", r.json())
