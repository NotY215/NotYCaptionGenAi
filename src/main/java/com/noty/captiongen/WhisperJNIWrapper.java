package com.noty.captiongen;

public class WhisperJNIWrapper {
    private static boolean nativeLibraryLoaded = false;

    static {
        try {
            // Try to load native library
            System.loadLibrary("whisper-jni");
            nativeLibraryLoaded = true;
            System.out.println("Whisper JNI library loaded successfully");
        } catch (UnsatisfiedLinkError e) {
            System.err.println("Native whisper-jni library not loaded: " + e.getMessage());
            System.err.println("Will use fallback transcription mode");
            nativeLibraryLoaded = false;
        } catch (SecurityException e) {
            System.err.println("Security exception loading native library: " + e.getMessage());
            nativeLibraryLoaded = false;
        }
    }

    // Native method declarations
    public native boolean loadModel(String modelPath);
    public native String transcribe(String audioPath, String language);
    public native void unloadModel();

    public static boolean isAvailable() {
        return nativeLibraryLoaded;
    }
}