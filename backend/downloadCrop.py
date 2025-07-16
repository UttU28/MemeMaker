#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
import yt_dlp
import json

# Set to True to delete original and mobile videos after processing
delete = True


def downloadYoutubeVideo(url, outputPath="downloads"):
    Path(outputPath).mkdir(exist_ok=True)
    
    downloadedFile = None
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            print(f"📥 Downloading: {url}")
            
            info = ydl.extract_info(url, download=False)
            videoId = info.get('id', 'unknown')
            title = info.get('title', 'Unknown')
            
            print(f"🎬 Title: {title}")
            print(f"🆔 Video ID: {videoId}")
        
        ydlOpts = {
            'format': 'bestvideo[height<=1080][ext=mp4]',
            'outtmpl': f'{outputPath}/{videoId}.%(ext)s',
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        with yt_dlp.YoutubeDL(ydlOpts) as ydl:
            ydl.download([url])
            downloadedFile = f"{outputPath}/{videoId}.mp4"
            
            print(f"✅ Downloaded as: {videoId}.mp4")
            
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
        
    baseFilename = Path(inputFile).stem
    outputFile = f"{outputPath}/{baseFilename}_mobile.mp4"
    
    if os.path.exists(outputFile):
        print(f"✅ Mobile version already exists: {outputFile}")
        print("📁 Original file preserved")
        return
        
    try:
        print("🎬 Processing video for mobile...")
        
        originalWidth, originalHeight = getVideoInfo(inputFile)
        if not originalWidth or not originalHeight:
            print("❌ Could not get video dimensions")
            return
            
        print(f"📐 Original: {originalWidth}x{originalHeight}")
        
        targetWidth = 1080
        targetHeight = 1920
        aspectRatio = targetWidth / targetHeight
        
        if originalWidth / originalHeight > aspectRatio:
            newWidth = int(originalHeight * aspectRatio)
            newHeight = originalHeight
            cropX = (originalWidth - newWidth) // 2
            cropY = 0
        else:
            newWidth = originalWidth
            newHeight = int(originalWidth / aspectRatio)
            cropX = 0
            cropY = (originalHeight - newHeight) // 2
        
        print("💾 Processing with ffmpeg...")
        
        gpuCmd = [
            'ffmpeg', '-i', inputFile,
            '-vf', f'crop={newWidth}:{newHeight}:{cropX}:{cropY},scale={targetWidth}:{targetHeight}',
            '-c:v', 'h264_nvenc', '-preset', 'fast', '-cq', '23',
            '-an',
            '-y',
            outputFile
        ]
        
        cpuCmd = [
            'ffmpeg', '-i', inputFile,
            '-vf', f'crop={newWidth}:{newHeight}:{cropX}:{cropY},scale={targetWidth}:{targetHeight}',
            '-c:v', 'libx264', '-crf', '23', '-preset', 'fast',
            '-an',
            '-y',
            outputFile
        ]
        
        print("🚀 Attempting GPU acceleration (NVIDIA)...")
        result = subprocess.run(gpuCmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️ GPU encoding failed, falling back to CPU...")
            print("💻 Processing with CPU...")
            result = subprocess.run(cpuCmd, capture_output=True, text=True)
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
    if not os.path.exists(backgroundDir):
        os.makedirs(backgroundDir, exist_ok=True)
        return 1
    
    existingFiles = os.listdir(backgroundDir)
    backgroundNumbers = []
    
    for filename in existingFiles:
        if filename.startswith('background') and filename.endswith('.mp4'):
            try:
                numberStr = filename.replace('background', '').replace('.mp4', '')
                number = int(numberStr)
                backgroundNumbers.append(number)
            except ValueError:
                continue
    
    if not backgroundNumbers:
        return 1
    
    return max(backgroundNumbers) + 1


def splitVideoIntoSegments(inputFile, backgroundDir="apiData/background"):
    if not inputFile or not os.path.exists(inputFile):
        print("❌ Input file not found for splitting")
        return
    
    Path(backgroundDir).mkdir(parents=True, exist_ok=True)
    
    duration = getVideoLength(inputFile)
    if not duration:
        print("❌ Could not get video duration")
        return
    
    print(f"🎬 Video duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    
    segmentDuration = 90
    
    startNumber = getNextBackgroundNumber(backgroundDir)
    
    print(f"📂 Starting from background{startNumber:03d}")
    print("✂️ Splitting into 1.5-minute segments...")
    
    segmentCount = 0
    currentTime = 0
    
    while currentTime < duration:
        remaining = duration - currentTime
        if remaining < segmentDuration:
            print(f"⏭️ Skipping last {remaining:.1f} seconds (less than 1.5 minutes)")
            break
        
        segmentNumber = startNumber + segmentCount
        outputFile = f"{backgroundDir}/background{segmentNumber:03d}.mp4"
        
        print(f"🎞️ Creating segment {segmentNumber:03d}: {currentTime/60:.1f}-{(currentTime+segmentDuration)/60:.1f} min")
        
        cmd = [
            'ffmpeg', '-i', inputFile,
            '-ss', str(currentTime),
            '-t', str(segmentDuration),
            '-c', 'copy',
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
        videoUrl = "https://www.youtube.com/watch?v=dVFm8veHbqc"
    
    if not videoUrl:
        print("❌ No URL provided")
        return
    
    if not any(domain in videoUrl for domain in ['youtube.com', 'youtu.be']):
        print("❌ Invalid YouTube URL")
        return
    
    outputDir = "downloads"
    if not outputDir:
        outputDir = "downloads"
    
    downloadedFile = downloadYoutubeVideo(videoUrl, outputDir)
    
    if downloadedFile:
        cropVideoToMobile(downloadedFile, outputDir)
        
        baseFilename = Path(downloadedFile).stem
        mobileFile = f"{outputDir}/{baseFilename}_mobile.mp4"
        
        if os.path.exists(mobileFile):
            splitVideoIntoSegments(mobileFile)
            
            # Delete original and mobile files if delete flag is True
            if delete:
                print("🗑️ Cleaning up video files...")
                
                # Delete original downloaded file
                if os.path.exists(downloadedFile):
                    try:
                        os.remove(downloadedFile)
                        print(f"✅ Deleted original file: {downloadedFile}")
                    except Exception as e:
                        print(f"❌ Error deleting original file: {e}")
                
                # Delete mobile file
                if os.path.exists(mobileFile):
                    try:
                        os.remove(mobileFile)
                        print(f"✅ Deleted mobile file: {mobileFile}")
                    except Exception as e:
                        print(f"❌ Error deleting mobile file: {e}")
                
                # Delete the entire downloads directory
                try:
                    import shutil
                    if os.path.exists(outputDir):
                        shutil.rmtree(outputDir)
                        print(f"✅ Deleted downloads directory: {outputDir}")
                except Exception as e:
                    print(f"❌ Error deleting downloads directory: {e}")
                
                print("🎉 Cleanup completed!")


if __name__ == "__main__":
    main()
