import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize

from utils import  get_video_title, get_video_id

# Download necessary NLTK data
nltk.download('punkt')

# Function to add periods every N words
def add_periods(text, n):
    words = text.split()
    punctuated_text = []
    for i in range(0, len(words), n):
        punctuated_text.append(' '.join(words[i:i+n]) + '.')
    return ' '.join(punctuated_text)

# Function to chunk the transcript
def chunk_transcript(text, chunk_size=1000):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield ' '.join(words[i:i + chunk_size])

def count_words(text):
    words = text.split()
    return len(words)

# Function to extract the most relevant sentences using TF-IDF
def extract_relevant_sentences(chunk, percentage=10):
    sentences = sent_tokenize(chunk)
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)
    scores = X.sum(axis=1).A1
    n_sentences = max(1, int(len(sentences) * percentage / 100))
    ranked_sentences = sorted(((score, sentence, idx) for idx, (sentence, score) in enumerate(zip(sentences, scores))), reverse=True)
    relevant_sentences = [(sentence, idx) for score, sentence, idx in ranked_sentences[:n_sentences]]
    return relevant_sentences

def summarize_transcript(youtube_url, result, chunk_size=1000, period_interval=50):
    # Read the transcript document
    transcript = result

    # Fetch video title
    video_id = get_video_id(youtube_url)
    video_title = get_video_title(video_id)

    # Print word count
    word_count = count_words(transcript)
    print(f"Transcript word count: {word_count}")
    if word_count < 5000:
        print("Transcript is too short to summarize.")
        words = transcript.split()
        intro = ' '.join(words[:50])
        transcript = intro + ' ' + transcript
        transcript = f"Youtube Video Title: {video_title}\n\n" + transcript
        return transcript
    if word_count < 10000: 
        summary_percentage = 50
    elif word_count < 20000: 
        summary_percentage = 30
    else:
        summary_percentage = 20
    # Print the summary percentage used
    print(f"Summary percentage used: {summary_percentage}%")

    # Apply the function to add periods
    transcript_with_periods = add_periods(transcript, n=period_interval)

    # Process the transcript
    rough_summary = []

    for chunk in chunk_transcript(transcript_with_periods, chunk_size):
        relevant_sentences = extract_relevant_sentences(chunk, percentage=summary_percentage)
        rough_summary.extend(relevant_sentences)

    # Sort the rough summary by the original position of the sentences
    rough_summary.sort(key=lambda x: x[1])
    ordered_summary = [sentence for sentence, idx in rough_summary]

    # Combine the rough summary into a single string
    rough_summary_text = ' '.join(ordered_summary)

    # Add an introduction from the first 50 words of the transcript
    words = transcript.split()
    intro = ' '.join(words[:50])
    rough_summary_text = intro + ' ' + rough_summary_text
    # Add the video title to the beginning of the summary
    rough_summary_text = f"Youtube Video Title: {video_title}\n\n" + rough_summary_text
    print(f"Rough summary word count: {count_words(rough_summary_text)}")
    print(f"Rough summary: {rough_summary_text}")
    return rough_summary_text

# Function to summarize the transcript
"""def summarize_transcript(result, chunk_size=1000, period_interval=50):
    # Read the transcript document
    transcript = result

    # Print word count
    word_count = count_words(transcript)
    print(f"Transcript word count: {word_count}")
    if word_count < 1000:
        print("Transcript is too short to summarize.")
        return transcript
    if word_count < 5000: 
        summary_percentage = 20
    elif word_count < 10000: 
        summary_percentage = 10
    else:
        summary_percentage = 5
    # Print the summary percentage used
    print(f"Summary percentage used: {summary_percentage}%")

    # Apply the function to add periods
    transcript_with_periods = add_periods(transcript, n=period_interval)

    # Process the transcript
    rough_summary = []

    for chunk in chunk_transcript(transcript_with_periods, chunk_size):
        relevant_sentences = extract_relevant_sentences(chunk, percentage=summary_percentage)
        rough_summary.extend(relevant_sentences)

    # Sort the rough summary by the original position of the sentences
    rough_summary.sort(key=lambda x: x[1])
    ordered_summary = [sentence for sentence, idx in rough_summary]

    # Combine the rough summary into a single string
    rough_summary_text = ' '.join(ordered_summary)

    words = transcript.split()
    intro = ' '.join(words[:50])
    rough_summary_text = intro + ' ' + rough_summary_text

    print(f"Rough summary word count: {count_words(rough_summary_text)}")
    print(f"Rough summary: {rough_summary_text}")
    return rough_summary_text"""

# Example usage
#file_path = "transcription.txt"
#summarized_text = summarize_transcript(file_path)
