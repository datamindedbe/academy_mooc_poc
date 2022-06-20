#%%
import csv
import json
import pandas as pd
from pathlib import Path
import random
import re

pd.set_option('display.max_columns', None)

KAGGLE_DATASET = Path("./data")
CREDITS_DATASET = KAGGLE_DATASET/Path("raw_credits.csv")
KEYWORDS_DATASET = KAGGLE_DATASET/Path("raw_keywords.csv")
MOVIES_METADATA_DATASET = KAGGLE_DATASET/Path("raw_movies_metadata.csv")

MINIMAL_BUDGET = 0
MINIMAL_REVENUE = 0
MINIMAL_VOTE_COUNT = 0
MINIMAL_VOTE_AVERAGE = 0
PERCENTAGE_OF_FILTERED_OUT_MOVIES_TO_KEEP = 5

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


def run_minimal_movies_metadata_cleaning(df_movies_metadata):
    df_movies_metadata = df_movies_metadata[df_movies_metadata["budget"].str.isnumeric()]
    df_movies_metadata["vote_count"] = df_movies_metadata["vote_count"].fillna(0)
    df_movies_metadata = df_movies_metadata.astype({
        "vote_count": int,
        })
    df_movies_metadata = df_movies_metadata[(df_movies_metadata["vote_count"] > MINIMAL_VOTE_COUNT) \
        & (df_movies_metadata["adult"] == "False")]
    df_movies_metadata = df_movies_metadata.drop(["vote_count", "adult"], axis=1, inplace=False)
    return df_movies_metadata


def run_expected_movies_metadata_transformation(df_movies_metadata):
    df_movies_metadata = df_movies_metadata[df_movies_metadata["budget"].str.isnumeric()]
    df_movies_metadata = df_movies_metadata.astype({
        "budget": float,
        "vote_average": float,
        "id": int
        })

    df_movies_metadata = df_movies_metadata[(df_movies_metadata["budget"] > MINIMAL_BUDGET) \
        & (df_movies_metadata["budget"] > MINIMAL_REVENUE) \
        & (df_movies_metadata["vote_average"] > MINIMAL_VOTE_AVERAGE) \
        & (~df_movies_metadata["release_date"].isna()) \
        & (~df_movies_metadata["runtime"].isna())]

    df_movies_metadata = df_movies_metadata.drop(["belongs_to_collection"], axis=1, inplace=False)
    df_movies_metadata["genres"] = df_movies_metadata["genres"].apply(extract_json_name_as_stringlist)
    df_movies_metadata["overview"] = df_movies_metadata["overview"].replace(r'\n',' ', regex=True).replace(',','', regex=True)

    df_movies_metadata["production_companies"] = df_movies_metadata["production_companies"].apply(extract_json_name_as_stringlist)
    df_movies_metadata["production_countries"] = df_movies_metadata["production_countries"].apply(extract_json_name_as_stringlist)
    df_movies_metadata["spoken_languages"] = df_movies_metadata["spoken_languages"].apply(extract_json_name_as_stringlist)

    return df_movies_metadata


def process_movies_metadata(df_movies_metadata):
    df_movies_metadata = pd.read_csv(MOVIES_METADATA_DATASET)
    df_movies_metadata = df_movies_metadata.astype({ "id": str})
    df_movies_metadata = run_minimal_movies_metadata_cleaning(df_movies_metadata)
    orignal_ids_list = df_movies_metadata["id"].to_list()

    transformed_df_movies_metadata = run_expected_movies_metadata_transformation(df_movies_metadata)
    
    movies_kept = list(map(str, transformed_df_movies_metadata["id"].to_list()))
    deleted_movies = [item for item in orignal_ids_list if item not in movies_kept]
    percentage_noise = len(deleted_movies) * PERCENTAGE_OF_FILTERED_OUT_MOVIES_TO_KEEP // 100
    deleted_movies_to_keep = [deleted_movies[i] for i in random.sample(range(len(deleted_movies)), percentage_noise)]
    all_movies_to_keep = deleted_movies_to_keep + movies_kept

    lightweight_raw_df_movies_metadata = df_movies_metadata[df_movies_metadata["id"].isin(all_movies_to_keep)]

    return transformed_df_movies_metadata, lightweight_raw_df_movies_metadata, all_movies_to_keep


def keep_json_fields(jsons_list_string, fields, max_entries):
    simplified_list = []
    regex_dict = re.compile(r"({.*?})")
    for idx, entry in enumerate(regex_dict.findall(jsons_list_string)):
        if idx > (max_entries-1):
            break
        filtered_entry = {}
        for field in fields:
            regex = re.compile(r"'"+field+r"': '(.*?)'")
            found_info = regex.findall(entry)
            filtered_entry[field] = found_info.pop(0) if found_info else ""
        
        simplified_list.append(filtered_entry)
    return str(simplified_list)
 

def simplify_df_credits(df_credits):
    df_credits["cast"] = df_credits["cast"].apply(keep_json_fields, args=(["character", "name"], 10,))
    df_credits["crew"] = df_credits["crew"].apply(keep_json_fields, args=(["job", "name"], 10,))
    return df_credits


def process_credits(df_credits, transformed_ids_movies_to_keep, all_movies_to_keep):
    df_credits = df_credits.astype({"id": str})
    df_credits = simplify_df_credits(df_credits)
    lightweight_raw_df_credits = df_credits[df_credits["id"].isin(all_movies_to_keep)]
    df_credits = df_credits[df_credits["id"].isin(transformed_ids_movies_to_keep)]

    cast_regex = re.compile(r"'name': '(.*?)'")
    director_regex = re.compile(r"'Director', 'name': '(.*?)'")

    df_credits['cast'] = df_credits['cast'].apply(lambda x: ', '.join(cast_regex.findall(x)))
    df_credits['director'] = df_credits['crew'].apply(lambda x: ', '.join(director_regex.findall(x)))

    df_credits = df_credits[["cast", "director", "id"]]
    df_credits = df_credits[(df_credits["director"] != "") & (df_credits["cast"] != "")]
    df_credits = df_credits.reset_index(drop=True, inplace=False)

    return df_credits, lightweight_raw_df_credits


def process_keywords(df_keywords, transformed_ids_movies_to_keep, all_movies_to_keep):
    df_keywords = df_keywords.astype({"id": str})
    lightweight_raw_df_keywords = df_keywords[df_keywords["id"].isin(all_movies_to_keep)]
    df_keywords = df_keywords[df_keywords["id"].isin(transformed_ids_movies_to_keep)]
    df_keywords["keywords"] = df_keywords["keywords"].apply(extract_json_name_as_stringlist)
    return df_keywords, lightweight_raw_df_keywords


def export_datasets(datasets_to_export, destination_folder, header):
    for dataset in datasets_to_export:
        datasets_to_export[dataset].to_csv(destination_folder/f"{dataset}.csv", 
                                           sep=',', 
                                           encoding='utf-8',
                                           index=False,
                                           header=header, 
                                           quoting=csv.QUOTE_ALL)


if __name__=="__main__":
    df_movies_metadata = pd.read_csv(MOVIES_METADATA_DATASET)
    df_credits = pd.read_csv(CREDITS_DATASET)
    df_keywords = pd.read_csv(KEYWORDS_DATASET)
    
    transformed_df_movies_metadata, lightweight_raw_df_movies_metadata, all_movies_to_keep = process_movies_metadata(df_movies_metadata)
    transformed_ids_movies_to_keep = df_movies_metadata["id"].tolist()

    transformed_df_credits, lightweight_raw_df_credits = process_credits(df_credits, transformed_ids_movies_to_keep, all_movies_to_keep)
    transformed_df_keywords, lightweight_raw_df_keywords = process_keywords(df_keywords, transformed_ids_movies_to_keep, all_movies_to_keep)

    export_datasets(destination_folder=KAGGLE_DATASET,
                    header = False,
                    datasets_to_export={
                        "transformed_movies_metadata": transformed_df_movies_metadata,
                        "transformed_keywords_cleaned": transformed_df_keywords,
                        "transformed_credits_cleaned": transformed_df_credits                    
                    })

    export_datasets(destination_folder=KAGGLE_DATASET,
                    header = True,
                    datasets_to_export={
                        "lightweight_raw_movies_metadata": lightweight_raw_df_movies_metadata,
                        "lightweight_raw_keywords": lightweight_raw_df_keywords,
                        "lightweight_raw_credits": lightweight_raw_df_credits
                    })

# %%
