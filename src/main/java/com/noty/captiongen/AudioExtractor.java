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

        // Try system FFmpeg first
        String ffmpegPath = findFFmpeg();

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

        // Read output to avoid buffer blocking
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            while (reader.readLine() != null) {
                // Consume output
            }
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new Exception("FFmpeg extraction failed with exit code: " + exitCode);
        }

        File outputFile = new File(outputPath);
        if (!outputFile.exists() || outputFile.length() == 0) {
            throw new Exception("Audio extraction failed: Output file is empty or missing");
        }

        return outputFile;
    }

    private static String findFFmpeg() {
        // Check common locations
        String[] commonPaths = {
                "ffmpeg",
                "ffmpeg.exe",
                "/usr/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
                "C:\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
        };

        for (String path : commonPaths) {
            File file = new File(path);
            if (file.exists() && file.canExecute()) {
                return path;
            }
        }

        // Return default, hoping it's in PATH
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