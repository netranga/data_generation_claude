# PDF Q&A Dataset Generator

## Overview
This tool automatically generates high-quality question-answer pairs from PDF documents using Claude 3.5 Sonnet. It's specifically designed to create training datasets for RAG (Retrieval-Augmented Generation) applications, eliminating the need for manual review by Subject Matter Experts (SMEs).

## Key Features
- Extraction of structured Q&A pairs from PDF documents without OCR, leveraging foundational model vision capabilities.
- Generates two distinct, valid answers for each question, enabling contrastive learning techniques.
- Uses Claude Opus to evaluate responses and identify the better answer based on level of detail.

## Value Proposition
1. Reduces the manual effort required by SMEs for creating curated golden evaluation datasets—a cumbersome process often plagued by subjective quality disagreements.
2. Lowers costs significantly through efficient techniques like caching and batching.
3. Enhances contextual awareness and generates higher-quality Q&A pairs by incorporating charts, images, and diagrams.

