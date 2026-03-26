package com.noty.captiongen;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class WhisperTranscriber {

    public static String transcribe(File audioFile, String language, String modelPath) throws Exception {
        System.out.println("Transcribing: " + audioFile.getAbsolutePath());
        System.out.println("Using model: " + modelPath);

        // Try JNI library first
        if (WhisperJNIWrapper.isAvailable()) {
            try {
                return transcribeWithJNI(audioFile, language, modelPath);
            } catch (Exception e) {
                System.err.println("JNI transcription failed: " + e.getMessage());
            }
        }

        // Try whisper.cpp executable
        String whisperExecutable = findWhisperExecutable();
        if (whisperExecutable != null) {
            try {
                return transcribeWithWhisperCpp(audioFile, language, modelPath, whisperExecutable);
            } catch (Exception e) {
                System.err.println("Whisper.cpp execution failed: " + e.getMessage());
            }
        }

        // Try Python whisper
        if (isPythonWhisperInstalled()) {
            try {
                return transcribeWithPythonWhisper(audioFile, language);
            } catch (Exception e) {
                System.err.println("Python whisper execution failed: " + e.getMessage());
            }
        }

        // If all else fails, show helpful message
        throw new Exception(
                "No Whisper installation found!\n\n" +
                        "Please install one of the following:\n\n" +
                        "1. Download whisper.cpp from: https://github.com/ggerganov/whisper.cpp\n" +
                        "   Place the executable (main.exe or whisper.exe) in the application folder\n\n" +
                        "2. Install Python whisper: pip install openai-whisper\n\n" +
                        "3. Place whisper-jni.dll in the application folder\n\n" +
                        "The application will automatically detect and use any available installation."
        );
    }

    private static String transcribeWithJNI(File audioFile, String language, String modelPath) throws Exception {
        WhisperJNIWrapper whisper = new WhisperJNIWrapper();

        // Load model
        if (!whisper.loadModel(modelPath)) {
            throw new Exception("Failed to load model: " + modelPath);
        }

        // Transcribe
        String languageCode = getLanguageCode(language);
        String result = whisper.transcribe(audioFile.getAbsolutePath(), languageCode);

        // Unload model
        whisper.unloadModel();

        return result;
    }

    private static String findWhisperExecutable() {
        String[] possiblePaths = {
                "whisper", "whisper.exe", "./whisper", "./whisper.exe",
                "main", "main.exe", "./main", "./main.exe",
                "whisper-cli", "whisper-cli.exe", "./whisper-cli", "./whisper-cli.exe"
        };

        for (String path : possiblePaths) {
            File file = new File(path);
            if (file.exists() && file.canExecute()) {
                return path;
            }
        }
        return null;
    }

    private static String transcribeWithWhisperCpp(File audioFile, String language, String modelPath, String whisperExecutable) throws Exception {
        String languageCode = getLanguageCode(language);
        String outputPath = audioFile.getParent() + File.separator +
                getFileNameWithoutExtension(audioFile);

        List<String> command = new ArrayList<>();
        command.add(whisperExecutable);
        command.add("-m");
        command.add(modelPath);
        command.add("-f");
        command.add(audioFile.getAbsolutePath());
        command.add("-o");
        command.add(outputPath);
        command.add("-t");
        command.add(String.valueOf(Runtime.getRuntime().availableProcessors()));
        command.add("-osrt");

        if (!languageCode.equals("auto")) {
            command.add("-l");
            command.add(languageCode);
        }

        ProcessBuilder pb = new ProcessBuilder(command);
        pb.redirectErrorStream(true);
        Process process = pb.start();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            while (reader.readLine() != null) {
                // Consume output
            }
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new Exception("Whisper.cpp failed with exit code: " + exitCode);
        }

        String srtPath = outputPath + ".srt";
        File srtFile = new File(srtPath);
        if (srtFile.exists()) {
            return new String(Files.readAllBytes(srtFile.toPath()));
        }

        throw new Exception("No SRT file generated");
    }

    private static boolean isPythonWhisperInstalled() {
        try {
            ProcessBuilder pb = new ProcessBuilder("python", "-c", "import whisper");
            Process process = pb.start();
            return process.waitFor() == 0;
        } catch (Exception e) {
            return false;
        }
    }

    private static String transcribeWithPythonWhisper(File audioFile, String language) throws Exception {
        String languageCode = getLanguageCode(language);
        String outputPath = audioFile.getParent() + File.separator +
                getFileNameWithoutExtension(audioFile);

        List<String> command = new ArrayList<>();
        command.add("python");
        command.add("-c");
        command.add(String.format(
                "import whisper; model = whisper.load_model('base'); " +
                        "result = model.transcribe('%s', language='%s'); " +
                        "with open('%s.srt', 'w') as f: f.write(result['text'])",
                audioFile.getAbsolutePath().replace("\\", "/"),
                languageCode,
                outputPath.replace("\\", "/")
        ));

        ProcessBuilder pb = new ProcessBuilder(command);
        pb.redirectErrorStream(true);
        Process process = pb.start();

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new Exception("Python whisper failed with exit code: " + exitCode);
        }

        String srtPath = outputPath + ".srt";
        File srtFile = new File(srtPath);
        if (srtFile.exists()) {
            return new String(Files.readAllBytes(srtFile.toPath()));
        }

        throw new Exception("No SRT file generated");
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