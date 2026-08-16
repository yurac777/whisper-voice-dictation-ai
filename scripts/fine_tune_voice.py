#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎙️ Whisper Voice Fine-Tuning & Personal Voice Adaptation Toolkit
===============================================================
Automated script for fine-tuning OpenAI Whisper on personal voice recordings,
training LoRA adapters, merging weights, and exporting to CTranslate2 (faster-whisper).

Usage:
    python scripts/fine_tune_voice.py --data_dir logs/recordings --base_model openai/whisper-small --epochs 5 --export_ct2
"""

import os
import sys
import glob
import json
import argparse
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Union

# -------------------------------------------------------------
# Hotfix: Bypass torchao compatibility bug in PEFT / Google Colab
# -------------------------------------------------------------
try:
    import peft.import_utils
    peft.import_utils.is_torchao_available = lambda: False
    import peft.tuners.lora.torchao
    peft.tuners.lora.torchao.is_torchao_available = lambda: False
    peft.tuners.lora.torchao.dispatch_torchao = lambda *args, **kwargs: None
except Exception:
    pass

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("VoiceFineTuner")

def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune Whisper on local personal voice dataset.")
    parser.add_argument("--data_dir", type=str, default="logs/recordings", help="Path to recordings directory with .wav and .txt pairs")
    parser.add_argument("--history_file", type=str, default="logs/recordings/dictation_history.jsonl", help="Optional path to dictation_history.jsonl")
    parser.add_argument("--base_model", type=str, default="openai/whisper-small", help="Hugging Face base model (e.g. openai/whisper-small, openai/whisper-large-v3-turbo)")
    parser.add_argument("--output_dir", type=str, default="models/whisper-custom-voice", help="Path to save merged HuggingFace model")
    parser.add_argument("--ct2_output_dir", type=str, default="models/faster-whisper-custom-voice", help="Path to save CTranslate2 model for faster-whisper")
    parser.add_argument("--language", type=str, default="Russian", help="Target language (e.g. Russian, English)")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Per-device training batch size")
    parser.add_argument("--learning_rate", type=float, default=1e-4, help="Learning rate for LoRA adapter")
    parser.add_argument("--export_ct2", action="store_true", default=True, help="Automatically convert merged model to CTranslate2 format")
    return parser.parse_args()

def collect_dataset(data_dir: str, history_file: str = None) -> List[Dict[str, str]]:
    """Scan directory for matching .wav and .txt pairs or parse dictation_history.jsonl."""
    samples = []
    
    # 1. Parse JSONL if present
    if history_file and os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        wav_path = entry.get("audio_file")
                        text = entry.get("text", "").strip()
                        if wav_path and os.path.exists(wav_path) and text:
                            samples.append({"audio": wav_path, "text": text})
            if samples:
                logger.info(f"Loaded {len(samples)} samples from JSONL history: {history_file}")
                return samples
        except Exception as e:
            logger.warning(f"Failed to parse JSONL history ({e}), falling back to file scanning.")

    # 2. Scan for matching .wav and .txt files
    wav_files = glob.glob(os.path.join(data_dir, "*.wav")) + glob.glob(os.path.join(data_dir, "**", "*.wav"), recursive=True)
    for wav in set(wav_files):
        txt = os.path.splitext(wav)[0] + ".txt"
        if os.path.exists(txt):
            try:
                with open(txt, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                if text:
                    samples.append({"audio": wav, "text": text})
            except Exception as e:
                logger.warning(f"Error reading transcript for {wav}: {e}")

    logger.info(f"Collected {len(samples)} valid audio-transcript pairs from {data_dir}")
    return samples

def run_training(args):
    try:
        import peft.import_utils
        peft.import_utils.is_torchao_available = lambda: False
        import peft.tuners.lora.torchao
        peft.tuners.lora.torchao.is_torchao_available = lambda: False
        peft.tuners.lora.torchao.dispatch_torchao = lambda *args, **kwargs: None
    except Exception:
        pass

    try:
        import torch
        import torchaudio
        from datasets import Dataset, Audio
        from transformers import (
            WhisperFeatureExtractor,
            WhisperTokenizer,
            WhisperProcessor,
            WhisperForConditionalGeneration,
            Seq2SeqTrainingArguments,
            Seq2SeqTrainer
        )
        from peft import LoraConfig, get_peft_model, PeftModel
    except ImportError as e:
        logger.error(
            f"Missing required fine-tuning dependencies: {e}\n"
            "Please install fine-tuning requirements:\n"
            "pip install torch torchaudio transformers datasets peft accelerate evaluate ctranslate2"
        )
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device for training: {device}")
    if device == "cpu":
        logger.warning("Training on CPU will be slow! We recommend using an NVIDIA GPU or Google Colab (T4/V100).")

    samples = collect_dataset(args.data_dir, args.history_file)
    if len(samples) < 5:
        logger.error(f"Dataset too small ({len(samples)} samples). Please record at least 10-20 voice clips before fine-tuning.")
        sys.exit(1)

    logger.info(f"Initializing feature extractor & tokenizer from {args.base_model}...")
    feature_extractor = WhisperFeatureExtractor.from_pretrained(args.base_model)
    tokenizer = WhisperTokenizer.from_pretrained(args.base_model, language=args.language, task="transcribe")
    processor = WhisperProcessor.from_pretrained(args.base_model, language=args.language, task="transcribe")

    # Prepare HuggingFace dataset
    raw_dataset = Dataset.from_dict({
        "audio": [s["audio"] for s in samples],
        "text": [s["text"] for s in samples]
    }).cast_column("audio", Audio(sampling_rate=16000))

    def prepare_dataset(batch):
        audio = batch["audio"]
        batch["input_features"] = feature_extractor(audio["array"], sampling_rate=audio["sampling_rate"]).input_features[0]
        batch["labels"] = tokenizer(batch["text"]).input_ids
        return batch

    logger.info("Processing audio features and tokenizing transcripts...")
    processed_dataset = raw_dataset.map(prepare_dataset, remove_columns=["audio", "text"])

    # Load base model
    logger.info(f"Loading Whisper model {args.base_model}...")
    model = WhisperForConditionalGeneration.from_pretrained(args.base_model)
    model.config.forced_decoder_ids = None
    model.config.suppress_tokens = []

    # Configure LoRA (Parameter-Efficient Fine-Tuning)
    logger.info("Configuring LoRA adapter...")
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none"
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    @dataclass
    class DataCollatorSpeechSeq2SeqWithPadding:
        processor: Any
        def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
            input_features = [{"input_features": feature["input_features"]} for feature in features]
            batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
            label_features = [{"input_ids": feature["labels"]} for feature in features]
            labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
            labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
            if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
                labels = labels[:, 1:]
            batch["labels"] = labels
            return batch

    data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

    training_args = Seq2SeqTrainingArguments(
        output_dir="./tmp_whisper_lora",
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=2,
        learning_rate=args.learning_rate,
        warmup_steps=10,
        max_steps=len(samples) * args.epochs // args.batch_size,
        gradient_checkpointing=True,
        fp16=torch.cuda.is_available(),
        save_strategy="no",
        logging_steps=5,
        report_to=[]
    )

    trainer_kwargs = {
        "args": training_args,
        "model": model,
        "train_dataset": processed_dataset,
        "data_collator": data_collator,
    }

    try:
        trainer = Seq2SeqTrainer(**trainer_kwargs, processing_class=processor.feature_extractor)
    except TypeError:
        trainer = Seq2SeqTrainer(**trainer_kwargs, tokenizer=processor.feature_extractor)

    logger.info("Starting LoRA fine-tuning on personal voice dataset...")
    trainer.train()
    logger.info("Fine-tuning completed successfully!")

    # Merge LoRA weights back into base model
    logger.info("Merging LoRA adapter weights into base Whisper checkpoint...")
    merged_model = model.merge_and_unload()
    os.makedirs(args.output_dir, exist_ok=True)
    merged_model.save_pretrained(args.output_dir)
    processor.save_pretrained(args.output_dir)
    logger.info(f"Merged model saved to: {args.output_dir}")

    # Convert to CTranslate2 (faster-whisper format)
    if args.export_ct2:
        logger.info(f"Converting merged model to CTranslate2 format -> {args.ct2_output_dir}...")
        try:
            import subprocess
            cmd = [
                sys.executable, "-m", "ctranslate2.converters.transformers",
                "--model", args.output_dir,
                "--output_dir", args.ct2_output_dir,
                "--quantization", "float16" if torch.cuda.is_available() else "int8",
                "--force"
            ]
            subprocess.run(cmd, check=True)
            logger.info("=" * 60)
            logger.info("🎉 SUCCESS! Custom Voice Model is ready for Whisper Voice AI!")
            logger.info(f"CTranslate2 Model Path: {os.path.abspath(args.ct2_output_dir)}")
            logger.info("To use this model in your application:")
            logger.info(f"  python main.py --model {os.path.abspath(args.ct2_output_dir)}")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"CTranslate2 conversion failed: {e}. You can manually run:\nct2-transformers-converter --model {args.output_dir} --output_dir {args.ct2_output_dir} --quantization float16")

if __name__ == "__main__":
    cli_args = parse_args()
    run_training(cli_args)
