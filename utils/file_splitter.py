import os
import logging

def split_large_file(file_path, chunk_size):
    file_size = os.path.getsize(file_path)
    file_name, file_ext = os.path.splitext(file_path)
    chunks = []

    try:
        with open(file_path, "rb") as file:
            chunk_index = 0
            while chunk := file.read(chunk_size):
                chunk_path = f"{file_name}_part{chunk_index + 1}{file_ext}"
                with open(chunk_path, "wb") as chunk_file:
                    chunk_file.write(chunk)
                chunks.append(chunk_path)
                chunk_index += 1
    except Exception as e:
        logging.error(f"Error splitting file: {e}")
        for chunk in chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
        raise
    return chunks
