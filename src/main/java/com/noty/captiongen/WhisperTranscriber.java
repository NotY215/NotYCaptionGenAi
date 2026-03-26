package com.noty.captiongen;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class WhisperTranscriber {
    
    public static String transcribe(File audioFile, String language, String modelPath) throws Exception {
        System.out.println("=== Whisper Transcription Started ===");
        System.out.println("Audio file: " + audioFile.getAbsolutePath());
        System.out.println("Model path: " + modelPath);
        System.out.println("Language: " + language);
        
        // First, extract audio if needed
        File wavFile = audioFile;
        if (!audioFile.getName().toLowerCase().endsWith(".wav")) {
            System.out.println("Converting to WAV format...");
            wavFile = AudioExtractor.extractAudio(audioFile);
        }
        
        System.out.println("Using audio file: " + wavFile.getAbsolutePath());
        System.out.println("Audio file size: " + wavFile.length() + " bytes");
        
        // Try to find whisper.cpp executable in files folder
        String whisperExecutable = findWhisperExecutable();
        
        if (whisperExecutable != null) {
            System.out.println("Found whisper executable: " + whisperExecutable);
            try {
                return transcribeWithWhisperCpp(wavFile, language, modelPath, whisperExecutable);
            } catch (Exception e) {
                System.err.println("Whisper.cpp execution failed: " + e.getMessage());
                e.printStackTrace();
                throw new Exception("Whisper.cpp failed: " + e.getMessage() + "\n\nPlease ensure the model file exists at: " + modelPath);
            }
        }
        
        throw new Exception(
            "Could not find whisper.exe!\n\n" +
            "Please make sure whisper.exe is in the 'files' folder.\n" +
            "Current directory: " + System.getProperty("user.dir") + "\n\n" +
            "Files found in files folder:\n" + listFilesInDirectory("files")
        );
    }
    
    private static String listFilesInDirectory(String dirName) {
        File dir = new File(dirName);
        if (!dir.exists()) return "Files folder not found";
        
        File[] files = dir.listFiles();
        if (files == null) return "Unable to list files";
        
        StringBuilder sb = new StringBuilder();
        for (File f : files) {
            if (f.isFile() && (f.getName().endsWith(".exe") || f.getName().contains("whisper"))) {
                sb.append("  - ").append(f.getName()).append("\n");
            }
        }
        return sb.toString();
    }
    
    private static String findWhisperExecutable() {
        // Check in files folder first
        String[] possibleNames = {
            "whisper.exe", "whisper", "main.exe", "main", "whisper-cli.exe", "whisper-cli"
        };
        
        // Check in files folder
        for (String name : possibleNames) {
            File file = new File("files", name);
            if (file.exists()) {
                System.out.println("Found in files folder: " + file.getAbsolutePath());
                return file.getAbsolutePath();
            }
        }
        
        // Check in current directory as fallback
        for (String name : possibleNames) {
            File file = new File(name);
            if (file.exists()) {
                System.out.println("Found in current directory: " + file.getAbsolutePath());
                return file.getAbsolutePath();
            }
        }
        
        // Check in PATH as last resort
        String pathEnv = System.getenv("PATH");
        if (pathEnv != null) {
            String[] paths = pathEnv.split(File.pathSeparator);
            for (String path : paths) {
                for (String name : possibleNames) {
                    File file = new File(path, name);
                    if (file.exists()) {
                        System.out.println("Found in PATH: " + file.getAbsolutePath());
                        return file.getAbsolutePath();
                    }
                }
            }
        }
        
        System.out.println("Could not find whisper.exe in files folder, current directory, or PATH");
        return null;
    }
    
    private static String transcribeWithWhisperCpp(File audioFile, String language, String modelPath, String whisperExecutable) throws Exception {
        String languageCode = getLanguageCode(language);
        String outputPath = audioFile.getParent() + File.separator + 
                           getFileNameWithoutExtension(audioFile);
        
        // Check if model exists
        File modelFile = new File(modelPath);
        if (!modelFile.exists()) {
            throw new Exception("Model file not found: " + modelPath + 
                "\n\nPlease download the model first using the Download button.");
        }
        
        System.out.println("Model file exists: " + modelFile.getAbsolutePath());
        System.out.println("Model file size: " + modelFile.length() + " bytes");
        
        // Build command for whisper.cpp
        List<String> command = new ArrayList<>();
        command.add(whisperExecutable);
        command.add("-m");
        command.add(modelPath);
        command.add("-f");
        command.add(audioFile.getAbsolutePath());
        command.add("-of");
        command.add(outputPath);
        command.add("-t");
        command.add(String.valueOf(Runtime.getRuntime().availableProcessors()));
        command.add("--output-srt");
        
        if (!languageCode.equals("auto")) {
            command.add("-l");
            command.add(languageCode);
        }
        
        System.out.println("\nExecuting command:");
        System.out.println(String.join(" ", command));
        System.out.println();
        
        // Execute whisper.cpp
        ProcessBuilder pb = new ProcessBuilder(command);
        pb.redirectErrorStream(true);
        pb.directory(new File(System.getProperty("user.dir")));
        
        Process process = pb.start();
        
        // Read output for progress monitoring
        StringBuilder processOutput = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                processOutput.append(line).append("\n");
                System.out.println(line);
                
                if (line.contains("transcribe") || line.contains("processing") || 
                    line.contains("progress") || line.contains("[")) {
                    System.out.println("Progress: " + line);
                }
            }
        }
        
        int exitCode = process.waitFor();
        System.out.println("\nWhisper process completed with exit code: " + exitCode);
        
        if (exitCode != 0) {
            throw new Exception("Whisper.cpp failed with exit code: " + exitCode + 
                "\n\nOutput:\n" + processOutput.toString());
        }
        
        // Read the generated SRT file
        String srtPath = outputPath + ".srt";
        File srtFile = new File(srtPath);
        
        System.out.println("Looking for SRT file at: " + srtPath);
        
        if (srtFile.exists()) {
            String content = new String(Files.readAllBytes(srtFile.toPath()));
            System.out.println("Success! Generated " + content.length() + " characters of subtitles");
            System.out.println("SRT file saved to: " + srtPath);
            return content;
        }
        
        // Try alternative naming patterns
        String[] altPaths = {
            outputPath + "_output.srt",
            outputPath + ".srt",
            audioFile.getParent() + File.separator + getFileNameWithoutExtension(audioFile) + ".srt"
        };
        
        for (String altPath : altPaths) {
            File altFile = new File(altPath);
            if (altFile.exists()) {
                System.out.println("Found SRT at alternative path: " + altPath);
                String content = new String(Files.readAllBytes(altFile.toPath()));
                return content;
            }
        }
        
        // List all files in output directory for debugging
        File outputDir = new File(audioFile.getParent());
        File[] files = outputDir.listFiles();
        if (files != null) {
            System.out.println("\nFiles in output directory:");
            for (File f : files) {
                if (f.getName().endsWith(".srt") || f.getName().contains("whisper")) {
                    System.out.println("  - " + f.getName());
                }
            }
        }
        
        throw new Exception("No SRT file generated. Whisper output:\n" + processOutput.toString());
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