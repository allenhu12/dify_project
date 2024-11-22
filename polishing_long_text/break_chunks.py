import re
import sys

def count_tokens(text: str) -> int:
    """
    Count tokens for both English and Chinese text.
    - For English: splits by whitespace
    - For Chinese: counts each character as a token
    """
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
    
    if has_chinese:
        cleaned_text = re.sub(r'\s+', '', text)
        return len(cleaned_text)
    else:
        return len(text.split())

def split_by_length(text: str, max_tokens: int, is_chinese: bool) -> list:
    """Split text by length when no punctuation is found"""
    chunks = []
    
    if is_chinese:
        chars = list(text.strip())
        current_chunk = []
        current_count = 0
        
        for char in chars:
            if current_count >= max_tokens:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_count = 0
            current_chunk.append(char)
            current_count += 1
            
        if current_chunk:
            chunks.append(''.join(current_chunk))
    else:
        words = text.strip().split()
        current_chunk = []
        current_count = 0
        
        for word in words:
            if current_count >= max_tokens:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_count = 0
            current_chunk.append(word)
            current_count += 1
            
        if current_chunk:
            chunks.append(' '.join(current_chunk))
    
    return chunks

def main(input_text: str) -> dict:
    # Initialize parameters
    token_limit = 1024
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    # Check if text contains Chinese characters
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', input_text))
    
    # Split text based on language
    if has_chinese:
        segments = re.split(r'([。！？])', input_text)
        if len(segments) > 1:
            segments = [''.join(i) for i in zip(segments[0::2], segments[1::2] + [''])]
        else:
            return {"chunks": split_by_length(input_text, token_limit, has_chinese)}
    else:
        segments = re.split(r'([.!?])', input_text)
        if len(segments) > 1:
            segments = [''.join(i) for i in zip(segments[0::2], segments[1::2] + [''])]
        else:
            return {"chunks": split_by_length(input_text, token_limit, has_chinese)}
    
    for segment in segments:
        if not segment.strip():
            continue
            
        segment = segment.strip()
        segment_tokens = count_tokens(segment)
        
        # If segment alone exceeds max tokens, split it
        if segment_tokens > token_limit:
            if current_chunk:
                chunk_text = (''.join(current_chunk) if has_chinese else ' '.join(current_chunk))
                chunks.append(chunk_text)
                current_chunk = []
                current_token_count = 0
            
            sub_chunks = split_by_length(segment, token_limit, has_chinese)
            chunks.extend(sub_chunks)
            continue
        
        # If adding this segment would exceed token limit and we have content,
        # store the current chunk and start a new one
        if current_token_count + segment_tokens > token_limit and current_chunk:
            chunk_text = (''.join(current_chunk) if has_chinese else ' '.join(current_chunk))
            chunks.append(chunk_text)
            current_chunk = []
            current_token_count = 0
            
        # Add segment to current chunk
        current_chunk.append(segment)
        current_token_count += segment_tokens
    
    # Add final chunk if exists
    if current_chunk:
        chunk_text = (''.join(current_chunk) if has_chinese else ' '.join(current_chunk))
        chunks.append(chunk_text)
    
    return {
        "chunks": chunks
    }

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python break_chunks.py <input_file_path>")
        sys.exit(1)
        
    try:
        # Read input from file
        with open(sys.argv[1], 'r', encoding='utf-8') as file:
            input_text = file.read()
            
        # Process the text
        result = main(input_text)
        
        # Print results
        print("Generated chunks:")
        for i, chunk in enumerate(result["chunks"], 1):
            print(f"\nChunk {i}:")
            print(chunk)
            print(f"Approximate tokens: {count_tokens(chunk)}")
            
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
