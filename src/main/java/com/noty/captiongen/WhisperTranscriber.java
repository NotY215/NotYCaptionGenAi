package com.noty.captiongen;

import java.io.*;

public class WhisperTranscriber {

    public static String transcribe(File audioFile, String language, String modelPath) throws Exception {
        LoggingUtil.info("=== Whisper Transcription Started ===");
        LoggingUtil.info("Audio file: " + audioFile.getAbsolutePath());
        LoggingUtil.info("Model path: " + modelPath);
        LoggingUtil.info("Language: " + language);

        // Check if model exists
        File modelFile = new File(modelPath);
        if (!modelFile.exists()) {
            throw new Exception("Model file not found: " + modelPath +
                    "\n\nPlease download the model first using the download option.");
        }

        if (modelFile.length() < 1000000) {
            throw new Exception("Model file appears corrupted (size: " + modelFile.length() + " bytes).\n" +
                    "Please delete the file and download it again.");
        }

        LoggingUtil.info("Model file exists: " + modelFile.getAbsolutePath());
        LoggingUtil.info("Model file size: " + modelFile.length() + " bytes");

        // Use embedded Python Whisper
        return PythonEmbeddedTranscriber.transcribe(audioFile, language, modelPath);
    }
}