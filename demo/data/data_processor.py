#!/usr/bin/env python3

import pandas as pd
import os
from pathlib import Path
import numpy as np
import argparse
import sys
from typing import Optional, Dict, Any
import logging
from rich.console import Console
from rich.progress import track
from rich.logging import RichHandler
import requests
import time
import io
from PIL import Image
from dataclasses import dataclass
import hashlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("data_processor")
console = Console()


@dataclass
class ImageGenConfig:
    """Configuration for image generation."""

    rate_limit: int = 5
    max_retries: int = 3
    width: int = 512
    height: int = 512
    model_url: str = (
        "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
    )


class ImageGenerator:
    def __init__(self, config: ImageGenConfig, image_folder: str):
        """Initialize the image generator."""
        self.config = config
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable not set")
        self.image_folder = image_folder
        os.makedirs(self.image_folder, exist_ok=True)

    def generate_prompt(self, title: str, description: str) -> str:
        """Generate an optimized prompt from product data."""
        # Combine title and description, but prioritize title
        base_prompt = f"Professional product photo of {title}. {description[:100]}"
        # Add style guidance for better product images
        return f"{base_prompt} Professional lighting, white background, high resolution, product photography style"

    def query(self, payload: Dict) -> Optional[tuple]:
        """Send request to the API."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.config.model_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(f"Request failed: {response.status_code}, {response.content}")
            return None

        content_type = response.headers.get("Content-Type")
        if content_type not in ["image/jpeg", "image/png"]:
            logger.error(f"Unexpected content type: {content_type}")
            return None

        return response.content, content_type

    def generate_image(self, title: str, description: str) -> Optional[str]:
        """Generate an image from product data."""
        prompt = self.generate_prompt(title, description)

        # Create a deterministic filename based on the prompt
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:10]

        retries = 0
        while retries < self.config.max_retries:
            try:
                response_data = self.query(
                    {
                        "inputs": prompt,
                        "parameters": {
                            "width": self.config.width,
                            "height": self.config.height,
                        },
                    }
                )

                if response_data is None:
                    raise ValueError("Invalid image data returned")

                image_bytes, content_type = response_data
                extension = "jpg" if content_type == "image/jpeg" else "png"
                filename = f"product_{prompt_hash}.{extension}"
                image_path = os.path.join(self.image_folder, filename)

                image = Image.open(io.BytesIO(image_bytes))
                image.save(image_path, quality=95)

                logger.info(f"Image generated and saved: {image_path}")
                return image_path

            except Exception as e:
                logger.error(f"Error generating image: {e}")
                retries += 1
                time.sleep(self.config.rate_limit * retries)

        logger.error("Failed to generate image after maximum retries")
        return None


class ProductDataProcessor:
    def __init__(
        self,
        input_file: str,
        output_dir: str = "demo/data",
        currency: str = "USD",
        verbose: bool = False,
        generate_images: bool = False,
        max_rows: Optional[int] = None,
    ):
        """Initialize the data processor."""
        self.input_file = input_file
        self.output_dir = output_dir
        self.currency = currency.upper()
        self.verbose = verbose
        self.generate_images = generate_images
        self.max_rows = max_rows
        self.required_columns = {
            "product_id": "int",
            "title": "str",
            "description": "str",
            "price": "float",
            "image_path": "str",
        }

        if generate_images:
            image_config = ImageGenConfig()
            self.image_generator = ImageGenerator(
                image_config, os.path.join(output_dir, "product_images")
            )

    def log(self, message: str, level: str = "info") -> None:
        """Log messages based on verbosity level."""
        if self.verbose or level != "debug":
            getattr(logger, level)(message)

    def validate_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean the input dataframe."""
        # Apply row limit if specified
        if self.max_rows is not None:
            df = df.head(self.max_rows)
            self.log(f"Limited dataset to {self.max_rows} rows")

        total_rows = len(df)
        self.log(f"Starting data validation and cleaning for {total_rows} records...")

        # Create product_id if not present
        if "product_id" not in df.columns:
            df["product_id"] = range(1, total_rows + 1)
            self.log("Generated new product IDs")

        # Process each required column
        for col in track(self.required_columns, description="Processing columns"):
            if col not in df.columns:
                if col == "image_path":
                    df[col] = ""
                    self.log("Added empty image_path column")
                elif col == "price":
                    df[col] = np.random.uniform(10, 100, total_rows).round(2)
                    self.log("Generated random prices")
                else:
                    raise ValueError(f"Missing required column: {col}")

        # Clean text fields
        df["description"] = (
            df["description"]
            .fillna("")
            .astype(str)
            .apply(lambda x: x.replace("\n", " ").strip())
        )
        df["title"] = (
            df["title"]
            .fillna("Untitled Product")
            .astype(str)
            .apply(lambda x: x.replace("\n", " ").strip())
        )

        self.log("Text cleaning completed")
        return df

    def process_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process price column, handling different formats and currencies."""
        self.log("Processing price column...")

        price_columns = ["price", "Price", "Price (INR)", "price_inr"]
        found_price_col = next(
            (col for col in price_columns if col in df.columns), None
        )

        if found_price_col:
            # Convert price to float
            df[found_price_col] = (
                df[found_price_col]
                .astype(str)
                .apply(
                    lambda x: float(
                        x.replace(",", "")
                        .replace("$", "")
                        .replace("₹", "")
                        .replace("INR", "")
                        .strip()
                    )
                    if x.strip()
                    else 0.0
                )
            )

            # Handle currency conversion
            if "INR" in found_price_col and self.currency == "USD":
                df[found_price_col] = (df[found_price_col] * 0.012).round(2)
                self.log("Converted prices from INR to USD")
            elif "INR" not in found_price_col and self.currency == "INR":
                df[found_price_col] = (df[found_price_col] * 83.0).round(2)
                self.log("Converted prices from USD to INR")

            # Rename to standardized 'price' column
            if found_price_col != "price":
                df["price"] = df[found_price_col]
                df = df.drop(columns=[found_price_col])
        else:
            df["price"] = np.random.uniform(10, 100, len(df)).round(2)
            self.log("Generated random prices")

        return df

    def get_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistics about the processed data."""
        return {
            "total_products": len(df),
            "price_range": f"{df['price'].min():.2f} - {df['price'].max():.2f} {self.currency}",
            "avg_price": f"{df['price'].mean():.2f} {self.currency}",
            "missing_descriptions": df["description"].isna().sum(),
            "missing_titles": df["title"].isna().sum(),
            "has_images": (df["image_path"] != "").sum(),
        }

    def process(self) -> Optional[str]:
        """Process the input file and save the processed data."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)

            self.log(f"Reading input file: {self.input_file}")
            df = pd.read_csv(self.input_file)

            df = self.validate_and_clean_data(df)
            df = self.process_price(df)

            # Generate images if requested
            if self.generate_images:
                self.log("Generating missing product images...")
                missing_images = df["image_path"].isna() | (df["image_path"] == "")

                for idx in track(
                    df[missing_images].index, description="Generating images"
                ):
                    title = df.loc[idx, "title"]
                    description = df.loc[idx, "description"]

                    image_path = self.image_generator.generate_image(title, description)
                    if image_path:
                        df.loc[idx, "image_path"] = image_path

            final_columns = [
                "product_id",
                "title",
                "description",
                "price",
                "image_path",
            ]
            df = df[final_columns]

            output_file = os.path.join(self.output_dir, "products.csv")
            df.to_csv(output_file, index=False)

            stats = self.get_stats(df)
            console.print("\n[bold green]Processing completed successfully![/]")
            console.print("\n[bold]Dataset Statistics:[/]")
            for key, value in stats.items():
                console.print(f"  {key.replace('_', ' ').title()}: {value}")

            return output_file

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=self.verbose)
            return None


def main():
    parser = argparse.ArgumentParser(
        description="Process product data CSV files for the recommendation system.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.csv -o output_dir                    Process input.csv and save to output_dir
  %(prog)s input.csv --currency INR                   Process with prices in INR
  %(prog)s input.csv -v --generate-images             Process with image generation
  %(prog)s input.csv --generate-images --skip-exists  Generate only missing images
  %(prog)s input.csv --max-rows 100                   Process only the first 100 rows
        """,
    )

    parser.add_argument("input_file", help="Input CSV file to process")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="demo/data",
        help="Output directory for processed files (default: demo/data)",
    )
    parser.add_argument(
        "--currency",
        choices=["USD", "INR"],
        default="USD",
        help="Target currency for prices (default: USD)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--generate-images",
        action="store_true",
        help="Generate images for products missing them",
    )
    parser.add_argument(
        "--skip-exists",
        action="store_true",
        help="Skip image generation if image already exists",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        help="Maximum number of rows to process (default: process all rows)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}")
        sys.exit(1)

    if args.generate_images and not os.getenv("HUGGINGFACE_API_KEY"):
        logger.error(
            "HUGGINGFACE_API_KEY environment variable must be set for image generation"
        )
        sys.exit(1)

    processor = ProductDataProcessor(
        input_file=args.input_file,
        output_dir=args.output_dir,
        currency=args.currency,
        verbose=args.verbose,
        generate_images=args.generate_images,
        max_rows=args.max_rows,
    )

    with console.status("[bold green]Processing data...") as _:
        output_file = processor.process()

    if output_file:
        console.print(f"\n[bold green]Output saved to:[/] {output_file}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
