#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()
    logger.info(" Artifact is being downloaded")
    local_path = wandb.use_artifact("sample.csv:latest").file()

    logger.info(" Reading artifact as a dataframe")
    df = pd.read_csv(local_path)

    logger.info(" Filtering data based on min and max price provided")
    min_price, max_price = args.min_price, args.max_price
    idx = df["price"].between(min_price, max_price)
    df = df[idx].copy()

    logger.info(" Converting last_review column to datetime")
    df["last_review"] = pd.to_datetime(df["last_review"])

    logger.info(" Ensuring longitude and latitudes are within limits")
    idx = df["longitude"].between(-74.25, -73.50) & df["latitude"].between(40.5, 41.2)
    df = df[idx].copy()

    logger.info(" Saving cleaned daa to a csv file")
    df.to_csv("clean_sample.csv", index=False)

    logger.info(" Uploading cleaned data to W&B")
    artifact = wandb.Artifact(
        args.output_artifact, type=args.output_type, description=args.output_description
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Enter the name of the input artifact",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Enter the name of the output artifact",
        required=True,
    )

    parser.add_argument(
        "--output_type", type=str, help="Enter the type of output", required=True
    )

    parser.add_argument(
        "--output_description", type=str, help="Describe the output", required=True
    )

    parser.add_argument(
        "--min_price", type=float, help="Minimum price to be considered", required=True
    )

    parser.add_argument(
        "--max_price", type=float, help="Minimum price to be considered", required=True
    )

    args = parser.parse_args()

    go(args)
