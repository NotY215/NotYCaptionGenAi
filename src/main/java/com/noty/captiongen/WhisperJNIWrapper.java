package com.noty.captiongen;

public class WhisperJNIWrapper {
    static {
        try {
            // Try to load native library
            System.loadLibrary("whisper-jni");
        } catch (UnsatisfiedLinkError e) {
            System.err.println("Native whisper-jni library not loaded: " + e.getMessage());
        }
    }

    public native boolean loadModel(String modelPath);
    public native String transcribe(String audioPath, String language);
    public native void unloadModel();

    public static boolean isAvailable() {
        try {
            WhisperJNIWrapper wrapper = new WhisperJNIWrapper();
            return wrapper.loadModel != null;
        } catch (Exception e) {
            return false;
        }
    }
}