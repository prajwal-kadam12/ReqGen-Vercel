import os
import sys
import torch
import gc
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import re
import warnings

# Filter warnings
warnings.filterwarnings('ignore')

class ComprehensiveMeetingSummarizer:
    """
    FINAL VERSION - No hallucinations.
    Ported from notebook for ReqGen Vercel Backend.
    Use existing Whisper loading if possible to save memory, or load separately.
    """
    
    def __init__(self, use_gpu=True, model_name="microsoft/phi-2", existing_whisper=None):
        """Initialize summarizer"""
        
        self.device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"

        print(f"🔧 Summarizer Device: {self.device}")
        
        if self.device == "cuda":
            try:
                print(f"🚀 GPU: {torch.cuda.get_device_name(0)}")
                print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
            except:
                pass
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

        if existing_whisper:
            self.whisper_model = existing_whisper
            print("✅ Using existing Whisper model")
        else:
            self.load_whisper()
            
        self.load_phi2(model_name)
        
    def load_whisper(self):
        """Load Whisper Large"""
        print("📥 Loading Whisper Large...")
        try:
            import whisper
            self.whisper_model = whisper.load_model("large", device=self.device)
            print("✅ Whisper Large loaded")
        except ImportError:
            print("📦 Installing Whisper...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper", "-q"])
            import whisper
            self.whisper_model = whisper.load_model("large", device=self.device)
            print("✅ Whisper Large loaded")
    
    def load_phi2(self, model_name):
        """Load Phi-2"""
        print(f"📥 Loading {model_name}...")
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True
            )
            
            dtype = torch.float16 if self.device == "cuda" else torch.float32
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=dtype,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print(f"✅ {model_name} loaded")
            
        except ImportError:
            print("📦 Installing Transformers...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "transformers", "accelerate", "einops", "-q"])
            self.load_phi2(model_name)  
        except Exception as e:
            print(f"❌ Error loading Phi-2: {e}")
            raise e

    def _manual_clean_repetition(self, text):
        """
        Hard-trims sentences that repeat more than 3 times consecutively.
        This is a safety net for Whisper Large loops.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if not sentences: return text
        
        cleaned = []
        for i, sent in enumerate(sentences):
            # If current sentence is same as last 2, stop adding
            if i > 2 and sent == sentences[i-1] == sentences[i-2]:
                print(f"  ⚠️  Manual Loop Break: Detected repetition of '{sent[:30]}...'")
                break
            cleaned.append(sent)
        return " ".join(cleaned)
        
    def transcribe_audio(self, audio_path, language=None):
        """Transcribe audio with Whisper Large"""
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"❌ Audio file not found: {audio_path}")
        
        file_size = os.path.getsize(audio_path) / (1024 * 1024)
        print(f"\\n🎵 Audio: {os.path.basename(audio_path)} ({file_size:.2f} MB)")
        print(f"⏳ Transcribing with Whisper Large...\\n")
        
        # Whisper transcribe arguments
        transcribe_args = {
            'task': 'translate',
            'language': language,
            'verbose': False,
            'beam_size': 5,
            'best_of': 5,
            # ANTI-LOOPING PARAMETERS START HERE
            'compression_ratio_threshold': 2.4, # Stops if text is too repetitive
            'no_speech_threshold': 0.6,         # Ignores segments with 60%+ silence probability
            'logprob_threshold': -1.0,          # Discards low-confidence text
            'condition_on_previous_text': False # Prevents error in one chunk from poisoning the next
            # ANTI-LOOPING PARAMETERS END HERE
        }
        
        if self.device == "cuda":
            transcribe_args['fp16'] = True
            
        result = self.whisper_model.transcribe(audio_path, **transcribe_args)
        
        raw_text = result['text'].strip()
        
        # Apply manual cleaning in case parameters don't catch a tail-end loop
        text = self._manual_clean_repetition(raw_text)
        
        word_count = len(text.split())
        
        print(f"✅ Transcription complete!")
        print(f"🌍 Language: {result.get('language', 'unknown')}")
        print(f"📝 Words: {word_count:,}")
        print(f"📏 Characters: {len(text):,}\\n")
        
        return {
            'text': text,
            'language': result.get('language'),
            'word_count': word_count
        }

    def calculate_adaptive_length(self, word_count):
        """Calculate adaptive summary length"""
        
        if word_count < 500:
            min_ratio, max_ratio = 0.40, 0.50
            compression = "40-50%"
        elif word_count < 2000:
            min_ratio, max_ratio = 0.30, 0.40
            compression = "30-40%"
        else:
            min_ratio, max_ratio = 0.25, 0.35
            compression = "25-35%"
        
        min_length = max(100, int(word_count * min_ratio))
        max_length = max(200, int(word_count * max_ratio))
        
        if max_length - min_length < 50:
            max_length = min_length + 100
        
        if max_length > 1500:
            max_length = 1500
            min_length = min(min_length, 1200)
        
        print(f"📊 Adaptive Length Calculation:")
        print(f"   Input: {word_count:,} words")
        print(f"   Strategy: Keep {compression} of original")
        print(f"   Target Range: {min_length:,} - {max_length:,} words\\n")
        
        return min_length, max_length
    
    def create_comprehensive_prompt(self, text, meeting_type="general"):
        """Create comprehensive summarization prompt"""
        
        prompt = f"""### Instruction:
You are an expert meeting summarizer. Create a comprehensive summary of the meeting transcript below.

REQUIREMENTS:
1. Include all important information
2. Preserve key decisions and action items
3. Maintain context and specific details
4. Use clear, professional language
5. Be thorough but concise

### Meeting Transcript:
{text}

### Comprehensive Summary:
"""
        return prompt
    
    def _clean_hallucinations(self, text):
        """
        CRITICAL: Remove all hallucinated content
        """
        
        # CRITICAL: Stop at these hallucination triggers
        stop_triggers = [
            "## Exercise",
            "##Exercise",
            "Exercise 1:",
            "Exercise 2:",
            "## Question",
            "##Question",
            "Question:",
            "Answer:",
            "A)",
            "B)",
            "C)",
            "D)",
            "##Your task",
            "##",
            "**Rewrite",
            "Rewrite",
            "Your task",
            "after that",
            "create some",
            "usecase",
            "Instruction:",
            "Task:",
            "Note:",
            "Example:",
            "Following:",
            "Step 1:",
            "First,",
            "Here is",
            "Here's",
            "What were",
            "Why is it",
            "How do you"
        ]
        
        # Find earliest trigger and cut everything after it
        earliest_pos = len(text)
        earliest_trigger = None
        
        for trigger in stop_triggers:
            pos = text.find(trigger)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
                earliest_trigger = trigger
        
        if earliest_trigger:
            # Cut at the trigger
            text = text[:earliest_pos].strip()
            print(f"   ⚠️  Removed hallucination starting with: '{earliest_trigger[:20]}...'")
        
        # Remove trailing incomplete sentences
        if text and text[-1] not in '.!?':
            sentences = re.split(r'[.!?]+', text)
            if len(sentences) > 1:
                text = '.'.join(sentences[:-1]) + '.'
        
        # Clean up whitespace
        text = re.sub(r'\\s+', ' ', text).strip()
        
        return text
    
    def _chunk_intelligently(self, text, max_length=1800):
        """Intelligent chunking for long meetings"""
        
        paragraphs = text.split('\\n\\n')
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para.split())
            
            if current_length + para_length > max_length and current_chunk:
                chunks.append('\\n\\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        if current_chunk:
            chunks.append('\\n\\n'.join(current_chunk))
        
        # Fallback to sentence splitting if still too long (e.g. one huge paragraph)
        final_chunks = []
        for c in chunks:
            if len(c.split()) > max_length:
                 sentences = re.split(r'(?<=[.!?])\\s+', c)
                 current_sub_chunk = []
                 current_sub_length = 0
                 
                 for sent in sentences:
                    sent_length = len(sent.split())
                    if current_sub_length + sent_length > max_length and current_sub_chunk:
                        final_chunks.append(' '.join(current_sub_chunk))
                        current_sub_chunk = [sent]
                        current_sub_length = sent_length
                    else:
                        current_sub_chunk.append(sent)
                        current_sub_length += sent_length
                 
                 if current_sub_chunk:
                    final_chunks.append(' '.join(current_sub_chunk))
            else:
                final_chunks.append(c)

        return final_chunks
    
    def _summarize_with_phi2(self, text, min_length, max_length):
        """Summarize text chunk with Phi-2"""
        
        import torch
        
        prompt = self.create_comprehensive_prompt(text)
        
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                min_new_tokens=min_length,
                temperature=0.3,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1,
                no_repeat_ngram_size=3
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract summary
        if "### Comprehensive Summary:" in generated_text:
            summary = generated_text.split("### Comprehensive Summary:")[-1].strip()
        else:
            summary = generated_text[len(prompt):].strip()
        
        # CRITICAL: Clean hallucinations
        summary = summary.replace("###", "").strip()
        summary = self._clean_hallucinations(summary)
        
        return summary
    
    def summarize_meeting(
        self,
        audio_path,
        meeting_type="general"
    ):
        """Main summarization function"""
        
        print("="*70)
        print("🎯 STARTING COMPREHENSIVE MEETING SUMMARIZATION (Phi-2)")
        print("="*70 + "\\n")
        
        start_time_all = time.time()

        # Step 1: Transcribe
        transcription = self.transcribe_audio(audio_path)
        text = transcription['text']
        word_count = transcription['word_count']
        
        if word_count < 20:
             return {
                'audio_file': os.path.basename(audio_path),
                'language': transcription['language'],
                'transcription': text,
                'summary': text,
                'original_words': word_count,
                'summary_words': word_count,
                'compression_percent': 0,
                'processing_time': time.time() - start_time_all,
                'meeting_type': meeting_type
            }

        # Step 2: Calculate adaptive lengths
        min_length, max_length = self.calculate_adaptive_length(word_count)
        
        # Step 3: Chunk if necessary
        chunks = self._chunk_intelligently(text, max_length=1500) # Slightly conservative than notebook
        
        if len(chunks) > 1:
            print(f"📑 Split into {len(chunks)} chunks for processing\\n")
        
        # Step 4: Summarize chunks
        chunk_summaries = []
        
        for i, chunk in enumerate(chunks, 1):
            chunk_words = len(chunk.split())
            
            if len(chunks) > 1:
                print(f"⏳ Processing chunk {i}/{len(chunks)} ({chunk_words} words)...")
                chunk_min = max(50, int(min_length * (chunk_words / word_count)))
                chunk_max = max(100, int(max_length * (chunk_words / word_count)))
            else:
                chunk_min = min_length
                chunk_max = max_length
            
            # Safety checks for min/max
            chunk_max = min(chunk_max, 500) # Cap per chunk
            chunk_min = min(chunk_min, chunk_max - 10)

            summary = self._summarize_with_phi2(chunk, chunk_min, chunk_max)
            chunk_summaries.append(summary)
            
            if len(chunks) > 1:
                print(f"   ✓ Generated {len(summary.split())} words\\n")
        
        # Step 5: Combine if multiple chunks
        if len(chunk_summaries) == 1:
            final_summary = chunk_summaries[0]
        else:
            combined = '\\n\\n'.join(chunk_summaries)
            combined_words = len(combined.split())
            
            print(f"📝 Combined chunks: {combined_words} words")
            
            if combined_words > max_length * 1.5:
                print(f"⏳ Consolidating final summary...\\n")
                # Recursive summary for consolidated text
                final_summary = self._summarize_with_phi2(combined, min_length, max_length)
            else:
                final_summary = combined
        
        # Calculate metrics
        elapsed = time.time() - start_time_all
        summary_words = len(final_summary.split())
        compression = (1 - summary_words / word_count) * 100 if word_count > 0 else 0
        
        print(f"✅ Summarization complete in {elapsed:.1f}s\\n")
        
        results = {
            'audio_file': os.path.basename(audio_path),
            'language': transcription['language'],
            'transcription': text,
            'summary': final_summary,
            'original_words': word_count,
            'summary_words': summary_words,
            'compression_percent': compression,
            'retained_percent': 100 - compression,
            'processing_time': elapsed,
            'meeting_type': meeting_type
        }
        
        return results
