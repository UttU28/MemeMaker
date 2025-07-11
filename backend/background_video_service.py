#!/usr/bin/env python3

import asyncio
import os
import uuid
import traceback
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import threading
import queue

from firebase_service import getFirebaseService
from video_service import VideoGenerator
from audio_service import generateAudioForScript, F5TTSClient
from utils import loadUserProfiles

logger = logging.getLogger(__name__)

class BackgroundVideoService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)  # Limit concurrent video generations
        self.active_jobs = {}
        self.job_queue = queue.Queue()  # Thread-safe queue
        self.processing_jobs = set()  # Track jobs being processed
        self.stop_event = threading.Event()  # Stop event for graceful shutdown
        self.is_processing = False
        
    async def start_background_processor(self):
        """Start processing video generation jobs in the background"""
        logger.info("🚀 Starting background video processor...")
        
        while not self.stop_event.is_set():
            try:
                # Get job from queue (with timeout)
                try:
                    job_id = self.job_queue.get(timeout=1.0)
                except queue.Empty:
                    continue  # Queue is empty, continue loop
                
                if job_id in self.processing_jobs:
                    continue  # Job already being processed
                
                # Add to processing set
                self.processing_jobs.add(job_id)
                
                # Get job data from Firebase
                firebase_service = getFirebaseService()
                job_data = firebase_service.getVideoGenerationJob(job_id)
                
                if not job_data:
                    logger.error(f"❌ Job {job_id} not found in database")
                    self.processing_jobs.discard(job_id)
                    continue
                
                # Process the job
                await self._process_video_generation_job(job_data)
                
            except Exception as e:
                logger.error(f"💥 Background processor error: {str(e)}")
                await asyncio.sleep(1)  # Wait before continuing
        
        logger.info("🛑 Background video processor stopped")
    
    def stop_background_processor(self):
        """Stop the background job processor"""
        self.is_processing = False
        self.stop_event.set()  # Signal the processor to stop
        logger.info("🛑 Stopped background video processor")
    
    async def queue_video_generation(self, script_id: str, user_id: str, background_video: Optional[str] = None) -> str:
        """Queue a new video generation job"""
        firebase_service = getFirebaseService()
        
        # Check if script exists
        script = firebase_service.getScript(script_id)
        if not script:
            raise Exception(f"Script {script_id} not found")
        
        # Generate unique job ID
        job_id = f"video_job_{uuid.uuid4().hex}"
        
        # Define processing steps
        steps = [
            {'stepName': 'audio_validation', 'status': 'pending', 'progress': 0.0, 'message': 'Validating audio files...'},
            {'stepName': 'audio_generation', 'status': 'pending', 'progress': 0.0, 'message': 'Generating missing audio...'},
            {'stepName': 'timeline_creation', 'status': 'pending', 'progress': 0.0, 'message': 'Creating video timeline...'},
            {'stepName': 'audio_concatenation', 'status': 'pending', 'progress': 0.0, 'message': 'Combining audio files...'},
            {'stepName': 'video_generation', 'status': 'pending', 'progress': 0.0, 'message': 'Generating final video...'}
        ]
        
        # Create job in Firebase
        success = firebase_service.createVideoGenerationJob(job_id, script_id, user_id, len(steps), steps)
        if not success:
            raise Exception("Failed to create video generation job")
        
        # **IMPORTANT**: Update script with video job information
        script_updates = {
            'currentVideoJobId': job_id,
            'videoJobStatus': 'queued',
            'videoJobProgress': 0.0,
            'videoJobStartedAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        # Update script document to link it with the video job
        firebase_service.saveScript(script_id, {**script, **script_updates})
        
        # Add to active jobs queue
        self.job_queue.put(job_id)
        
        logger.info(f"✅ Queued video generation job: {job_id} for script {script_id}")
        return job_id
    
    async def _process_video_generation_job(self, job_data: Dict[str, Any]):
        """Process a single video generation job"""
        job_id = job_data.get('jobId')
        script_id = job_data.get('scriptId')
        user_id = job_data.get('userId')
        
        logger.info(f"🎬 Starting video generation job: {job_id}")
        
        firebase_service = getFirebaseService()
        
        try:
            # Step 1: Audio validation (0-20%)
            await self._step_audio_validation(job_id, script_id)
            
            # Step 2: Audio generation (20-40%)
            await self._step_audio_generation(job_id, script_id)
            
            # Step 3: Timeline creation (40-60%)
            timeline, total_duration = await self._step_timeline_creation(job_id, script_id)
            
            # Step 4: Audio concatenation (60-80%)
            combined_audio_path = await self._step_audio_concatenation(job_id, script_id, timeline)
            
            # Step 5: Video generation (80-100%)
            background_video = None  # Use default background
            final_video_path, video_size = await self._step_video_generation(
                job_id, script_id, timeline, total_duration, combined_audio_path, background_video
            )
            
            # Complete the job
            firebase_service.completeVideoGenerationJob(
                job_id, final_video_path, total_duration, video_size
            )
            
            # Update the script database with video information
            script_data = firebase_service.getScript(script_id)
            if script_data:
                script_data['finalVideoPath'] = final_video_path
                script_data['videoDuration'] = total_duration
                script_data['videoSize'] = video_size
                script_data['videoJobStatus'] = 'completed'
                script_data['videoJobProgress'] = 100.0
                script_data['videoJobCompletedAt'] = datetime.now().isoformat()
                script_data['updatedAt'] = datetime.now().isoformat()
                
                # Save the updated script
                firebase_service.saveScript(script_id, script_data)
                logger.info(f"✅ Updated script {script_id} with video information")
            
            # Log video completion activity
            if user_id:
                firebase_service.addVideoActivity(
                    user_id, 
                    firebase_service.ActivityType.VIDEO_GENERATION_COMPLETED, 
                    script_id, 
                    script_data.get('originalPrompt', '')[:50] + "..." if len(script_data.get('originalPrompt', '')) > 50 else script_data.get('originalPrompt', script_id),
                    final_video_path
                )
            
            logger.info(f"✅ Successfully completed video generation job: {job_id}")
            
        except Exception as e:
            logger.error(f"💥 Job {job_id} failed: {str(e)}")
            logger.error(f"💥 Traceback: {traceback.format_exc()}")
            
            # Mark job as failed
            firebase_service.failVideoGenerationJob(job_id, f"Video generation failed: {str(e)}")
            
            # Update script with failure status
            script_data = firebase_service.getScript(script_id)
            if script_data:
                script_data['videoJobStatus'] = 'failed'
                script_data['videoJobErrorMessage'] = str(e)
                script_data['videoJobCompletedAt'] = datetime.now().isoformat()
                script_data['updatedAt'] = datetime.now().isoformat()
                firebase_service.saveScript(script_id, script_data)
                logger.info(f"✅ Updated script {script_id} with failure status")
            
            # Clean up any temporary files
            try:
                if 'combined_audio_path' in locals() and os.path.exists(combined_audio_path):
                    os.remove(combined_audio_path)
                    logger.info(f"🗑️ Cleaned up temporary audio file: {combined_audio_path}")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Could not clean up temporary files: {cleanup_error}")
                
        finally:
            # Always remove from processing set
            self.processing_jobs.discard(job_id)
    
    def _update_script_progress(self, script_id: str, status: str, progress: float, current_step: str = None):
        """Update script document with current video generation progress"""
        try:
            firebase_service = getFirebaseService()
            script_data = firebase_service.getScript(script_id)
            if script_data:
                script_data['videoJobStatus'] = status
                script_data['videoJobProgress'] = progress
                if current_step:
                    script_data['videoJobCurrentStep'] = current_step
                script_data['updatedAt'] = datetime.now().isoformat()
                firebase_service.saveScript(script_id, script_data)
        except Exception as e:
            logger.warning(f"⚠️ Could not update script progress: {str(e)}")

    async def _step_audio_validation(self, job_id: str, script_id: str):
        """Step 1: Validate existing audio files"""
        firebase_service = getFirebaseService()
        
        try:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_validation', 'in_progress', 0.0, 'Starting audio validation...'
            )
            self._update_script_progress(script_id, 'in_progress', 5.0, 'audio_validation')
            
            script_data = firebase_service.getScript(script_id)
            if not script_data:
                raise Exception(f"Script {script_id} not found")
            
            dialogue_lines = script_data.get('dialogue', [])
            if not dialogue_lines:
                raise Exception("Script has no dialogue lines")
            
            # Check which audio files exist
            total_lines = len(dialogue_lines)
            existing_audio = 0
            
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_validation', 'in_progress', 10.0, f'Checking {total_lines} dialogue lines...'
            )
            self._update_script_progress(script_id, 'in_progress', 10.0, 'audio_validation')
            
            for line in dialogue_lines:
                audio_file = line.get('audioFile', '')
                if audio_file and os.path.exists(audio_file):
                    existing_audio += 1
            
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_validation', 'completed', 100.0, 
                f'Found {existing_audio}/{total_lines} audio files', 
                overallProgress=20.0, currentStep='audio_generation'
            )
            self._update_script_progress(script_id, 'in_progress', 20.0, 'audio_generation')
            
        except Exception as e:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_validation', 'failed', 0.0, str(e)
            )
            self._update_script_progress(script_id, 'failed', 0.0)
            raise
    
    async def _step_audio_generation(self, job_id: str, script_id: str):
        """Step 2: Generate missing audio files"""
        firebase_service = getFirebaseService()
        
        try:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_generation', 'in_progress', 10.0, 'Generating audio files...'
            )
            self._update_script_progress(script_id, 'in_progress', 25.0, 'audio_generation')
            
            # Load required data
            scripts_data = firebase_service.getAllScripts()
            user_profiles = loadUserProfiles("apiData/userProfiles.json")
            
            # Define progress callback
            def audio_progress_callback(progress_percent: float, message: str):
                # Map 0-100% audio progress to 10-90% within the audio generation step
                mapped_progress = 10.0 + (progress_percent * 0.8)  # 10% to 90%
                firebase_service.updateVideoGenerationJobProgress(
                    job_id, 'audio_generation', 'in_progress', mapped_progress, message
                )
                # Overall progress: audio generation is 25-70%, so map accordingly for better granularity
                overall_progress = 25.0 + (progress_percent * 0.45)  # 25% to 70%
                self._update_script_progress(script_id, 'in_progress', overall_progress, 'audio_generation')
            
            # Generate audio with progress tracking
            from app import GENERATED_AUDIO_DIR
            result = await generateAudioForScript(
                script_id, scripts_data, user_profiles, GENERATED_AUDIO_DIR, audio_progress_callback
            )
            
            # Save updated scripts data
            firebase_service.saveScripts(scripts_data)
            
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_generation', 'completed', 100.0, 
                f'Generated audio: {result.message}',
                overallProgress=70.0, currentStep='timeline_creation'
            )
            self._update_script_progress(script_id, 'in_progress', 70.0, 'timeline_creation')
            
        except Exception as e:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_generation', 'failed', 0.0, str(e)
            )
            self._update_script_progress(script_id, 'failed', 70.0)
            raise
    
    async def _step_timeline_creation(self, job_id: str, script_id: str):
        """Step 3: Create video timeline"""
        firebase_service = getFirebaseService()
        
        try:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'timeline_creation', 'in_progress', 20.0, 'Creating timeline...'
            )
            self._update_script_progress(script_id, 'in_progress', 72.0, 'timeline_creation')
            
            script_data = firebase_service.getScript(script_id)
            user_profiles = loadUserProfiles("apiData/userProfiles.json")
            
            video_generator = VideoGenerator()
            timeline, total_duration = video_generator._createTimeline(script_data, user_profiles)
            
            if not timeline:
                raise Exception("Failed to create timeline - no valid segments")
            
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'timeline_creation', 'completed', 100.0, 
                f'Created timeline with {len(timeline)} segments ({total_duration:.2f}s)',
                overallProgress=80.0, currentStep='audio_concatenation'
            )
            self._update_script_progress(script_id, 'in_progress', 80.0, 'audio_concatenation')
            
            return timeline, total_duration
            
        except Exception as e:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'timeline_creation', 'failed', 0.0, str(e)
            )
            self._update_script_progress(script_id, 'failed', 72.0)
            raise
    
    async def _step_audio_concatenation(self, job_id: str, script_id: str, timeline: List[Dict]):
        """Step 4: Concatenate audio files"""
        firebase_service = getFirebaseService()
        
        try:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_concatenation', 'in_progress', 20.0, 'Combining audio...'
            )
            self._update_script_progress(script_id, 'in_progress', 82.0, 'audio_concatenation')
            
            from app import VIDEO_OUTPUT_DIR
            combined_audio_path = os.path.join(VIDEO_OUTPUT_DIR, f"{script_id}_combined_audio.wav")
            
            video_generator = VideoGenerator()
            success = video_generator._concatenateAudioFiles(timeline, combined_audio_path)
            
            if not success:
                raise Exception("Failed to concatenate audio files")
            
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_concatenation', 'completed', 100.0, 
                'Audio files combined successfully',
                overallProgress=90.0, currentStep='video_generation'
            )
            self._update_script_progress(script_id, 'in_progress', 90.0, 'video_generation')
            
            return combined_audio_path
            
        except Exception as e:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'audio_concatenation', 'failed', 0.0, str(e)
            )
            self._update_script_progress(script_id, 'failed', 82.0)
            raise
    
    async def _step_video_generation(self, job_id: str, script_id: str, timeline: List[Dict], 
                                   total_duration: float, combined_audio_path: str, background_video: Optional[str]):
        """Step 5: Generate final video"""
        firebase_service = getFirebaseService()
        
        try:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'video_generation', 'in_progress', 10.0, 'Starting video generation...'
            )
            self._update_script_progress(script_id, 'in_progress', 92.0, 'video_generation')
            
            from app import VIDEO_OUTPUT_DIR, BACKGROUND_DIR, DEFAULT_BACKGROUND_VIDEO, FONT_PATH
            
            video_generator = VideoGenerator()
            
            # Get background video
            if not background_video:
                background_video = video_generator._getRandomBackgroundVideo(BACKGROUND_DIR, DEFAULT_BACKGROUND_VIDEO)
            
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'video_generation', 'in_progress', 30.0, 'Running FFmpeg...'
            )
            self._update_script_progress(script_id, 'in_progress', 95.0, 'video_generation')
            
            final_video_path = os.path.join(VIDEO_OUTPUT_DIR, f"{script_id}_final_video.mp4")
            
            # Generate video with FFmpeg
            success, video_size = video_generator._generateVideoWithFfmpeg(
                background_video, timeline, total_duration, combined_audio_path, 
                final_video_path, script_id, FONT_PATH
            )
            
            if not success:
                raise Exception("FFmpeg video generation failed")
            
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'video_generation', 'completed', 100.0, 
                f'Video generated successfully ({video_size} bytes)',
                overallProgress=100.0
            )
            self._update_script_progress(script_id, 'in_progress', 98.0, 'video_generation')
            
            return final_video_path, video_size
            
        except Exception as e:
            firebase_service.updateVideoGenerationJobProgress(
                job_id, 'video_generation', 'failed', 0.0, str(e)
            )
            self._update_script_progress(script_id, 'failed', 95.0)
            raise

# Global background service instance
background_video_service = None

def get_background_video_service() -> BackgroundVideoService:
    """Get the global background video service instance"""
    global background_video_service
    if background_video_service is None:
        background_video_service = BackgroundVideoService()
    return background_video_service

def initialize_background_video_service():
    """Initialize and start the background video service"""
    service = get_background_video_service()
    
    # Start background processor in a separate thread
    def run_processor():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(service.start_background_processor())
        except Exception as e:
            logger.error(f"💥 Background processor error: {str(e)}")
        finally:
            loop.close()
    
    processor_thread = Thread(target=run_processor, daemon=True)
    processor_thread.start()
    
    logger.info("🚀 Background video service initialized") 