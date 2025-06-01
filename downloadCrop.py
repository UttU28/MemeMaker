#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
import yt_dlp
import json


def downloadYoutubeVideo(url, outputPath="downloads"):
    Path(outputPath).mkdir(exist_ok=True)
    
    downloadedFile = None
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            # Extract video info to get video ID and title
            print(f"Downloading: {url}")
            
            info = ydl.extract_info(url, download=False)
            video_id = info.get('id', 'unknown')
            title = info.get('title', 'Unknown')
            
            print(f"Title: {title}")
            print(f"Video ID: {video_id}")
        
        # Use video ID as filename
        ydlOpts = {
            'format': 'bestvideo[height<=1080][ext=mp4]',
            'outtmpl': f'{outputPath}/{video_id}.%(ext)s',
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        with yt_dlp.YoutubeDL(ydlOpts) as ydl:
            ydl.download([url])
            downloadedFile = f"{outputPath}/{video_id}.mp4"
            
            print(f"✅ Downloaded as: {video_id}.mp4")
            
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None
        
    return downloadedFile


def getVideoInfo(inputFile):
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
            inputFile
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                width = int(stream['width'])
                height = int(stream['height'])
                return width, height
                
    except Exception as e:
        print(f"❌ Error getting video info: {e}")
        return None, None


def cropVideoToMobile(inputFile, outputPath="downloads"):
    if not inputFile or not os.path.exists(inputFile):
        print("❌ Input file not found")
        return
        
    # Generate output filename first to check if it already exists
    baseFilename = Path(inputFile).stem
    outputFile = f"{outputPath}/{baseFilename}_mobile.mp4"
    
    # Check if mobile version already exists
    if os.path.exists(outputFile):
        print(f"✅ Mobile version already exists: {outputFile}")
        print("📁 Original file preserved")
        return
        
    try:
        print("🎬 Processing video for mobile...")
        
        # Get original video dimensions
        originalWidth, originalHeight = getVideoInfo(inputFile)
        if not originalWidth or not originalHeight:
            print("❌ Could not get video dimensions")
            return
            
        print(f"Original: {originalWidth}x{originalHeight}")
        
        # Target dimensions for mobile (16:9 vertical aspect ratio)
        targetWidth = 1080
        targetHeight = 1920
        aspectRatio = targetWidth / targetHeight
        
        # Calculate crop parameters
        if originalWidth / originalHeight > aspectRatio:
            # Video is wider, crop width
            newWidth = int(originalHeight * aspectRatio)
            newHeight = originalHeight
            cropX = (originalWidth - newWidth) // 2
            cropY = 0
        else:
            # Video is taller, crop height
            newWidth = originalWidth
            newHeight = int(originalWidth / aspectRatio)
            cropX = 0
            cropY = (originalHeight - newHeight) // 2
        
        print("💾 Processing with ffmpeg...")
        
        # Try GPU encoding first (NVIDIA), fallback to CPU
        gpu_cmd = [
            'ffmpeg', '-i', inputFile,
            '-vf', f'crop={newWidth}:{newHeight}:{cropX}:{cropY},scale={targetWidth}:{targetHeight}',
            '-c:v', 'h264_nvenc', '-preset', 'fast', '-cq', '23',
            '-an',  # Remove audio
            '-y',   # Overwrite output file
            outputFile
        ]
        
        cpu_cmd = [
            'ffmpeg', '-i', inputFile,
            '-vf', f'crop={newWidth}:{newHeight}:{cropX}:{cropY},scale={targetWidth}:{targetHeight}',
            '-c:v', 'libx264', '-crf', '23', '-preset', 'fast',
            '-an',  # Remove audio
            '-y',   # Overwrite output file
            outputFile
        ]
        
        # Try GPU encoding first
        print("🚀 Attempting GPU acceleration (NVIDIA)...")
        result = subprocess.run(gpu_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️ GPU encoding failed, falling back to CPU...")
            print("💻 Processing with CPU...")
            result = subprocess.run(cpu_cmd, capture_output=True, text=True)
        else:
            print("🎮 GPU acceleration successful!")
        
        if result.returncode == 0:
            print(f"✅ Mobile version saved: {outputFile}")
            print("📁 Original file preserved")
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Processing error: {e}")


def getVideoLength(inputFile):
    """Get video duration in seconds"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_entries',
            'format=duration', inputFile
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
        
    except Exception as e:
        print(f"❌ Error getting video duration: {e}")
        return None


def getNextBackgroundNumber(backgroundDir):
    """Get the next available background number"""
    if not os.path.exists(backgroundDir):
        os.makedirs(backgroundDir, exist_ok=True)
        return 1
    
    existing_files = os.listdir(backgroundDir)
    background_numbers = []
    
    for filename in existing_files:
        if filename.startswith('background') and filename.endswith('.mp4'):
            try:
                # Extract number from filename like background001.mp4
                number_str = filename.replace('background', '').replace('.mp4', '')
                number = int(number_str)
                background_numbers.append(number)
            except ValueError:
                continue
    
    if not background_numbers:
        return 1
    
    return max(background_numbers) + 1


def splitVideoIntoSegments(inputFile, backgroundDir="data/background"):
    """Split mobile video into 1.5-minute segments"""
    if not inputFile or not os.path.exists(inputFile):
        print("❌ Input file not found for splitting")
        return
    
    # Create background directory if it doesn't exist
    Path(backgroundDir).mkdir(parents=True, exist_ok=True)
    
    # Get video duration
    duration = getVideoLength(inputFile)
    if not duration:
        print("❌ Could not get video duration")
        return
    
    print(f"🎬 Video duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    
    # Segment duration (1.5 minutes = 90 seconds)
    segmentDuration = 90
    
    # Get starting number for background files
    startNumber = getNextBackgroundNumber(backgroundDir)
    
    print(f"📂 Starting from background{startNumber:03d}")
    print("✂️ Splitting into 1.5-minute segments...")
    
    segmentCount = 0
    currentTime = 0
    
    while currentTime < duration:
        # Check if remaining time is at least 1.5 minutes
        remaining = duration - currentTime
        if remaining < segmentDuration:
            print(f"⏭️ Skipping last {remaining:.1f} seconds (less than 1.5 minutes)")
            break
        
        segmentNumber = startNumber + segmentCount
        outputFile = f"{backgroundDir}/background{segmentNumber:03d}.mp4"
        
        print(f"🎞️ Creating segment {segmentNumber:03d}: {currentTime/60:.1f}-{(currentTime+segmentDuration)/60:.1f} min")
        
        # FFmpeg command to extract segment
        cmd = [
            'ffmpeg', '-i', inputFile,
            '-ss', str(currentTime),
            '-t', str(segmentDuration),
            '-c', 'copy',  # Copy without re-encoding for speed
            '-avoid_negative_ts', 'make_zero',
            '-y',
            outputFile
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Segment {segmentNumber:03d} saved")
        else:
            print(f"❌ Error creating segment {segmentNumber:03d}: {result.stderr}")
            break
        
        segmentCount += 1
        currentTime += segmentDuration
    
    print(f"🎉 Created {segmentCount} background video segments")
    print(f"📁 Mobile video preserved: {inputFile}")


def main():
    print("🎥 YouTube Mobile Video Downloader")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        videoUrl = sys.argv[1]
    else:
        # videoUrl = input("YouTube URL: ").strip()
        videoUrl = "https://www.youtube.com/watch?v=dVFm8veHbqc"
        # videoUrl = "https://www.youtube.com/watch?v=u7kdVe8q5zs"
    
    if not videoUrl:
        print("❌ No URL provided")
        return
    
    if not any(domain in videoUrl for domain in ['youtube.com', 'youtu.be']):
        print("❌ Invalid YouTube URL")
        return
    
    # outputDir = input("Output directory (Enter for 'downloads'): ").strip()
    outputDir = "downloads"
    if not outputDir:
        outputDir = "downloads"
    
    # Download video
    downloadedFile = downloadYoutubeVideo(videoUrl, outputDir)
    
    if downloadedFile:
        # Crop to mobile format
        cropVideoToMobile(downloadedFile, outputDir)
        
        # Generate mobile filename for splitting
        baseFilename = Path(downloadedFile).stem
        mobileFile = f"{outputDir}/{baseFilename}_mobile.mp4"
        
        # Split mobile version into segments
        if os.path.exists(mobileFile):
            splitVideoIntoSegments(mobileFile)


if __name__ == "__main__":
    main()
