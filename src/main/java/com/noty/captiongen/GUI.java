package com.noty.captiongen;

import javafx.application.Platform;
import javafx.embed.swing.JFXPanel;
import javafx.scene.Scene;
import javafx.scene.web.WebView;
import javafx.scene.web.WebEngine;
import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.net.URI;
import java.net.URL;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import javax.swing.filechooser.FileNameExtensionFilter;
import javafx.concurrent.Worker;
import netscape.javascript.JSObject;

public class GUI extends JFrame {
    private JFXPanel jfxPanel;
    private WebEngine webEngine;
    private File selectedFile;
    private String selectedModelPath;
    private boolean modelAvailable;
    private ModelDownloader modelDownloader;
    private DownloadProgressDialog downloadDialog;
    
    // Model information
    private static final class ModelInfo {
        String name;
        String url;
        String fileName;
        long sizeBytes;
        boolean isEmbedded;
        
        ModelInfo(String name, String url, String fileName, long sizeBytes, boolean isEmbedded) {
            this.name = name;
            this.url = url;
            this.fileName = fileName;
            this.sizeBytes = sizeBytes;
            this.isEmbedded = isEmbedded;
        }
    }
    
    private final ModelInfo[] MODELS = {
        new ModelInfo("Tiny (39 MB)", 
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
            "models/ggml-tiny.bin", 39 * 1024 * 1024, true),
        new ModelInfo("Base (142 MB)", 
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
            "models/ggml-base.bin", 142 * 1024 * 1024, true),
        new ModelInfo("Small (466 MB)", 
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
            "models/ggml-small.bin", 466 * 1024 * 1024, false),
        new ModelInfo("Medium (1.5 GB)", 
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
            "models/ggml-medium.bin", 1536 * 1024 * 1024, false),
        new ModelInfo("Large V1 (2.9 GB)", 
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin",
            "models/ggml-large-v1.bin", 2900 * 1024 * 1024, false)
    };
    
    public GUI() {
        setTitle("NotYCaptionGenAi - AI Subtitle Generator");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1200, 800);
        setLocationRelativeTo(null);
        
        // Create required folders
        createRequiredFolders();
        
        // Copy embedded files
        copyEmbeddedFiles();
        
        // Extract models
        extractEmbeddedModels();
        
        // Initialize JavaFX
        initJavaFX();
        
        // Set icon
        setAppIcon();
        
        // Check whisper executable
        checkWhisperExecutable();
    }
    
    private void createRequiredFolders() {
        new File("models").mkdirs();
        new File("files").mkdirs();
        new File("temp").mkdirs();
    }
    
    private void copyEmbeddedFiles() {
        copyFileIfNeeded("/whisper.exe", "files/whisper.exe");
        copyFileIfNeeded("/ffmpeg.exe", "files/ffmpeg.exe");
        copyFileIfNeeded("/ffprobe.exe", "files/ffprobe.exe");
    }
    
    private void copyFileIfNeeded(String resourcePath, String destPath) {
        File destFile = new File(destPath);
        if (!destFile.exists()) {
            try {
                InputStream in = getClass().getResourceAsStream(resourcePath);
                if (in != null) {
                    Files.copy(in, destFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                    System.out.println("Extracted: " + destPath);
                    destFile.setExecutable(true);
                }
            } catch (Exception e) {
                System.err.println("Failed to extract: " + destPath);
            }
        }
    }
    
    private void extractEmbeddedModels() {
        extractModelIfNeeded("ggml-tiny.bin", "models/ggml-tiny.bin");
        extractModelIfNeeded("ggml-base.bin", "models/ggml-base.bin");
    }
    
    private void extractModelIfNeeded(String resourceName, String destPath) {
        File modelFile = new File(destPath);
        if (!modelFile.exists() || modelFile.length() == 0) {
            try {
                InputStream in = getClass().getResourceAsStream("/" + resourceName);
                if (in != null) {
                    Files.copy(in, modelFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                    System.out.println("Extracted model: " + destPath);
                }
            } catch (Exception e) {
                System.err.println("Failed to extract model: " + resourceName);
            }
        }
    }
    
    private void checkWhisperExecutable() {
        File whisperExe = new File("files/whisper.exe");
        if (!whisperExe.exists()) {
            System.out.println("Warning: whisper.exe not found in files folder");
        }
    }
    
    private void setAppIcon() {
        try {
            URL iconURL = getClass().getResource("/app.ico");
            if (iconURL != null) {
                ImageIcon icon = new ImageIcon(iconURL);
                setIconImage(icon.getImage());
            }
        } catch (Exception e) {
            System.err.println("Could not load icon: " + e.getMessage());
        }
    }
    
    private void initJavaFX() {
        jfxPanel = new JFXPanel();
        setLayout(new BorderLayout());
        add(jfxPanel, BorderLayout.CENTER);
        
        Platform.runLater(() -> {
            WebView webView = new WebView();
            webEngine = webView.getEngine();
            
            // Enable JavaScript
            webEngine.getLoadWorker().stateProperty().addListener((obs, oldState, newState) -> {
                if (newState == Worker.State.SUCCEEDED) {
                    JSObject window = (JSObject) webEngine.executeScript("window");
                    window.setMember("javaApp", new JavaBridge());
                    
                    // Remove default cursor
                    webView.setCursor(javafx.scene.Cursor.DEFAULT);
                }
            });
            
            // Load HTML content
            String htmlContent = getHTMLContent();
            webEngine.loadContent(htmlContent);
            
            Scene scene = new Scene(webView);
            jfxPanel.setScene(scene);
        });
    }
    
    private String getHTMLContent() {
        return "<!DOCTYPE html>\n" +
        "<html lang=\"en\">\n" +
        "<head>\n" +
        "    <meta charset=\"UTF-8\">\n" +
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n" +
        "    <title>NotYCaptionGenAi</title>\n" +
        "    <style>\n" +
        "        * {\n" +
        "            margin: 0;\n" +
        "            padding: 0;\n" +
        "            box-sizing: border-box;\n" +
        "            cursor: default;\n" +
        "        }\n" +
        "        \n" +
        "        body {\n" +
        "            font-family: 'Segoe UI', 'System-ui', -apple-system, BlinkMacSystemFont, sans-serif;\n" +
        "            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);\n" +
        "            min-height: 100vh;\n" +
        "            overflow-x: hidden;\n" +
        "            position: relative;\n" +
        "        }\n" +
        "        \n" +
        "        .bg-animation {\n" +
        "            position: fixed;\n" +
        "            top: 0;\n" +
        "            left: 0;\n" +
        "            width: 100%;\n" +
        "            height: 100%;\n" +
        "            z-index: 0;\n" +
        "            overflow: hidden;\n" +
        "        }\n" +
        "        \n" +
        "        .bg-animation::before {\n" +
        "            content: '';\n" +
        "            position: absolute;\n" +
        "            width: 200%;\n" +
        "            height: 200%;\n" +
        "            background: radial-gradient(circle, rgba(0,120,212,0.1) 1px, transparent 1px);\n" +
        "            background-size: 50px 50px;\n" +
        "            animation: moveDots 20s linear infinite;\n" +
        "        }\n" +
        "        \n" +
        "        @keyframes moveDots {\n" +
        "            0% { transform: translate(0, 0); }\n" +
        "            100% { transform: translate(-50px, -50px); }\n" +
        "        }\n" +
        "        \n" +
        "        .gradient-bg {\n" +
        "            position: fixed;\n" +
        "            top: 0;\n" +
        "            left: 0;\n" +
        "            width: 100%;\n" +
        "            height: 100%;\n" +
        "            background: linear-gradient(125deg, \n" +
        "                rgba(0,120,212,0.1) 0%, \n" +
        "                rgba(0,200,120,0.05) 50%, \n" +
        "                rgba(255,100,0,0.1) 100%);\n" +
        "            animation: gradientShift 10s ease infinite;\n" +
        "        }\n" +
        "        \n" +
        "        @keyframes gradientShift {\n" +
        "            0%, 100% { opacity: 0.5; }\n" +
        "            50% { opacity: 1; }\n" +
        "        }\n" +
        "        \n" +
        "        .container {\n" +
        "            position: relative;\n" +
        "            z-index: 1;\n" +
        "            max-width: 1200px;\n" +
        "            margin: 0 auto;\n" +
        "            padding: 20px;\n" +
        "        }\n" +
        "        \n" +
        "        .title-bar {\n" +
        "            background: rgba(20, 20, 30, 0.95);\n" +
        "            backdrop-filter: blur(10px);\n" +
        "            border-radius: 12px;\n" +
        "            padding: 12px 20px;\n" +
        "            margin-bottom: 20px;\n" +
        "            display: flex;\n" +
        "            justify-content: space-between;\n" +
        "            align-items: center;\n" +
        "            box-shadow: 0 4px 20px rgba(0,0,0,0.3);\n" +
        "            border: 1px solid rgba(255,255,255,0.1);\n" +
        "        }\n" +
        "        \n" +
        "        .title-bar h2 {\n" +
        "            color: #fff;\n" +
        "            font-size: 18px;\n" +
        "            font-weight: 500;\n" +
        "        }\n" +
        "        \n" +
        "        .window-controls {\n" +
        "            display: flex;\n" +
        "            gap: 8px;\n" +
        "        }\n" +
        "        \n" +
        "        .win-btn {\n" +
        "            width: 32px;\n" +
        "            height: 32px;\n" +
        "            border: none;\n" +
        "            background: rgba(255,255,255,0.1);\n" +
        "            color: #fff;\n" +
        "            font-size: 16px;\n" +
        "            border-radius: 6px;\n" +
        "            cursor: pointer;\n" +
        "            transition: all 0.2s;\n" +
        "        }\n" +
        "        \n" +
        "        .win-btn:hover {\n" +
        "            background: rgba(255,255,255,0.2);\n" +
        "        }\n" +
        "        \n" +
        "        .win-btn.close:hover {\n" +
        "            background: #e81123;\n" +
        "        }\n" +
        "        \n" +
        "        .card {\n" +
        "            background: rgba(30, 30, 40, 0.9);\n" +
        "            backdrop-filter: blur(10px);\n" +
        "            border-radius: 16px;\n" +
        "            padding: 24px;\n" +
        "            margin-bottom: 20px;\n" +
        "            border: 1px solid rgba(255,255,255,0.1);\n" +
        "            transition: transform 0.3s, box-shadow 0.3s;\n" +
        "        }\n" +
        "        \n" +
        "        .card:hover {\n" +
        "            transform: translateY(-2px);\n" +
        "            box-shadow: 0 8px 30px rgba(0,0,0,0.3);\n" +
        "        }\n" +
        "        \n" +
        "        .logo-section {\n" +
        "            text-align: center;\n" +
        "            margin-bottom: 30px;\n" +
        "        }\n" +
        "        \n" +
        "        .windows-logo {\n" +
        "            display: inline-flex;\n" +
        "            gap: 12px;\n" +
        "            margin-bottom: 20px;\n" +
        "        }\n" +
        "        \n" +
        "        .win-logo-piece {\n" +
        "            width: 50px;\n" +
        "            height: 50px;\n" +
        "            border-radius: 12px;\n" +
        "            animation: pulse 2s ease-in-out infinite;\n" +
        "        }\n" +
        "        \n" +
        "        @keyframes pulse {\n" +
        "            0%, 100% { transform: scale(1); opacity: 0.8; }\n" +
        "            50% { transform: scale(1.05); opacity: 1; }\n" +
        "        }\n" +
        "        \n" +
        "        .logo-blue { background: #0078d4; animation-delay: 0s; }\n" +
        "        .logo-green { background: #107c10; animation-delay: 0.2s; }\n" +
        "        .logo-orange { background: #ff8c00; animation-delay: 0.4s; }\n" +
        "        .logo-red { background: #e81123; animation-delay: 0.6s; }\n" +
        "        \n" +
        "        h1 {\n" +
        "            font-size: 48px;\n" +
        "            background: linear-gradient(135deg, #0078d4, #00b4d8);\n" +
        "            -webkit-background-clip: text;\n" +
        "            -webkit-text-fill-color: transparent;\n" +
        "            background-clip: text;\n" +
        "            margin-bottom: 10px;\n" +
        "        }\n" +
        "        \n" +
        "        .subtitle {\n" +
        "            color: #aaa;\n" +
        "            font-size: 16px;\n" +
        "        }\n" +
        "        \n" +
        "        .btn {\n" +
        "            padding: 12px 28px;\n" +
        "            font-size: 14px;\n" +
        "            font-weight: 600;\n" +
        "            border: none;\n" +
        "            border-radius: 10px;\n" +
        "            cursor: pointer;\n" +
        "            transition: all 0.3s;\n" +
        "            position: relative;\n" +
        "            overflow: hidden;\n" +
        "        }\n" +
        "        \n" +
        "        .btn-primary {\n" +
        "            background: linear-gradient(135deg, #0078d4, #00b4d8);\n" +
        "            color: white;\n" +
        "        }\n" +
        "        \n" +
        "        .btn-success {\n" +
        "            background: linear-gradient(135deg, #107c10, #2ecc71);\n" +
        "            color: white;\n" +
        "        }\n" +
        "        \n" +
        "        .btn-warning {\n" +
        "            background: linear-gradient(135deg, #ff8c00, #ffb347);\n" +
        "            color: white;\n" +
        "        }\n" +
        "        \n" +
        "        .btn-telegram {\n" +
        "            background: linear-gradient(135deg, #0088cc, #2ca5e0);\n" +
        "            color: white;\n" +
        "        }\n" +
        "        \n" +
        "        .btn:hover {\n" +
        "            transform: translateY(-2px);\n" +
        "            box-shadow: 0 5px 20px rgba(0,0,0,0.3);\n" +
        "        }\n" +
        "        \n" +
        "        .btn-glow {\n" +
        "            animation: glowPulse 1.5s ease-in-out infinite;\n" +
        "        }\n" +
        "        \n" +
        "        @keyframes glowPulse {\n" +
        "            0%, 100% { box-shadow: 0 0 5px rgba(0,120,212,0.5); }\n" +
        "            50% { box-shadow: 0 0 20px rgba(0,120,212,0.8); }\n" +
        "        }\n" +
        "        \n" +
        "        .file-input-area {\n" +
        "            border: 2px dashed rgba(255,255,255,0.2);\n" +
        "            border-radius: 12px;\n" +
        "            padding: 20px;\n" +
        "            text-align: center;\n" +
        "            cursor: pointer;\n" +
        "            transition: all 0.3s;\n" +
        "        }\n" +
        "        \n" +
        "        .file-input-area:hover {\n" +
        "            border-color: #0078d4;\n" +
        "            background: rgba(0,120,212,0.1);\n" +
        "        }\n" +
        "        \n" +
        "        .file-info {\n" +
        "            color: #0078d4;\n" +
        "            font-size: 14px;\n" +
        "            margin-top: 10px;\n" +
        "        }\n" +
        "        \n" +
        "        select, input {\n" +
        "            background: rgba(20,20,30,0.9);\n" +
        "            border: 1px solid rgba(255,255,255,0.2);\n" +
        "            border-radius: 8px;\n" +
        "            padding: 10px 15px;\n" +
        "            color: white;\n" +
        "            font-size: 14px;\n" +
        "            width: 100%;\n" +
        "        }\n" +
        "        \n" +
        "        .status {\n" +
        "            background: rgba(0,0,0,0.5);\n" +
        "            border-radius: 10px;\n" +
        "            padding: 12px;\n" +
        "            text-align: center;\n" +
        "            font-size: 13px;\n" +
        "            color: #2ecc71;\n" +
        "        }\n" +
        "        \n" +
        "        .status-error { color: #e81123; }\n" +
        "        .status-warning { color: #ff8c00; }\n" +
        "        \n" +
        "        .slider-container {\n" +
        "            display: flex;\n" +
        "            align-items: center;\n" +
        "            gap: 15px;\n" +
        "        }\n" +
        "        \n" +
        "        input[type=\"range\"] {\n" +
        "            flex: 1;\n" +
        "            height: 4px;\n" +
        "            -webkit-appearance: none;\n" +
        "            background: rgba(255,255,255,0.2);\n" +
        "            border-radius: 2px;\n" +
        "        }\n" +
        "        \n" +
        "        input[type=\"range\"]::-webkit-slider-thumb {\n" +
        "            -webkit-appearance: none;\n" +
        "            width: 16px;\n" +
        "            height: 16px;\n" +
        "            border-radius: 50%;\n" +
        "            background: #0078d4;\n" +
        "            cursor: pointer;\n" +
        "        }\n" +
        "        \n" +
        "        .letter-value {\n" +
        "            color: #0078d4;\n" +
        "            font-weight: bold;\n" +
        "            min-width: 40px;\n" +
        "        }\n" +
        "        \n" +
        "        .grid-2 {\n" +
        "            display: grid;\n" +
        "            grid-template-columns: 1fr 1fr;\n" +
        "            gap: 20px;\n" +
        "        }\n" +
        "        \n" +
        "        .model-status {\n" +
        "            color: #2ecc71;\n" +
        "            font-size: 12px;\n" +
        "            margin-top: 8px;\n" +
        "        }\n" +
        "        \n" +
        "        footer {\n" +
        "            text-align: center;\n" +
        "            padding: 20px;\n" +
        "            color: #666;\n" +
        "            font-size: 12px;\n" +
        "        }\n" +
        "        \n" +
        "        @media (max-width: 768px) {\n" +
        "            .grid-2 { grid-template-columns: 1fr; }\n" +
        "            h1 { font-size: 32px; }\n" +
        "        }\n" +
        "    </style>\n" +
        "</head>\n" +
        "<body>\n" +
        "    <div class=\"bg-animation\"></div>\n" +
        "    <div class=\"gradient-bg\"></div>\n" +
        "    \n" +
        "    <div class=\"container\">\n" +
        "        <div class=\"title-bar\">\n" +
        "            <h2>NotYCaptionGenAi v3.0</h2>\n" +
        "            <div class=\"window-controls\">\n" +
        "                <button class=\"win-btn\" onclick=\"javaApp.minimize()\">─</button>\n" +
        "                <button class=\"win-btn\" onclick=\"javaApp.maximize()\">□</button>\n" +
        "                <button class=\"win-btn close\" onclick=\"javaApp.close()\">✕</button>\n" +
        "            </div>\n" +
        "        </div>\n" +
        "        \n" +
        "        <div class=\"logo-section\">\n" +
        "            <div class=\"windows-logo\">\n" +
        "                <div class=\"win-logo-piece logo-blue\"></div>\n" +
        "                <div class=\"win-logo-piece logo-green\"></div>\n" +
        "                <div class=\"win-logo-piece logo-orange\"></div>\n" +
        "                <div class=\"win-logo-piece logo-red\"></div>\n" +
        "            </div>\n" +
        "            <h1>NotYCaptionGenAi</h1>\n" +
        "            <div class=\"subtitle\">AI-Powered Subtitle Generator for Windows</div>\n" +
        "        </div>\n" +
        "        \n" +
        "        <div class=\"card\">\n" +
        "            <div class=\"file-input-area\" onclick=\"javaApp.selectFile()\">\n" +
        "                📁 Click to Select Video/Audio File\n" +
        "                <div id=\"fileInfo\" class=\"file-info\">No file selected</div>\n" +
        "            </div>\n" +
        "        </div>\n" +
        "        \n" +
        "        <div class=\"grid-2\">\n" +
        "            <div class=\"card\">\n" +
        "                <h3>🤖 Whisper Model</h3>\n" +
        "                <select id=\"modelSelect\" style=\"margin-top: 10px;\">\n" +
        "                    <option value=\"0\">Tiny (39 MB) - Built-in</option>\n" +
        "                    <option value=\"1\">Base (142 MB) - Built-in</option>\n" +
        "                    <option value=\"2\">Small (466 MB) - Download</option>\n" +
        "                    <option value=\"3\">Medium (1.5 GB) - Download</option>\n" +
        "                    <option value=\"4\">Large V1 (2.9 GB) - Download</option>\n" +
        "                </select>\n" +
        "                <div id=\"modelStatus\" class=\"model-status\">✅ Ready to use</div>\n" +
        "                <button id=\"downloadBtn\" class=\"btn btn-warning\" style=\"margin-top: 15px; width: 100%;\" onclick=\"javaApp.downloadModel()\">\n" +
        "                    📥 Download Selected Model\n" +
        "                </button>\n" +
        "            </div>\n" +
        "            \n" +
        "            <div class=\"card\">\n" +
        "                <h3>⚙️ Settings</h3>\n" +
        "                <div style=\"margin-top: 15px;\">\n" +
        "                    <label>Max Letters per Line:</label>\n" +
        "                    <div class=\"slider-container\">\n" +
        "                        <input type=\"range\" id=\"letterSpacing\" min=\"20\" max=\"80\" value=\"42\">\n" +
        "                        <span id=\"letterValue\" class=\"letter-value\">42</span>\n" +
        "                    </div>\n" +
        "                </div>\n" +
        "                <div style=\"margin-top: 15px;\">\n" +
        "                    <label>Language:</label>\n" +
        "                    <select id=\"languageSelect\" style=\"margin-top: 5px;\">\n" +
        "                        <option value=\"auto\">Auto Detect</option>\n" +
        "                        <option value=\"en\">English</option>\n" +
        "                        <option value=\"hi\">Hindi</option>\n" +
        "                        <option value=\"ja\">Japanese</option>\n" +
        "                        <option value=\"es\">Spanish</option>\n" +
        "                        <option value=\"fr\">French</option>\n" +
        "                        <option value=\"de\">German</option>\n" +
        "                        <option value=\"zh\">Chinese</option>\n" +
        "                        <option value=\"ar\">Arabic</option>\n" +
        "                        <option value=\"ru\">Russian</option>\n" +
        "                        <option value=\"ko\">Korean</option>\n" +
        "                    </select>\n" +
        "                </div>\n" +
        "                <div style=\"margin-top: 15px;\">\n" +
        "                    <label>\n" +
        "                        <input type=\"checkbox\" id=\"transliterate\"> \n" +
        "                        🔄 Transliterate to English\n" +
        "                    </label>\n" +
        "                </div>\n" +
        "                <button id=\"generateBtn\" class=\"btn btn-success btn-glow\" style=\"margin-top: 20px; width: 100%;\" onclick=\"javaApp.generate()\">\n" +
        "                    🚀 Generate Subtitles\n" +
        "                </button>\n" +
        "            </div>\n" +
        "        </div>\n" +
        "        \n" +
        "        <div class=\"card\">\n" +
        "            <div id=\"status\" class=\"status\">✅ Ready. Select a file and model to begin.</div>\n" +
        "        </div>\n" +
        "        \n" +
        "        <div class=\"grid-2\">\n" +
        "            <button class=\"btn btn-telegram\" onclick=\"javaApp.openTelegram()\">\n" +
        "                💬 Join Telegram Channel @Noty_215\n" +
        "            </button>\n" +
        "            <div style=\"text-align: right; color: #666; font-size: 12px; padding: 12px;\">\n" +
        "                Developed with ❤️ by NotY215\n" +
        "            </div>\n" +
        "        </div>\n" +
        "        \n" +
        "        <footer>\n" +
        "            LGPL v3 License | Tiny & Base Models Built-in | Windows 11 Optimized\n" +
        "        </footer>\n" +
        "    </div>\n" +
        "    \n" +
        "    <script>\n" +
        "        const slider = document.getElementById('letterSpacing');\n" +
        "        const letterValue = document.getElementById('letterValue');\n" +
        "        slider.addEventListener('input', () => {\n" +
        "            letterValue.textContent = slider.value;\n" +
        "        });\n" +
        "        \n" +
        "        const modelSelect = document.getElementById('modelSelect');\n" +
        "        const modelStatus = document.getElementById('modelStatus');\n" +
        "        const downloadBtn = document.getElementById('downloadBtn');\n" +
        "        \n" +
        "        function updateModelUI(index) {\n" +
        "            if (index === '0' || index === '1') {\n" +
        "                modelStatus.innerHTML = '✅ Built-in model - Ready to use';\n" +
        "                modelStatus.style.color = '#2ecc71';\n" +
        "                downloadBtn.innerHTML = '✓ Model Available (Built-in)';\n" +
        "                downloadBtn.disabled = true;\n" +
        "                downloadBtn.style.opacity = '0.5';\n" +
        "            } else {\n" +
        "                modelStatus.innerHTML = '⚠️ Not downloaded';\n" +
        "                modelStatus.style.color = '#ff8c00';\n" +
        "                downloadBtn.innerHTML = '📥 Download Selected Model';\n" +
        "                downloadBtn.disabled = false;\n" +
        "                downloadBtn.style.opacity = '1';\n" +
        "            }\n" +
        "        }\n" +
        "        \n" +
        "        modelSelect.addEventListener('change', (e) => {\n" +
        "            updateModelUI(e.target.value);\n" +
        "        });\n" +
        "        \n" +
        "        updateModelUI(modelSelect.value);\n" +
        "        \n" +
        "        window.updateFileInfo = function(filename) {\n" +
        "            document.getElementById('fileInfo').innerHTML = filename;\n" +
        "        };\n" +
        "        \n" +
        "        window.updateStatus = function(message, isError, isWarning) {\n" +
        "            const statusDiv = document.getElementById('status');\n" +
        "            statusDiv.innerHTML = message;\n" +
        "            statusDiv.className = 'status';\n" +
        "            if (isError) statusDiv.classList.add('status-error');\n" +
        "            if (isWarning) statusDiv.classList.add('status-warning');\n" +
        "        };\n" +
        "        \n" +
        "        window.updateModelAvailable = function(available) {\n" +
        "            const generateBtn = document.getElementById('generateBtn');\n" +
        "            if (available) {\n" +
        "                generateBtn.disabled = false;\n" +
        "                generateBtn.style.opacity = '1';\n" +
        "            } else {\n" +
        "                generateBtn.disabled = true;\n" +
        "                generateBtn.style.opacity = '0.5';\n" +
        "            }\n" +
        "        };\n" +
        "    </script>\n" +
        "</body>\n" +
        "</html>";
    }
    
    // Helper method to execute JavaScript and get value synchronously
    private String executeScriptSync(String script) {
        CountDownLatch latch = new CountDownLatch(1);
        String[] result = new String[1];
        
        Platform.runLater(() -> {
            try {
                result[0] = (String) webEngine.executeScript(script);
            } catch (Exception e) {
                result[0] = "";
            } finally {
                latch.countDown();
            }
        });
        
        try {
            latch.await();
        } catch (InterruptedException e) {
            return "";
        }
        return result[0];
    }
    
    private boolean executeScriptSyncBoolean(String script) {
        CountDownLatch latch = new CountDownLatch(1);
        boolean[] result = new boolean[1];
        
        Platform.runLater(() -> {
            try {
                result[0] = (Boolean) webEngine.executeScript(script);
            } catch (Exception e) {
                result[0] = false;
            } finally {
                latch.countDown();
            }
        });
        
        try {
            latch.await();
        } catch (InterruptedException e) {
            return false;
        }
        return result[0];
    }
    
    // Java Bridge for JavaScript communication
    public class JavaBridge {
        
        public void minimize() {
            setState(JFrame.ICONIFIED);
        }
        
        public void maximize() {
            setExtendedState(getExtendedState() == JFrame.MAXIMIZED_BOTH ? JFrame.NORMAL : JFrame.MAXIMIZED_BOTH);
        }
        
        public void close() {
            int confirm = JOptionPane.showConfirmDialog(GUI.this, "Are you sure you want to exit?", "Exit", JOptionPane.YES_NO_OPTION);
            if (confirm == JOptionPane.YES_OPTION) {
                System.exit(0);
            }
        }
        
        public void selectFile() {
            JFileChooser fileChooser = new JFileChooser();
            fileChooser.setDialogTitle("Select Video or Audio File");
            String[] extensions = {"wav", "mp4", "mp3", "m4a", "mkv", "avi", "wmv", "mpeg", "flac"};
            fileChooser.setFileFilter(new javax.swing.filechooser.FileNameExtensionFilter(
                "Media Files", extensions));
            
            int result = fileChooser.showOpenDialog(GUI.this);
            if (result == JFileChooser.APPROVE_OPTION) {
                selectedFile = fileChooser.getSelectedFile();
                Platform.runLater(() -> {
                    webEngine.executeScript("updateFileInfo('" + selectedFile.getName() + " (" + 
                        (selectedFile.length() / 1024 / 1024) + " MB)')");
                });
                checkModelAvailability();
            }
        }
        
        public void downloadModel() {
            int index = Integer.parseInt(executeScriptSync("document.getElementById('modelSelect').value"));
            
            ModelInfo model = MODELS[index];
            long sizeMB = model.sizeBytes / (1024 * 1024);
            
            int response = JOptionPane.showConfirmDialog(GUI.this,
                String.format("Download %s (%d MB)?", model.name, sizeMB),
                "Confirm Download", JOptionPane.YES_NO_OPTION);
            
            if (response == JOptionPane.YES_OPTION) {
                downloadDialog = new DownloadProgressDialog(GUI.this, model.name, model.sizeBytes);
                downloadDialog.setVisible(true);
                
                modelDownloader = new ModelDownloader();
                modelDownloader.downloadModel(model.url, model.fileName, model.sizeBytes, new ModelDownloader.DownloadCallback() {
                    @Override
                    public void onProgress(int percent, long downloaded, long total, double speed) {
                        Platform.runLater(() -> {
                            if (downloadDialog != null) {
                                downloadDialog.updateProgress(percent, downloaded, total, speed);
                            }
                        });
                    }
                    
                    @Override
                    public void onComplete(boolean success) {
                        Platform.runLater(() -> {
                            if (downloadDialog != null) downloadDialog.dispose();
                            if (success) {
                                checkModelAvailability();
                                Platform.runLater(() -> {
                                    webEngine.executeScript("updateStatus('✅ Model downloaded successfully!', false, false)");
                                });
                            } else {
                                Platform.runLater(() -> {
                                    webEngine.executeScript("updateStatus('❌ Download failed!', true, false)");
                                });
                            }
                        });
                    }
                    
                    @Override
                    public void onCancel() {
                        Platform.runLater(() -> {
                            if (downloadDialog != null) downloadDialog.dispose();
                            webEngine.executeScript("updateStatus('❌ Download cancelled', true, false)");
                        });
                    }
                });
            }
        }
        
        public void generate() {
            if (selectedFile == null) {
                Platform.runLater(() -> {
                    webEngine.executeScript("updateStatus('❌ Please select a file first!', true, false)");
                });
                return;
            }
            
            int modelIndex = Integer.parseInt(executeScriptSync("document.getElementById('modelSelect').value"));
            String language = executeScriptSync("document.getElementById('languageSelect').value");
            int letterSpacing = Integer.parseInt(executeScriptSync("document.getElementById('letterSpacing').value"));
            boolean transliterate = executeScriptSyncBoolean("document.getElementById('transliterate').checked");
            
            Platform.runLater(() -> {
                webEngine.executeScript("updateStatus('⏳ Processing... Extracting audio...', false, false)");
            });
            
            new Thread(() -> {
                try {
                    String modelPath = MODELS[modelIndex].fileName;
                    File modelFile = new File(modelPath);
                    if (!modelFile.exists()) {
                        Platform.runLater(() -> {
                            webEngine.executeScript("updateStatus('❌ Model not found! Please download it first.', true, false)");
                        });
                        return;
                    }
                    
                    File audioFile = AudioExtractor.extractAudio(selectedFile);
                    
                    Platform.runLater(() -> {
                        webEngine.executeScript("updateStatus('🎤 Transcribing with Whisper AI...', false, false)");
                    });
                    
                    String transcription = WhisperTranscriber.transcribe(audioFile, language, modelPath);
                    
                    Platform.runLater(() -> {
                        webEngine.executeScript("updateStatus('📝 Generating SRT subtitles...', false, false)");
                    });
                    
                    String srtContent = SRTGenerator.generateSRT(transcription, letterSpacing);
                    
                    String outputPath = selectedFile.getParent() + File.separator + 
                                       getFileNameWithoutExtension(selectedFile) + ".srt";
                    Files.write(Paths.get(outputPath), srtContent.getBytes());
                    
                    if (transliterate) {
                        String transliterated = Transliterator.transliterate(srtContent);
                        String translitPath = selectedFile.getParent() + File.separator + 
                                             getFileNameWithoutExtension(selectedFile) + "_translit.srt";
                        Files.write(Paths.get(translitPath), transliterated.getBytes());
                    }
                    
                    if (!selectedFile.getName().toLowerCase().endsWith(".wav")) {
                        audioFile.delete();
                    }
                    
                    Platform.runLater(() -> {
                        webEngine.executeScript("updateStatus('🎉 Subtitle generation completed successfully!', false, false)");
                        JOptionPane.showMessageDialog(GUI.this, 
                            "Subtitles generated successfully!\n\nSaved to:\n" + outputPath,
                            "Success", JOptionPane.INFORMATION_MESSAGE);
                    });
                    
                } catch (Exception e) {
                    e.printStackTrace();
                    String errorMsg = e.getMessage().replace("'", "\\'");
                    Platform.runLater(() -> {
                        webEngine.executeScript("updateStatus('❌ Error: " + errorMsg + "', true, false)");
                    });
                }
            }).start();
        }
        
        public void openTelegram() {
            try {
                Desktop.getDesktop().browse(new URI("https://t.me/Noty_215"));
            } catch (Exception e) {
                JOptionPane.showMessageDialog(GUI.this, 
                    "Visit: https://t.me/Noty_215", "Telegram Channel", JOptionPane.INFORMATION_MESSAGE);
            }
        }
        
        private void checkModelAvailability() {
            int index = Integer.parseInt(executeScriptSync("document.getElementById('modelSelect').value"));
            File modelFile = new File(MODELS[index].fileName);
            boolean available = modelFile.exists() && modelFile.length() > 0;
            
            Platform.runLater(() -> {
                webEngine.executeScript("updateModelAvailable(" + available + ")");
                if (available) {
                    webEngine.executeScript("updateStatus('✅ Model available. Ready to generate.', false, false)");
                }
            });
        }
        
        private String getFileNameWithoutExtension(File file) {
            String name = file.getName();
            int lastDot = name.lastIndexOf('.');
            return lastDot > 0 ? name.substring(0, lastDot) : name;
        }
    }
}