package com.noty.captiongen;

public class WhisperJNIWrapper {

    static {
        try {
            System.loadLibrary("whisper-jni");
        } catch (UnsatisfiedLinkError e) {
            System.err.println("Failed to load whisper-jni library");
        }
    }

    // Native method placeholder
    public native String transcribe(String audioPath);

}
