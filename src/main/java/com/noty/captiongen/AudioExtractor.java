package com.noty.captiongen;

import java.io.*;
import java.nio.file.*;

public class AudioExtractor {
    
    public static File extractAudio(File inputFile) throws Exception {
        String inputPath = inputFile.getAbsolutePath();
        String outputPath = inputFile.getParent() + File.separator + 
                           getFileNameWithoutExtension(inputFile) + "_temp.wav";
        
        // If input is already WAV, just return it
        if (inputPath.toLowerCase().endsWith(".wav")) {
            return inputFile;
        }
        
        // Find FFmpeg in files folder
        String ffmpegPath = findFFmpeg();
        
        System.out.println("Using FFmpeg: " + ffmpegPath);
        System.out.println("Extracting audio from: " + inputPath);
        System.out.println("Output to: " + outputPath);
        
        // Try to extract vocals using FFmpeg filters
        File outputFile = new File(outputPath);
        
        // Method 1: Try vocal isolation using ffmpeg filters
        if (extractWithFFmpeg(ffmpegPath, inputPath, outputPath)) {
            System.out.println("Audio extraction successful");
            return outputFile;
        }
        
        throw new Exception("FFmpeg extraction failed. Please ensure ffmpeg.exe is in the files folder.");
    }
    
    private static boolean extractWithFFmpeg(String ffmpegPath, String inputPath, String outputPath) {
        try {
            ProcessBuilder pb = new ProcessBuilder(
                ffmpegPath,
                "-i", inputPath,
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                "-y",
                outputPath
            );
            
            pb.redirectErrorStream(true);
            Process process = pb.start();
            
            StringBuilder output = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                }
            }
            
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                File outputFile = new File(outputPath);
                return outputFile.exists() && outputFile.length() > 0;
            }
            return false;
            
        } catch (Exception e) {
            System.err.println("FFmpeg extraction error: " + e.getMessage());
            return false;
        }
    }
    
    private static String findFFmpeg() {
        // Check in files folder first
        File ffmpegFile = new File("files/ffmpeg.exe");
        if (ffmpegFile.exists() && ffmpegFile.canExecute()) {
            return ffmpegFile.getAbsolutePath();
        }
        
        // Check in current directory
        ffmpegFile = new File("ffmpeg.exe");
        if (ffmpegFile.exists() && ffmpegFile.canExecute()) {
            return ffmpegFile.getAbsolutePath();
        }
        
        // Check in PATH
        String[] commonPaths = {"ffmpeg", "ffmpeg.exe"};
        for (String path : commonPaths) {
            try {
                ProcessBuilder pb = new ProcessBuilder(path, "-version");
                Process process = pb.start();
                int exitCode = process.waitFor();
                if (exitCode == 0) {
                    return path;
                }
            } catch (Exception e) {
                // Not found
            }
        }
        
        return "ffmpeg";
    }
    
    private static String getFileNameWithoutExtension(File file) {
        String name = file.getName();
        int lastDot = name.lastIndexOf('.');
        if (lastDot > 0) {
            return name.substring(0, lastDot);
        }
        return name;
    }
}