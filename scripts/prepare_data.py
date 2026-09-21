import pandas as pd
import time

def prepare_dataset():
    url = "https://huggingface.co/datasets/dair-ai/emotion/resolve/main/unsplit/train-00000-of-00001.parquet"
    max_retries = 10
    df = None
    
    for attempt in range(max_retries):
        try:
            df = pd.read_parquet(url)
            break
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return

    if df is None:
        return

    emotion_mapping = {
        0: 'sadness', 
        1: 'joy', 
        2: 'love', 
        3: 'anger', 
        4: 'fear', 
        5: 'surprise'
    }
    
    sampled_df = df.groupby('label').sample(n=8, random_state=42)
    remaining_df = df.drop(sampled_df.index)
    extra_df = remaining_df.sample(n=2, random_state=99)
    
    final_df = pd.concat([sampled_df, extra_df]).sample(frac=1, random_state=123).reset_index(drop=True)
    final_df['true_emotion'] = final_df['label'].map(emotion_mapping)
    final_df['tweet_id'] = [f"tweet_{i}" for i in range(50)]
    
    output_file = "../data/emotion_dataset_50.csv"
    final_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    prepare_dataset()
