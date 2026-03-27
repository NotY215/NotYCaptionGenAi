package com.noty.captiongen;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

public class AudioExtractor {

    private static final String[] FFMPEG_PATHS = {
            "files/ffmpeg.exe",
            "ffmpeg.exe",
            "ffmpeg",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg"
    };

    public static File extractAudio(File inputFile) throws Exception {
        LoggingUtil.info("Extracting audio from: " + inputFile.getAbsolutePath());

        String inputPath = inputFile.getAbsolutePath();
        String outputPath = inputFile.getParent() + File.separator +
                getFileNameWithoutExtension(inputFile) + "_temp.wav";

        // If input is already WAV, just return it
        if (inputPath.toLowerCase().endsWith(".wav")) {
            LoggingUtil.info("File is already WAV format");
            return inputFile;
        }

        // Find FFmpeg
        String ffmpegPath = findFFmpeg();
        LoggingUtil.info("Using FFmpeg: " + ffmpegPath);

        // Build FFmpeg command
        List<String> command = new ArrayList<>();
        command.add(ffmpegPath);
        command.add("-i");
        command.add(inputPath);
        command.add("-acodec");
        command.add("pcm_s16le");
        command.add("-ar");
        command.add("16000");
        command.add("-ac");
        command.add("1");
        command.add("-y");
        command.add(outputPath);

        LoggingUtil.info("Running FFmpeg command: " + String.join(" ", command));

        ProcessBuilder pb = new ProcessBuilder(command);
        pb.redirectErrorStream(true);
        Process process = pb.start();

        // Read output
        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
                if (line.contains("Duration") || line.contains("Stream")) {
                    LoggingUtil.info("  " + line);
                }
            }
        }

        boolean completed = process.waitFor(120, TimeUnit.SECONDS);
        if (!completed) {
            process.destroyForcibly();
            throw new Exception("FFmpeg extraction timed out");
        }

        int exitCode = process.exitValue();
        if (exitCode != 0) {
            throw new Exception("FFmpeg extraction failed with exit code: " + exitCode +
                    "\nOutput: " + output.toString());
        }

        File outputFile = new File(outputPath);
        if (!outputFile.exists() || outputFile.length() == 0) {
            throw new Exception("Audio extraction failed: Output file is empty or missing");
        }

        LoggingUtil.info("Audio extracted successfully: " + outputFile.length() + " bytes");
        return outputFile;
    }

    private static String findFFmpeg() {
        for (String path : FFMPEG_PATHS) {
            File file = new File(path);
            if (file.exists() && file.canExecute()) {
                return path;
            }
        }

        // Try to find in PATH
        try {
            ProcessBuilder pb = new ProcessBuilder("ffmpeg", "-version");
            Process process = pb.start();
            boolean completed = process.waitFor(5, TimeUnit.SECONDS);
            if (completed && process.exitValue() == 0) {
                return "ffmpeg";
            }
        } catch (Exception e) {
            // Not found
        }

        return "ffmpeg";
    }

    private static String getFileNameWithoutExtension(File file) {
        String name = file.getName();
        int dot = name.lastIndexOf('.');
        return dot > 0 ? name.substring(0, dot) : name;
    }
}