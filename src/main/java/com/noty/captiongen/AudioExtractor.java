package com.noty.captiongen;

import net.bramp.ffmpeg.FFmpeg;
import net.bramp.ffmpeg.FFmpegExecutor;
import net.bramp.ffmpeg.FFprobe;
import net.bramp.ffmpeg.builder.FFmpegBuilder;
import java.io.*;
import java.nio.file.*;

public class AudioExtractor {

    public static File extractAudio(File inputFile) throws Exception {
        String inputPath = inputFile.getAbsolutePath();
        String outputPath = inputFile.getParent() + File.separator +
                getFileNameWithoutExtension(inputFile) + "_temp.wav";

        // If input is already WAV, just return it
        if (inputPath.toLowerCase().endsWith(".wav")) {
            return inputFile;
        }

        // Check if FFmpeg exists in current directory
        String ffmpegPath = findFFmpeg();

        try {
            FFmpeg ffmpeg = new FFmpeg(ffmpegPath);
            FFprobe ffprobe = new FFprobe(ffmpegPath.replace("ffmpeg", "ffprobe"));

            FFmpegBuilder builder = new FFmpegBuilder()
                    .setInput(inputPath)
                    .overrideOutputFiles(true)
                    .addOutput(outputPath)
                    .setAudioCodec("pcm_s16le")
                    .setAudioSampleRate(16000)
                    .setAudioChannels(1)
                    .done();

            FFmpegExecutor executor = new FFmpegExecutor(ffmpeg, ffprobe);
            executor.createJob(builder).run();

            return new File(outputPath);

        } catch (Exception e) {
            // Fallback: Use embedded FFmpeg
            return extractWithEmbeddedFFmpeg(inputFile, outputPath);
        }
    }

    private static File extractWithEmbeddedFFmpeg(File inputFile, String outputPath) throws Exception {
        String os = System.getProperty("os.name").toLowerCase();
        String ffmpegExecutable;

        if (os.contains("win")) {
            ffmpegExecutable = "ffmpeg.exe";
        } else if (os.contains("mac")) {
            ffmpegExecutable = "ffmpeg";
        } else {
            ffmpegExecutable = "ffmpeg";
        }

        // Check if ffmpeg is in resources
        File ffmpegFile = new File(ffmpegExecutable);
        if (!ffmpegFile.exists()) {
            // Extract from JAR
            try (InputStream is = GUI.class.getResourceAsStream("/ffmpeg/" + ffmpegExecutable)) {
                if (is != null) {
                    Files.copy(is, ffmpegFile.toPath());
                    ffmpegFile.setExecutable(true);
                }
            }
        }

        ProcessBuilder pb = new ProcessBuilder(
                ffmpegFile.getAbsolutePath(),
                "-i", inputFile.getAbsolutePath(),
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                "-y",
                outputPath
        );

        pb.redirectErrorStream(true);
        Process process = pb.start();
        process.waitFor();

        return new File(outputPath);
    }

    private static String findFFmpeg() {
        // Check common locations
        String[] commonPaths = {
                "ffmpeg",
                "ffmpeg.exe",
                "/usr/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
                "C:\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
        };

        for (String path : commonPaths) {
            File file = new File(path);
            if (file.exists() && file.canExecute()) {
                return path;
            }
        }

        // Return default, hoping it's in PATH
        return "ffmpeg";
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