package com.noty.captiongen;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

public class PythonEmbeddedTranscriber {

    private static String pythonPath = null;
    private static boolean initialized = false;

    public static synchronized String transcribe(File audioFile, String language, String modelPath) throws Exception {
        System.out.println("=== Python Embedded Whisper Transcription Started ===");
        System.out.println("Audio file: " + audioFile.getAbsolutePath());
        System.out.println("Language: " + language);

        // Initialize embedded Python
        if (!initialized) {
            initializeEmbeddedPython();
        }

        // Extract audio to WAV if needed
        File wavFile = audioFile;
        if (!audioFile.getName().toLowerCase().endsWith(".wav")) {
            System.out.println("Converting to WAV format...");
            wavFile = AudioExtractor.extractAudio(audioFile);
        }

        String languageCode = getLanguageCode(language);
        String outputPath = wavFile.getParent() + File.separator +
                getFileNameWithoutExtension(wavFile);

        // Create Python script for transcription
        File tempScript = createPythonScript(wavFile, languageCode, outputPath);

        try {
            // Execute Python script with embedded Python
            ProcessBuilder pb = new ProcessBuilder(
                    pythonPath,
                    tempScript.getAbsolutePath()
            );

            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Read output with timeout
            StringBuilder output = new StringBuilder();
            boolean completed = process.waitFor(300, TimeUnit.SECONDS);

            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                    System.out.println(line);
                }
            }

            if (!completed) {
                process.destroyForcibly();
                throw new Exception("Transcription timed out after 5 minutes");
            }

            int exitCode = process.exitValue();
            System.out.println("Python process exit code: " + exitCode);

            if (exitCode != 0) {
                throw new Exception("Python script failed:\n" + output.toString());
            }

            // Read the generated SRT file
            String srtPath = outputPath + ".srt";
            File srtFile = new File(srtPath);

            if (srtFile.exists() && srtFile.length() > 0) {
                String content = new String(Files.readAllBytes(srtFile.toPath()));
                System.out.println("Success! Generated " + content.length() + " characters of subtitles");
                return content;
            }

            throw new Exception("No SRT file generated");

        } finally {
            // Clean up temp script
            tempScript.delete();
        }
    }

    private static File createPythonScript(File audioFile, String languageCode, String outputPath) throws IOException {
        File tempScript = File.createTempFile("whisper_transcribe", ".py");
        tempScript.deleteOnExit();

        String script =
                "# -*- coding: utf-8 -*-\n" +
                        "import sys\n" +
                        "import os\n" +
                        "import json\n\n" +
                        "# Add embedded packages to path\n" +
                        "sys.path.insert(0, os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages'))\n" +
                        "sys.path.insert(0, os.path.join(os.path.dirname(sys.executable), 'Lib'))\n\n" +
                        "def format_time(seconds):\n" +
                        "    hours = int(seconds // 3600)\n" +
                        "    minutes = int((seconds % 3600) // 60)\n" +
                        "    secs = int(seconds % 60)\n" +
                        "    millis = int((seconds % 1) * 1000)\n" +
                        "    return f'{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}'\n\n" +
                        "try:\n" +
                        "    import whisper\n" +
                        "    print('Loading Whisper model...')\n" +
                        "    model = whisper.load_model('base')\n" +
                        "    print('Transcribing audio...')\n" +
                        "    result = model.transcribe('" + audioFile.getAbsolutePath().replace("\\", "/") + "', language='" + languageCode + "')\n" +
                        "    print('Writing subtitles...')\n" +
                        "    with open('" + outputPath.replace("\\", "/") + ".srt', 'w', encoding='utf-8') as f:\n" +
                        "        for i, segment in enumerate(result['segments']):\n" +
                        "            start = segment['start']\n" +
                        "            end = segment['end']\n" +
                        "            text = segment['text'].strip()\n" +
                        "            f.write(f'{i+1}\\n')\n" +
                        "            f.write(f'{format_time(start)} --> {format_time(end)}\\n')\n" +
                        "            f.write(f'{text}\\n\\n')\n" +
                        "    print('SUCCESS')\n" +
                        "    sys.exit(0)\n" +
                        "except ImportError as e:\n" +
                        "    print(f'ImportError: {e}', file=sys.stderr)\n" +
                        "    print('Whisper package not found. Please ensure it is installed.', file=sys.stderr)\n" +
                        "    sys.exit(1)\n" +
                        "except Exception as e:\n" +
                        "    print(f'Error: {e}', file=sys.stderr)\n" +
                        "    import traceback\n" +
                        "    traceback.print_exc()\n" +
                        "    sys.exit(1)\n";

        Files.write(tempScript.toPath(), script.getBytes(StandardCharsets.UTF_8));
        return tempScript;
    }

    private static void initializeEmbeddedPython() throws Exception {
        System.out.println("Initializing embedded Python...");

        // Find embedded Python executable
        File pythonExe = findPythonExecutable();
        if (pythonExe == null || !pythonExe.exists()) {
            throw new Exception("Embedded Python not found. Please ensure Python is included in the application.");
        }

        pythonPath = pythonExe.getAbsolutePath();
        System.out.println("Using Python: " + pythonPath);

        // Check if whisper is installed
        if (!isWhisperInstalled()) {
            System.out.println("Installing Whisper package...");
            installWhisperPackage();
        }

        initialized = true;
        System.out.println("Python initialized successfully");
    }

    private static File findPythonExecutable() {
        // Check for embedded Python
        String[] possiblePaths = {
                "python/python.exe",
                "python/python3.exe",
                "./python/python.exe",
                "./python/python3.exe",
                "python39/python.exe",
                "./python39/python.exe"
        };

        for (String path : possiblePaths) {
            File file = new File(path);
            if (file.exists()) {
                System.out.println("Found Python at: " + file.getAbsolutePath());
                return file;
            }
        }

        // Also check current directory
        File currentDir = new File(".");
        File[] files = currentDir.listFiles();
        if (files != null) {
            for (File file : files) {
                if (file.isDirectory() && file.getName().toLowerCase().contains("python")) {
                    File pythonExe = new File(file, "python.exe");
                    if (pythonExe.exists()) {
                        return pythonExe;
                    }
                    pythonExe = new File(file, "python3.exe");
                    if (pythonExe.exists()) {
                        return pythonExe;
                    }
                }
            }
        }

        System.out.println("Python not found in embedded locations");
        return null;
    }

    private static boolean isWhisperInstalled() {
        try {
            // Create a test script
            File testScript = File.createTempFile("test_whisper", ".py");
            testScript.deleteOnExit();

            String script =
                    "import sys\n" +
                            "try:\n" +
                            "    import whisper\n" +
                            "    print('OK')\n" +
                            "    sys.exit(0)\n" +
                            "except ImportError:\n" +
                            "    print('NOT FOUND')\n" +
                            "    sys.exit(1)\n";

            Files.write(testScript.toPath(), script.getBytes(StandardCharsets.UTF_8));

            ProcessBuilder pb = new ProcessBuilder(pythonPath, testScript.getAbsolutePath());
            pb.redirectErrorStream(true);
            Process process = pb.start();

            StringBuilder output = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line);
                }
            }

            int exitCode = process.waitFor();
            return exitCode == 0 && output.toString().contains("OK");

        } catch (Exception e) {
            System.err.println("Whisper check failed: " + e.getMessage());
            return false;
        }
    }

    private static void installWhisperPackage() {
        try {
            // Create install script
            File installScript = File.createTempFile("install_whisper", ".py");
            installScript.deleteOnExit();

            String script =
                    "import subprocess\n" +
                            "import sys\n" +
                            "import os\n\n" +
                            "def install_package(package):\n" +
                            "    try:\n" +
                            "        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet', '--no-cache-dir'])\n" +
                            "        print(f'Installed: {package}')\n" +
                            "        return True\n" +
                            "    except Exception as e:\n" +
                            "        print(f'Failed to install {package}: {e}')\n" +
                            "        return False\n\n" +
                            "print('Installing required packages...')\n" +
                            "packages = ['openai-whisper', 'ffmpeg-python', 'numpy', 'torch']\n" +
                            "for pkg in packages:\n" +
                            "    install_package(pkg)\n" +
                            "print('Installation complete')\n";

            Files.write(installScript.toPath(), script.getBytes(StandardCharsets.UTF_8));

            ProcessBuilder pb = new ProcessBuilder(pythonPath, installScript.getAbsolutePath());
            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Read output
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }

            int exitCode = process.waitFor(120, TimeUnit.SECONDS);
            if (exitCode == 0) {
                System.out.println("Whisper package installed successfully");
            } else {
                System.err.println("Failed to install Whisper package");
            }

        } catch (Exception e) {
            System.err.println("Package installation failed: " + e.getMessage());
        }
    }

    private static String getLanguageCode(String language) {
        Map<String, String> languageMap = new HashMap<>();
        languageMap.put("English", "en");
        languageMap.put("Hindi", "hi");
        languageMap.put("Japanese", "ja");
        languageMap.put("Spanish", "es");
        languageMap.put("French", "fr");
        languageMap.put("German", "de");
        languageMap.put("Chinese", "zh");
        languageMap.put("Arabic", "ar");
        languageMap.put("Russian", "ru");
        languageMap.put("Korean", "ko");

        return languageMap.getOrDefault(language, "en");
    }

    private static String getFileNameWithoutExtension(File file) {
        String name = file.getName();
        int lastDot = name.lastIndexOf('.');
        return lastDot > 0 ? name.substring(0, lastDot) : name;
    }
}