package com.noty.captiongen;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class WhisperTranscriber {

    public static String transcribe(File audioFile, String language, String modelPath) throws Exception {
        System.out.println("Transcribing: " + audioFile.getAbsolutePath());
        System.out.println("Using model: " + modelPath);

        // Check if we can use actual Whisper (if installed)
        if (isWhisperInstalled()) {
            try {
                return transcribeWithWhisper(audioFile, language, modelPath);
            } catch (Exception e) {
                System.err.println("Whisper execution failed: " + e.getMessage());
                System.err.println("Falling back to simulated transcription");
            }
        }

        // Fallback to simulation for demonstration
        return generateSimulatedTranscription(audioFile);
    }

    private static boolean isWhisperInstalled() {
        try {
            ProcessBuilder pb = new ProcessBuilder("whisper", "--help");
            Process process = pb.start();
            int exitCode = process.waitFor();
            return exitCode == 0;
        } catch (Exception e) {
            return false;
        }
    }

    private static String transcribeWithWhisper(File audioFile, String language, String modelPath) throws Exception {
        String languageCode = getLanguageCode(language);
        String outputPath = audioFile.getParent() + File.separator +
                getFileNameWithoutExtension(audioFile);

        ProcessBuilder pb = new ProcessBuilder(
                "whisper",
                audioFile.getAbsolutePath(),
                "--model", getModelType(modelPath),
                "--language", languageCode,
                "--output_dir", audioFile.getParent(),
                "--output_format", "srt"
        );

        pb.redirectErrorStream(true);
        Process process = pb.start();

        // Read output
        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new Exception("Whisper transcription failed: " + output.toString());
        }

        // Read the generated SRT file
        String srtPath = outputPath + ".srt";
        File srtFile = new File(srtPath);
        if (srtFile.exists()) {
            String content = new String(Files.readAllBytes(srtFile.toPath()));
            return content;
        }

        return output.toString();
    }

    private static String getModelType(String modelPath) {
        String fileName = new File(modelPath).getName();
        if (fileName.contains("tiny")) return "tiny";
        if (fileName.contains("base")) return "base";
        if (fileName.contains("small")) return "small";
        if (fileName.contains("medium")) return "medium";
        if (fileName.contains("large")) return "large";
        return "base";
    }

    private static String getLanguageCode(String language) {
        switch (language) {
            case "English": return "en";
            case "Hindi": return "hi";
            case "Japanese": return "ja";
            case "Spanish": return "es";
            case "French": return "fr";
            case "German": return "de";
            case "Chinese": return "zh";
            case "Arabic": return "ar";
            case "Russian": return "ru";
            case "Korean": return "ko";
            default: return "auto";
        }
    }

    private static String generateSimulatedTranscription(File audioFile) {
        StringBuilder sb = new StringBuilder();

        long fileSize = audioFile.length();
        int wordCount = Math.min(500, Math.max(50, (int) (fileSize / 50000)));

        String[] sampleWords = {
                "Welcome", "to", "NotYCaptionGenAi", "the", "AI", "powered", "subtitle", "generator",
                "This", "is", "a", "simulated", "transcription", "using", "the", "Whisper", "AI", "model",
                "The", "actual", "transcription", "would", "be", "generated", "by", "the", "real",
                "Whisper", "implementation", "when", "properly", "configured", "on", "your", "system"
        };

        double duration = Math.min(300, wordCount * 0.3);
        double wordDuration = duration / wordCount;
        double currentTime = 0.0;

        for (int i = 0; i < wordCount; i++) {
            String word = sampleWords[i % sampleWords.length];
            String timeStart = formatTime(currentTime);
            currentTime += wordDuration;
            String timeEnd = formatTime(currentTime);

            sb.append(String.format("%d\n%s --> %s\n%s\n\n",
                    i + 1, timeStart, timeEnd, word));
        }

        return sb.toString();
    }

    private static String formatTime(double seconds) {
        int hours = (int) (seconds / 3600);
        int minutes = (int) ((seconds % 3600) / 60);
        int secs = (int) (seconds % 60);
        int millis = (int) ((seconds - secs) * 1000);

        return String.format("%02d:%02d:%02d,%03d", hours, minutes, secs, millis);
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