#%%
import pandas as pd
from pathlib import Path
import re
import csv
import json

pd.set_option('display.max_columns', None)

KAGGLE_DATASET = Path("~/Desktop/imdb_dataset")
CREDITS_DATASET = KAGGLE_DATASET/Path("credits.csv")
KEYWORDS_DATASET = KAGGLE_DATASET/Path("keywords.csv")
MOVIES_METADATA_DATASET = KAGGLE_DATASET/Path("movies_metadata.csv")

MINIMAL_BUDGET = 0
MINIMAL_REVENUE = 0
MINIMAL_VOTE_COUNT = 0
MINIMAL_VOTE_AVERAGE = 0

def extract_json_name_as_stringlist(row: str):
    try:
        row = row.replace("'","\"")
        json_row = json.loads(row)
        entries = [entry["name"] for entry in json_row]
        if not entries:
            return ""
    except:
        return ""

    return ", ".join(entries)


def process_movies_metadata(df_movies_metadata):
    df_movies_metadata = pd.read_csv(MOVIES_METADATA_DATASET)
    df_movies_metadata = df_movies_metadata[df_movies_metadata["budget"].str.isnumeric()]
    df_movies_metadata["vote_count"] = df_movies_metadata["vote_count"].fillna(0)
    df_movies_metadata = df_movies_metadata.astype({
        "budget": float,
        "vote_count": int,
        "vote_average": float,
        "id": int
        })

    df_movies_metadata = df_movies_metadata[(df_movies_metadata["budget"] > MINIMAL_BUDGET) \
        & (df_movies_metadata["budget"] > MINIMAL_REVENUE) \
        & (df_movies_metadata["adult"] == "False") \
        & (df_movies_metadata["vote_count"] > MINIMAL_VOTE_COUNT) \
        & (df_movies_metadata["vote_average"] > MINIMAL_VOTE_AVERAGE) \
        & (~df_movies_metadata["release_date"].isna()) \
        & (~df_movies_metadata["runtime"].isna())]

    df_movies_metadata = df_movies_metadata.drop(["belongs_to_collection", "adult"], axis=1, inplace=False)
    df_movies_metadata["genres"] = df_movies_metadata["genres"].apply(extract_json_name_as_stringlist)
    df_movies_metadata["overview"] = df_movies_metadata["overview"].replace(r'\n',' ', regex=True).replace(',','', regex=True)

    df_movies_metadata["production_companies"] = df_movies_metadata["production_companies"].apply(extract_json_name_as_stringlist)
    df_movies_metadata["production_countries"] = df_movies_metadata["production_countries"].apply(extract_json_name_as_stringlist)
    df_movies_metadata["spoken_languages"] = df_movies_metadata["spoken_languages"].apply(extract_json_name_as_stringlist)
    return df_movies_metadata

def process_credits(df_credits, ids_movies_to_keep):
    df_credits = df_credits[df_credits["id"].isin(ids_movies_to_keep)]

    cast_regex = re.compile(r"'name': '(.*?)'")
    director_regex = re.compile(r"'Director', 'name': '(.*?)'")

    df_credits['cast'] = df_credits['cast'].apply(lambda x: ', '.join(cast_regex.findall(x)))
    df_credits['director'] = df_credits['crew'].apply(lambda x: ', '.join(director_regex.findall(x)))

    df_credits = df_credits[["cast", "director", "id"]]
    df_credits = df_credits[(df_credits["director"] != "") & (df_credits["cast"] != "")]
    df_credits = df_credits.reset_index(drop=True, inplace=False)

    return df_credits

def process_keywords(df_keywords, ids_movies_to_keep):
    df_keywords = df_keywords[df_keywords["id"].isin(ids_movies_to_keep)]
    df_keywords["keywords"] = df_keywords["keywords"].apply(extract_json_name_as_stringlist)
    return df_keywords

def export_datasets(datasets_to_export, destination_folder):
    for dataset in datasets_to_export:
        datasets_to_export[dataset].to_csv(destination_folder/f"{dataset}.csv", 
                                           sep=',', 
                                           encoding='utf-8',
                                           index=False,
                                           header=False, 
                                           quoting=csv.QUOTE_ALL)

if __name__=="__main__":
    df_movies_metadata = pd.read_csv(MOVIES_METADATA_DATASET)
    df_credits = pd.read_csv(CREDITS_DATASET)
    df_keywords = pd.read_csv(KEYWORDS_DATASET)

    df_movies_metadata = process_movies_metadata(df_movies_metadata)
    ids_movies_to_keep = df_movies_metadata["id"].tolist()

    df_credits = process_credits(df_credits, ids_movies_to_keep)
    df_keywords = process_keywords(df_keywords, ids_movies_to_keep)

    export_datasets(destination_folder=KAGGLE_DATASET,
                    datasets_to_export={
                        "movies_metadata_cleaned": df_movies_metadata,
                        "keywords_cleaned": df_keywords,
                        "credits_cleaned": df_credits
                    })
