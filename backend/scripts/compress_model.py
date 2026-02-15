import os
import gzip
import shutil

def compress_yield_model():
    input_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'yield_model.pkl')
    output_path = input_path + '.gz'
    
    if os.path.exists(input_path):
        print(f"Compressing {input_path}...")
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        orig_size = os.path.getsize(input_path) / (1024*1024)
        comp_size = os.path.getsize(output_path) / (1024*1024)
        
        print(f"Original: {orig_size:.2f} MB")
        print(f"Compressed: {comp_size:.2f} MB")
        
        if comp_size < 100:
            print("SUCCESS! The compressed model fits in GitHub limits (<100MB).")
        else:
            print("WARNING: Even compressed, it's still too big.")
    else:
        print(f"File not found: {input_path}")

if __name__ == "__main__":
    compress_yield_model()
