import os

def split_large_file(file_path, chunk_size):
    """
    Splits a large file into smaller chunks of a given size.

    Args:
        file_path (str): The path to the large file to split.
        chunk_size (int): The maximum size of each chunk in bytes.

    Returns:
        list: A list of file paths for the generated chunks.
    """
    file_size = os.path.getsize(file_path)
    file_name, file_ext = os.path.splitext(file_path)
    chunks = []

    with open(file_path, "rb") as file:
        chunk_index = 0
        while chunk := file.read(chunk_size):
            chunk_path = f"{file_name}_part{chunk_index + 1}{file_ext}"
            with open(chunk_path, "wb") as chunk_file:
                chunk_file.write(chunk)
            chunks.append(chunk_path)
            chunk_index += 1

    return chunks

