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

        // Find FFmpeg
        String ffmpegPath = findFFmpeg();

        System.out.println("Using FFmpeg: " + ffmpegPath);
        System.out.println("Extracting vocals from: " + inputPath);
        System.out.println("Output to: " + outputPath);

        // Try to extract vocals using FFmpeg filters
        File outputFile = new File(outputPath);

        // Method 1: Try vocal isolation using ffmpeg filters
        if (extractVocalsWithFFmpeg(ffmpegPath, inputPath, outputPath)) {
            System.out.println("Vocal extraction successful");
            return outputFile;
        }

        // Method 2: Fallback to standard audio extraction
        System.out.println("Vocal extraction failed, falling back to standard audio extraction");
        return extractStandardAudio(ffmpegPath, inputPath, outputPath);
    }

    private static boolean extractVocalsWithFFmpeg(String ffmpegPath, String inputPath, String outputPath) {
        try {
            // Use FFmpeg's voice isolation filter
            ProcessBuilder pb = new ProcessBuilder(
                    ffmpegPath,
                    "-i", inputPath,
                    "-af", "highpass=f=200, lowpass=f=3000, acompressor=threshold=0.1:ratio=2:attack=200:release=1000, volume=2",
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
            System.err.println("Vocal extraction error: " + e.getMessage());
            return false;
        }
    }

    private static File extractStandardAudio(String ffmpegPath, String inputPath, String outputPath) throws Exception {
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
                System.out.println(line);
            }
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new Exception("FFmpeg extraction failed with exit code: " + exitCode + "\nOutput: " + output.toString());
        }

        File outputFile = new File(outputPath);
        if (!outputFile.exists() || outputFile.length() == 0) {
            throw new Exception("Audio extraction failed: Output file is empty or missing");
        }

        System.out.println("Audio extracted successfully: " + outputFile.length() + " bytes");
        return outputFile;
    }

    private static String findFFmpeg() {
        // Check current directory first
        String[] commonPaths = {
                "ffmpeg",
                "ffmpeg.exe",
                "./ffmpeg",
                "./ffmpeg.exe",
                "/usr/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
                "C:\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe"
        };

        for (String path : commonPaths) {
            File file = new File(path);
            if (file.exists() && file.canExecute()) {
                return path;
            }
        }

        // Try to find in PATH
        try {
            ProcessBuilder pb = new ProcessBuilder("ffmpeg", "-version");
            Process process = pb.start();
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                return "ffmpeg";
            }
        } catch (Exception e) {
            // Not found
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