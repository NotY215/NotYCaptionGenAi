package com.noty.captiongen;

public class WhisperJNIWrapper {
    private static boolean nativeLibraryLoaded = false;

    static {
        // JNI not available - we'll use whisper.cpp executable instead
        nativeLibraryLoaded = false;
        System.out.println("Whisper JNI not available - using whisper.cpp executable");
    }

    // Placeholder methods for compatibility
    public boolean loadModel(String modelPath) {
        return false;
    }

    public String transcribe(String audioPath, String language) {
        return null;
    }

    public void unloadModel() {
        // Do nothing
    }

    public static boolean isAvailable() {
        return false;
    }
}