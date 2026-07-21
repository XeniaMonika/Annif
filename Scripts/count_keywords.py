import json

input_file_small = "Data/Vocabs/keywords_mapped_small.json"
input_file_big = "Data/Vocabs/keywords_mapped_big.json"
input_file_both = "Data/Vocabs/keywords_mapped_both.json"


def count_keywords_under_threshold(file_path, threshold=50):
    """Count how many keywords have count under the threshold."""
    with open(file_path, 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    
    total_count = len(keywords)
    under_threshold = sum(1 for kw in keywords if kw.get('count', 0) < threshold)
    percentage = (under_threshold / total_count * 100) if total_count > 0 else 0
    
    print(f"Keywords with count under {threshold}:")
    print(f"Number: {under_threshold}")
    print(f"Percentage: {percentage:.2f}%")
    
    return under_threshold, percentage


print(count_keywords_under_threshold(input_file_small))
print(count_keywords_under_threshold(input_file_big))
print(count_keywords_under_threshold(input_file_both))