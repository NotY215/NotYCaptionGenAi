package com.noty.captiongen;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class WhisperTranscriber {

    public static String transcribe(File audioFile, String language, String modelPath) throws Exception {
        System.out.println("Transcribing: " + audioFile.getAbsolutePath());
        System.out.println("Using model: " + modelPath);

        // Get the directory where the model is located
        File modelFile = new File(modelPath);
        String modelDir = modelFile.getParent();
        String modelName = modelFile.getName();

        // Use Whisper.cpp executable if available
        String whisperExecutable = findWhisperExecutable();

        if (whisperExecutable != null) {
            try {
                return transcribeWithWhisperCpp(audioFile, language, modelPath, whisperExecutable);
            } catch (Exception e) {
                System.err.println("Whisper.cpp execution failed: " + e.getMessage());
                System.err.println("Trying Python whisper...");
            }
        }

        // Try Python whisper as fallback
        if (isPythonWhisperInstalled()) {
            try {
                return transcribeWithPythonWhisper(audioFile, language);
            } catch (Exception e) {
                System.err.println("Python whisper execution failed: " + e.getMessage());
            }
        }

        throw new Exception("No working Whisper installation found. Please install whisper.cpp or Python whisper.");
    }

    private static String findWhisperExecutable() {
        String[] possiblePaths = {
                "whisper",
                "whisper.exe",
                "./whisper",
                "./whisper.exe",
                "main",
                "main.exe",
                "./main",
                "./main.exe",
                "whisper-cli",
                "whisper-cli.exe",
                "./whisper-cli",
                "./whisper-cli.exe"
        };

        for (String path : possiblePaths) {
            File file = new File(path);
            if (file.exists() && file.canExecute()) {
                return path;
            }
            try {
                ProcessBuilder pb = new ProcessBuilder(path, "--help");
                Process process = pb.start();
                int exitCode = process.waitFor();
                if (exitCode == 0 || exitCode == 1) {
                    return path;
                }
            } catch (Exception e) {
                // Continue searching
            }
        }
        return null;
    }

    private static String transcribeWithWhisperCpp(File audioFile, String language, String modelPath, String whisperExecutable) throws Exception {
        // First convert to 16kHz WAV if not already
        File wavFile = audioFile;
        if (!audioFile.getName().toLowerCase().endsWith(".wav")) {
            wavFile = AudioExtractor.extractAudio(audioFile);
        }

        String languageCode = getLanguageCode(language);
        String outputPath = wavFile.getParent() + File.separator +
                getFileNameWithoutExtension(wavFile);

        // Build command for whisper.cpp
        List<String> command = new ArrayList<>();
        command.add(whisperExecutable);
        command.add("-m");
        command.add(modelPath);
        command.add("-f");
        command.add(wavFile.getAbsolutePath());
        command.add("-o");
        command.add(outputPath);
        command.add("-t");
        command.add(String.valueOf(Runtime.getRuntime().availableProcessors()));
        command.add("-osrt"); // Output SRT format

        if (!languageCode.equals("auto")) {
            command.add("-l");
            command.add(languageCode);
        }

        System.out.println("Running command: " + String.join(" ", command));

        // Execute whisper.cpp
        ProcessBuilder pb = new ProcessBuilder(command);
        pb.redirectErrorStream(true);
        Process process = pb.start();

        // Read output
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
            throw new Exception("Whisper.cpp failed with exit code: " + exitCode);
        }

        // Read the generated SRT file
        String srtPath = outputPath + ".srt";
        File srtFile = new File(srtPath);
        if (srtFile.exists()) {
            String content = new String(Files.readAllBytes(srtFile.toPath()));
            // Clean up temporary file if it was created
            if (wavFile != audioFile && wavFile.exists()) {
                wavFile.delete();
            }
            return content;
        }

        return output.toString();
    }

    private static boolean isPythonWhisperInstalled() {
        try {
            ProcessBuilder pb = new ProcessBuilder("pip", "show", "openai-whisper");
            Process process = pb.start();
            int exitCode = process.waitFor();
            return exitCode == 0;
        } catch (Exception e) {
            return false;
        }
    }

    private static String transcribeWithPythonWhisper(File audioFile, String language) throws Exception {
        String languageCode = getLanguageCode(language);
        String outputPath = audioFile.getParent() + File.separator +
                getFileNameWithoutExtension(audioFile);

        // Build Python whisper command
        List<String> command = new ArrayList<>();
        command.add("whisper");
        command.add(audioFile.getAbsolutePath());
        command.add("--model");
        command.add("base");
        command.add("--language");
        command.add(languageCode);
        command.add("--output_dir");
        command.add(audioFile.getParent());
        command.add("--output_format");
        command.add("srt");

        ProcessBuilder pb = new ProcessBuilder(command);
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
        if (exitCode != 0) {
            throw new Exception("Python whisper failed with exit code: " + exitCode);
        }

        String srtPath = outputPath + ".srt";
        File srtFile = new File(srtPath);
        if (srtFile.exists()) {
            return new String(Files.readAllBytes(srtFile.toPath()));
        }

        return output.toString();
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

    private static String getFileNameWithoutExtension(File file) {
        String name = file.getName();
        int lastDot = name.lastIndexOf('.');
        if (lastDot > 0) {
            return name.substring(0, lastDot);
        }
        return name;
    }
}