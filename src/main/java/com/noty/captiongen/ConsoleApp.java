package com.noty.captiongen;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

public class ConsoleApp {
    
    private Scanner scanner;
    private String videoPath;
    private File selectedFile;
    private String selectedModel;
    private String modelPath;
    private boolean modelExists;
    private String lineType;
    private int lineCount;
    
    private static class ModelInfo {
        String name;
        String fileName;
        long sizeBytes;
        String url;
        
        ModelInfo(String name, String fileName, long sizeBytes, String url) {
            this.name = name;
            this.fileName = fileName;
            this.sizeBytes = sizeBytes;
            this.url = url;
        }
    }
    
    private final ModelInfo[] MODELS = {
        new ModelInfo("Tiny (39 MB) - Built-in", "models/ggml-tiny.bin", 39 * 1024 * 1024, ""),
        new ModelInfo("Base (142 MB) - Built-in", "models/ggml-base.bin", 142 * 1024 * 1024, ""),
        new ModelInfo("Small (466 MB)", "models/ggml-small.bin", 466 * 1024 * 1024, 
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"),
        new ModelInfo("Medium (1.5 GB)", "models/ggml-medium.bin", 1536 * 1024 * 1024,
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin"),
        new ModelInfo("Large V1 (2.9 GB)", "models/ggml-large-v1.bin", 2900 * 1024 * 1024,
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin")
    };
    
    private final String[] ALLOWED_EXTENSIONS = {".mp4", ".mkv", ".avi", ".wmv", ".mpeg", ".mp3", ".wav", ".m4a", ".flac"};
    
    public ConsoleApp() {
        scanner = new Scanner(System.in);
        LoggingUtil.initialize();
    }
    
    public void start() {
        printBanner();
        createRequiredFolders();
        extractEmbeddedFiles();
        
        boolean running = true;
        while (running) {
            try {
                // Step A: Get video/audio path
                videoPath = getVideoPath();
                if (videoPath == null) continue;
                
                selectedFile = new File(videoPath);
                if (!selectedFile.exists()) {
                    System.out.println("\n❌ File does not exist! Please try again.");
                    continue;
                }
                
                // Check extension
                String ext = getFileExtension(selectedFile).toLowerCase();
                boolean validExt = false;
                for (String allowed : ALLOWED_EXTENSIONS) {
                    if (ext.equals(allowed)) {
                        validExt = true;
                        break;
                    }
                }
                if (!validExt) {
                    System.out.println("\n❌ Unsupported file format! Allowed: " + String.join(", ", ALLOWED_EXTENSIONS));
                    continue;
                }
                
                boolean modelSelected = false;
                while (!modelSelected) {
                    int choice = showModelMenu();
                    if (choice == 0) break;
                    
                    int modelChoice = showModelSelection();
                    if (modelChoice == 0) continue;
                    
                    selectedModel = MODELS[modelChoice - 1].name;
                    modelPath = MODELS[modelChoice - 1].fileName;
                    boolean isBuiltIn = (modelChoice == 1 || modelChoice == 2);
                    
                    System.out.println("\n📦 You selected: " + selectedModel);
                    
                    File modelFile = new File(modelPath);
                    modelExists = modelFile.exists() && modelFile.length() > 0;
                    
                    if (modelExists) {
                        System.out.println("✅ Model already exists! Ready to use.");
                        modelSelected = true;
                    } else {
                        int downloadChoice = showDownloadMenu(isBuiltIn);
                        if (downloadChoice == 0) continue;
                        else if (downloadChoice == 1) {
                            if (isBuiltIn) {
                                System.out.print("📦 Extracting built-in model...");
                                extractBuiltInModel(MODELS[modelChoice - 1].fileName);
                                System.out.println(" ✅");
                                modelExists = true;
                                modelSelected = true;
                            } else {
                                System.out.println("📥 Downloading model...");
                                boolean success = downloadModel(MODELS[modelChoice - 1]);
                                if (success) {
                                    modelExists = true;
                                    modelSelected = true;
                                } else {
                                    System.out.println("❌ Download failed. Please try again.");
                                }
                            }
                        }
                    }
                }
                
                if (!modelSelected) continue;
                
                int lineTypeChoice = showLineTypeMenu();
                if (lineTypeChoice == 0) continue;
                lineType = (lineTypeChoice == 1) ? "words" : "letters";
                
                boolean valid = false;
                while (!valid) {
                    System.out.print("\n📝 How many " + lineType + " per line? (1-30) [0 to go back]: ");
                    String input = scanner.nextLine().trim();
                    if (input.equals("0")) {
                        valid = true;
                        continue;
                    }
                    try {
                        lineCount = Integer.parseInt(input);
                        if (lineCount >= 1 && lineCount <= 30) {
                            valid = true;
                        } else {
                            System.out.println("❌ Please enter a number between 1 and 30.");
                        }
                    } catch (NumberFormatException e) {
                        System.out.println("❌ Invalid input. Please enter a number.");
                    }
                }
                if (lineCount == 0) continue;
                
                boolean confirmed = showConfirmation();
                if (!confirmed) continue;
                
                generateSubtitles();
                thankYouAndOpenLinks();
                
                System.out.print("\n🔄 Process another video? (1: Yes / 0: No): ");
                String nextChoice = scanner.nextLine().trim();
                if (!nextChoice.equals("1")) {
                    running = false;
                    System.out.println("\n👋 Thank you for using NotYCaptionGenAi!");
                    System.out.println("🔗 Join our Telegram: https://t.me/Noty_215");
                    System.out.println("🎥 Subscribe on YouTube: https://www.youtube.com/@NotY215");
                }
                
            } catch (Exception e) {
                LoggingUtil.error("Error: " + e.getMessage(), e);
                System.out.println("\n❌ An error occurred: " + e.getMessage());
            }
        }
        
        scanner.close();
        LoggingUtil.close();
    }
    
    private void printBanner() {
        System.out.println("╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║                    NotYCaptionGenAi v3.0                      ║");
        System.out.println("║              AI-Powered Subtitle Generator                   ║");
        System.out.println("║                   Developed by NotY215                       ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        System.out.println();
    }
    
    private String getVideoPath() {
        System.out.println("╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║  Step A: Provide Video/Audio File Path                      ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        System.out.print("\n📁 Enter file path");
        System.out.print("\n   Supported formats: " + String.join(", ", ALLOWED_EXTENSIONS));
        System.out.print("\n   [Type 'exit' to quit]: ");
        
        String path = scanner.nextLine().trim();
        if (path.equalsIgnoreCase("exit")) {
            System.out.println("\n👋 Goodbye!");
            System.exit(0);
        }
        return path;
    }
    
    private int showModelMenu() {
        System.out.println("\n╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║  Step B: Choose Model Option                                 ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        System.out.println("   [1] Choose Model");
        System.out.println("   [0] Go Back (Select different file)");
        System.out.print("\n👉 Enter your choice: ");
        
        String input = scanner.nextLine().trim();
        if (input.equals("0")) return 0;
        if (input.equals("1")) return 1;
        return showModelMenu();
    }
    
    private int showModelSelection() {
        System.out.println("\n╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║  Step C: Select Whisper Model                                ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        for (int i = 0; i < MODELS.length; i++) {
            System.out.printf("   [%d] %s%n", i + 1, MODELS[i].name);
        }
        System.out.println("   [0] Back to previous menu");
        System.out.print("\n👉 Enter your choice (1-" + MODELS.length + "): ");
        
        String input = scanner.nextLine().trim();
        if (input.equals("0")) return 0;
        
        try {
            int choice = Integer.parseInt(input);
            if (choice >= 1 && choice <= MODELS.length) return choice;
        } catch (NumberFormatException e) { }
        
        System.out.println("❌ Invalid choice. Please try again.");
        return showModelSelection();
    }
    
    private int showDownloadMenu(boolean isBuiltIn) {
        System.out.println("\n╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║  Step D: Model Availability                                  ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        
        if (isBuiltIn) {
            System.out.println("   This model is built-in!");
            System.out.println("   [1] Extract Model");
            System.out.println("   [0] Back to model selection");
        } else {
            System.out.println("   Model not found. Download required.");
            System.out.println("   [1] Download Model");
            System.out.println("   [0] Back to model selection");
        }
        System.out.print("\n👉 Enter your choice: ");
        
        String input = scanner.nextLine().trim();
        if (input.equals("0")) return 0;
        if (input.equals("1")) return 1;
        return showDownloadMenu(isBuiltIn);
    }
    
    private void extractBuiltInModel(String modelPath) {
        try {
            String modelName = new File(modelPath).getName();
            InputStream in = getClass().getResourceAsStream("/" + modelName);
            if (in == null) in = getClass().getResourceAsStream("/models/" + modelName);
            if (in != null) {
                File outFile = new File(modelPath);
                outFile.getParentFile().mkdirs();
                Files.copy(in, outFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
            }
        } catch (Exception e) {
            LoggingUtil.error("Failed to extract model: " + e.getMessage());
        }
    }
    
    private boolean downloadModel(ModelInfo model) {
        ModelDownloader downloader = new ModelDownloader();
        final boolean[] success = {false};
        final Object lock = new Object();
        
        System.out.println("\n📥 Downloading " + model.name);
        System.out.println("   Size: " + (model.sizeBytes / (1024 * 1024)) + " MB");
        System.out.println("   URL: " + model.url);
        System.out.println();
        
        downloader.downloadModel(model.url, model.fileName, model.sizeBytes, new ModelDownloader.DownloadCallback() {
            @Override
            public void onProgress(int percent, long downloaded, long total, double speed) {
                System.out.print("\r   Progress: " + percent + "% | " + 
                    formatSize(downloaded) + " / " + formatSize(total) + 
                    " | Speed: " + String.format("%.2f", speed) + " KB/s    ");
            }
            
            @Override
            public void onComplete(boolean s) {
                success[0] = s;
                synchronized (lock) { lock.notify(); }
            }
            
            @Override
            public void onCancel() {
                success[0] = false;
                synchronized (lock) { lock.notify(); }
            }
        });
        
        synchronized (lock) {
            try { lock.wait(); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        }
        
        System.out.println();
        return success[0];
    }
    
    private int showLineTypeMenu() {
        System.out.println("\n╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║  Step E: Choose Line Breaking Method                         ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        System.out.println("   [1] Break by Words");
        System.out.println("   [2] Break by Letters");
        System.out.println("   [0] Back to model selection");
        System.out.print("\n👉 Enter your choice: ");
        
        String input = scanner.nextLine().trim();
        if (input.equals("0")) return 0;
        if (input.equals("1")) return 1;
        if (input.equals("2")) return 2;
        return showLineTypeMenu();
    }
    
    private boolean showConfirmation() {
        System.out.println("\n╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║  Step G: Confirm Generation                                  ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        System.out.println("\n📁 File: " + selectedFile.getAbsolutePath());
        System.out.println("🤖 Model: " + selectedModel);
        System.out.println("📝 Line Type: " + lineType);
        System.out.println("🔢 " + lineCount + " " + lineType + " per line");
        System.out.println("\n   [1] Continue and Generate Subtitles");
        System.out.println("   [0] Back to previous step");
        System.out.print("\n👉 Enter your choice: ");
        
        String input = scanner.nextLine().trim();
        if (input.equals("1")) return true;
        if (input.equals("0")) return false;
        return showConfirmation();
    }
    
    private void generateSubtitles() {
        System.out.println("\n╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║  Generating Subtitles                                        ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        
        try {
            System.out.print("🔧 Initializing Python environment...");
            PythonInstaller.ensureWhisperInstalled();
            System.out.println(" ✅");
            
            System.out.print("🎵 Extracting audio from video...");
            File audioFile = AudioExtractor.extractAudio(selectedFile);
            System.out.println(" ✅");
            
            System.out.print("🎤 Transcribing with Whisper AI...");
            String transcription = WhisperTranscriber.transcribe(audioFile, "English", modelPath);
            System.out.println(" ✅");
            
            System.out.print("📝 Generating SRT subtitles...");
            int maxCount = lineCount;
            if (lineType.equals("words")) maxCount = lineCount * 5;
            String srtContent = SRTGenerator.generateSRT(transcription, maxCount);
            System.out.println(" ✅");
            
            String outputPath = selectedFile.getParent() + File.separator + 
                getFileNameWithoutExtension(selectedFile) + ".srt";
            Files.write(Paths.get(outputPath), srtContent.getBytes());
            System.out.println("💾 Saved to: " + outputPath);
            
            if (!selectedFile.getName().toLowerCase().endsWith(".wav") && audioFile.exists()) {
                audioFile.delete();
            }
            
            System.out.println("\n✅ Subtitle generation completed successfully!");
            
        } catch (Exception e) {
            LoggingUtil.error("Generation failed: " + e.getMessage(), e);
            System.out.println("\n❌ Error generating subtitles: " + e.getMessage());
        }
    }
    
    private void thankYouAndOpenLinks() {
        System.out.println("\n╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║  Thank You for Using NotYCaptionGenAi!                       ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        System.out.println("\n🎉 Your subtitles have been generated successfully!");
        
        System.out.println("\n🔗 Opening links in your browser...");
        try {
            java.awt.Desktop.getDesktop().browse(new java.net.URI("https://t.me/Noty_215"));
            System.out.println("   ✓ Telegram channel opened");
            Thread.sleep(1000);
            java.awt.Desktop.getDesktop().browse(new java.net.URI("https://www.youtube.com/@NotY215"));
            System.out.println("   ✓ YouTube channel opened");
        } catch (Exception e) {
            System.out.println("   ⚠ Could not open browser. Please visit manually:");
            System.out.println("   Telegram: https://t.me/Noty_215");
            System.out.println("   YouTube: https://www.youtube.com/@NotY215");
        }
    }
    
    private void createRequiredFolders() {
        new File("models").mkdirs();
        new File("files").mkdirs();
        new File("temp").mkdirs();
        new File("python").mkdirs();
        new File("logs").mkdirs();
    }
    
    private void extractEmbeddedFiles() {
        try {
            extractFileIfNeeded("/ffmpeg.exe", "files/ffmpeg.exe");
            extractFileIfNeeded("/ffprobe.exe", "files/ffprobe.exe");
            extractModelIfNeeded("ggml-tiny.bin", "models/ggml-tiny.bin");
            extractModelIfNeeded("ggml-base.bin", "models/ggml-base.bin");
            extractPythonFiles();
        } catch (Exception e) {
            System.err.println("Warning: Could not extract some files: " + e.getMessage());
        }
    }
    
    private void extractFileIfNeeded(String resourcePath, String destPath) {
        File destFile = new File(destPath);
        if (!destFile.exists()) {
            try {
                InputStream in = getClass().getResourceAsStream(resourcePath);
                if (in == null) in = getClass().getResourceAsStream("/resources" + resourcePath);
                if (in != null) {
                    Files.copy(in, destFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                    destFile.setExecutable(true);
                }
            } catch (Exception e) { }
        }
    }
    
    private void extractModelIfNeeded(String resourceName, String destPath) {
        File modelFile = new File(destPath);
        if (!modelFile.exists() || modelFile.length() == 0) {
            try {
                InputStream in = getClass().getResourceAsStream("/" + resourceName);
                if (in == null) in = getClass().getResourceAsStream("/models/" + resourceName);
                if (in != null) {
                    Files.copy(in, modelFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                }
            } catch (Exception e) { }
        }
    }
    
    private void extractPythonFiles() {
        File pythonDir = new File("python");
        if (!pythonDir.exists()) pythonDir.mkdirs();
        
        String[] pythonFiles = {
            "python.exe", "pythonw.exe", "python3.dll", "python311.dll",
            "python311.zip", "python311._pth", "python.cat", "LICENSE.txt",
            "libcrypto-3.dll", "libffi-8.dll", "libssl-3.dll", "pyexpat.pyd",
            "select.pyd", "sqlite3.dll", "unicodedata.pyd", "vcruntime140.dll",
            "vcruntime140_1.dll", "winsound.pyd", "_asyncio.pyd", "_bz2.pyd",
            "_ctypes.pyd", "_decimal.pyd", "_elementtree.pyd", "_hashlib.pyd",
            "_lzma.pyd", "_msi.pyd", "_multiprocessing.pyd", "_overlapped.pyd",
            "_queue.pyd", "_socket.pyd", "_sqlite3.pyd", "_ssl.pyd", "_uuid.pyd", "_zoneinfo.pyd"
        };
        
        for (String fileName : pythonFiles) {
            try {
                InputStream in = getClass().getResourceAsStream("/Python/" + fileName);
                if (in == null) in = getClass().getResourceAsStream("/resources/Python/" + fileName);
                if (in != null) {
                    File outFile = new File(pythonDir, fileName);
                    if (!outFile.exists()) {
                        Files.copy(in, outFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                    }
                }
            } catch (Exception e) { }
        }
    }
    
    private String formatSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        if (bytes < 1024 * 1024 * 1024) return String.format("%.1f MB", bytes / (1024.0 * 1024));
        return String.format("%.2f GB", bytes / (1024.0 * 1024 * 1024));
    }
    
    private String getFileExtension(File file) {
        String name = file.getName();
        int dot = name.lastIndexOf('.');
        return dot > 0 ? name.substring(dot) : "";
    }
    
    private String getFileNameWithoutExtension(File file) {
        String name = file.getName();
        int dot = name.lastIndexOf('.');
        return dot > 0 ? name.substring(0, dot) : name;
    }
}