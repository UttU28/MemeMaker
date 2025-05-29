#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
import yt_dlp


def downloadYoutubeVideo(url, outputPath="downloads"):
    Path(outputPath).mkdir(exist_ok=True)
    
    ydlOpts = {
        'format': 'bestvideo[height<=1080][ext=mp4]',
        'outtmpl': f'{outputPath}/%(title)s.%(ext)s',
        'writeinfojson': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
    }
    
    downloadedFile = None
    try:
        with yt_dlp.YoutubeDL(ydlOpts) as ydl:
            print(f"Downloading: {url}")
            
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            
            print(f"Title: {title}")
            
            ydl.download([url])
            downloadedFile = f"{outputPath}/{title}.mp4"
            
            print(f"✅ Downloaded: {title}")
            
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
        
        import json
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
        
        # Generate output filename
        baseFilename = Path(inputFile).stem
        outputFile = f"{outputPath}/{baseFilename}_mobile.mp4"
        
        print("💾 Processing with ffmpeg...")
        
        # FFmpeg command to crop and resize
        cmd = [
            'ffmpeg', '-i', inputFile,
            '-vf', f'crop={newWidth}:{newHeight}:{cropX}:{cropY},scale={targetWidth}:{targetHeight}',
            '-c:v', 'libx264', '-crf', '23', '-preset', 'fast',
            '-an',  # Remove audio
            '-y',   # Overwrite output file
            outputFile
        ]
        
        # Run ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Mobile version saved: {outputFile}")
            
            # Remove original file
            os.remove(inputFile)
            print("🗑️ Original file removed")
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Processing error: {e}")


def main():
    print("🎥 YouTube Mobile Video Downloader")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        videoUrl = sys.argv[1]
    else:
        # videoUrl = input("YouTube URL: ").strip()
        videoUrl = "https://www.youtube.com/watch?v=4rwfpmYcwns"
    
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
        cropVideoToMobile(downloadedFile, outputDir)


if __name__ == "__main__":
    main()
