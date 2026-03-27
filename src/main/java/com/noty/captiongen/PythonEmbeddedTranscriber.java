package com.noty.captiongen;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

public class PythonEmbeddedTranscriber {

    private static String pythonPath = null;
    private static boolean initialized = false;

    public static synchronized String transcribe(File audioFile, String language, String modelPath) throws Exception {
        LoggingUtil.info("=== Python Embedded Whisper Transcription Started ===");

        if (!initialized) {
            initializeEmbeddedPython();
        }

        String languageCode = getLanguageCode(language);
        String outputBase = audioFile.getParent() + File.separator + getFileNameWithoutExtension(audioFile);
        File tempScript = createPythonScript(audioFile, languageCode, outputBase);

        try {
            ProcessBuilder pb = new ProcessBuilder(pythonPath, tempScript.getAbsolutePath());
            pb.redirectErrorStream(true);
            pb.environment().put("PYTHONHOME", new File("python").getAbsolutePath());
            pb.environment().put("PYTHONPATH", new File("python/Lib").getAbsolutePath() +
                    File.pathSeparator + new File("python/Lib/site-packages").getAbsolutePath());

            LoggingUtil.info("Starting Python transcription process...");
            Process process = pb.start();
            StringBuilder output = new StringBuilder();

            // Create a thread to read output in real-time
            Thread outputReader = new Thread(() -> {
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        output.append(line).append("\n");
                        if (line.contains("Loading") || line.contains("Transcribing") ||
                                line.contains("Writing") || line.contains("Progress")) {
                            LoggingUtil.info("  " + line);
                        }
                    }
                } catch (IOException e) {
                    // Ignore
                }
            });
            outputReader.start();

            boolean completed = process.waitFor(600, TimeUnit.SECONDS);
            outputReader.join();

            if (!completed) {
                process.destroyForcibly();
                throw new Exception("Transcription timed out after 10 minutes");
            }

            int exitCode = process.exitValue();
            LoggingUtil.info("Python process exit code: " + exitCode);

            if (exitCode != 0) {
                throw new Exception("Python failed with exit code " + exitCode + "\nOutput: " + output);
            }

            File srtFile = new File(outputBase + ".srt");
            if (srtFile.exists() && srtFile.length() > 0) {
                String content = new String(Files.readAllBytes(srtFile.toPath()), StandardCharsets.UTF_8);
                LoggingUtil.info("Success! Generated " + content.length() + " characters of subtitles");
                return content;
            }
            throw new Exception("No SRT file generated");
        } finally {
            tempScript.delete();
        }
    }

    private static void initializeEmbeddedPython() throws Exception {
        LoggingUtil.info("========================================");
        LoggingUtil.info("Initializing Embedded Python...");
        LoggingUtil.info("========================================");

        File pythonDir = new File("python");
        if (!pythonDir.exists()) {
            pythonDir.mkdirs();
        }

        File pythonExe = new File(pythonDir, "python.exe");
        if (!pythonExe.exists() || pythonExe.length() < 100000) {
            LoggingUtil.info("Extracting Python from JAR...");
            extractPythonFromJar(pythonDir);
        }

        pythonExe = new File(pythonDir, "python.exe");
        if (!pythonExe.exists() || pythonExe.length() < 100000) {
            throw new Exception("Failed to extract Python. python.exe not found.");
        }

        pythonPath = pythonExe.getAbsolutePath();
        LoggingUtil.info("✓ Python found at: " + pythonPath);

        // Create necessary directories
        new File(pythonDir, "Lib").mkdirs();
        new File(pythonDir, "Lib/site-packages").mkdirs();
        new File(pythonDir, "Scripts").mkdirs();

        // Update python._pth file
        updatePythonPthFile(pythonDir);

        // Install Whisper packages
        PythonInstaller.ensureWhisperInstalled();

        initialized = true;
        LoggingUtil.info("========================================");
        LoggingUtil.info("Python initialized successfully!");
        LoggingUtil.info("========================================");
    }

    private static void extractPythonFromJar(File targetDir) {
        int count = 0;

        try {
            String jarPath = PythonEmbeddedTranscriber.class.getProtectionDomain()
                    .getCodeSource().getLocation().toURI().getPath();

            if (jarPath.contains("%20")) jarPath = jarPath.replace("%20", " ");
            if (jarPath.startsWith("file:")) jarPath = jarPath.substring(5);

            File jarFile = new File(jarPath);
            if (jarFile.exists() && jarFile.getName().endsWith(".jar")) {
                LoggingUtil.info("Extracting from JAR: " + jarPath);

                try (JarFile jar = new JarFile(jarFile)) {
                    Enumeration<JarEntry> entries = jar.entries();

                    while (entries.hasMoreElements()) {
                        JarEntry entry = entries.nextElement();
                        String name = entry.getName();

                        if (name.startsWith("Python/") && !entry.isDirectory()) {
                            String fileName = name.substring("Python/".length());
                            File outFile = new File(targetDir, fileName);

                            if (!outFile.exists()) {
                                outFile.getParentFile().mkdirs();
                                try (InputStream in = jar.getInputStream(entry);
                                     FileOutputStream out = new FileOutputStream(outFile)) {
                                    byte[] buffer = new byte[8192];
                                    int len;
                                    while ((len = in.read(buffer)) > 0) {
                                        out.write(buffer, 0, len);
                                    }
                                }
                                count++;
                                if (count % 10 == 0) LoggingUtil.info("  Extracted " + count + " files...");
                            }
                        }
                    }
                }
                LoggingUtil.info("✓ Extracted " + count + " Python files from JAR");
            }
        } catch (Exception e) {
            LoggingUtil.error("JAR extraction error: " + e.getMessage());
        }
    }

    private static void updatePythonPthFile(File pythonDir) throws IOException {
        File pthFile = new File(pythonDir, "python311._pth");
        List<String> lines = new ArrayList<>();
        lines.add("python311.zip");
        lines.add(".");
        lines.add("Lib");
        lines.add("Lib/site-packages");
        lines.add("import site");
        Files.write(pthFile.toPath(), lines);

        File altPthFile = new File(pythonDir, "python._pth");
        Files.write(altPthFile.toPath(), lines);
        LoggingUtil.info("✓ Updated python._pth file");
    }

    private static File createPythonScript(File audioFile, String languageCode, String outputBase) throws IOException {
        File script = File.createTempFile("whisper", ".py");
        script.deleteOnExit();

        String audioPath = audioFile.getAbsolutePath().replace("\\", "/");
        String outPath = outputBase.replace("\\", "/");

        String content =
                "import whisper\n" +
                        "import sys\n" +
                        "import os\n\n" +
                        "def format_time(s):\n" +
                        "    h = int(s // 3600)\n" +
                        "    m = int((s % 3600) // 60)\n" +
                        "    sec = int(s % 60)\n" +
                        "    ms = int((s % 1) * 1000)\n" +
                        "    return f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'\n\n" +
                        "try:\n" +
                        "    print('Loading Whisper model...')\n" +
                        "    model = whisper.load_model('base')\n" +
                        "    print('Transcribing audio...')\n" +
                        "    result = model.transcribe(r'" + audioPath + "', language='" + languageCode + "', fp16=False)\n" +
                        "    print('Writing subtitles...')\n" +
                        "    with open(r'" + outPath + ".srt', 'w', encoding='utf-8') as f:\n" +
                        "        for i, seg in enumerate(result['segments']):\n" +
                        "            f.write(f'{i+1}\\n')\n" +
                        "            f.write(f'{format_time(seg[\"start\"])} --> {format_time(seg[\"end\"])}\\n')\n" +
                        "            f.write(f'{seg[\"text\"].strip()}\\n\\n')\n" +
                        "    print('SUCCESS')\n" +
                        "    sys.exit(0)\n" +
                        "except Exception as e:\n" +
                        "    print(f'Error: {e}', file=sys.stderr)\n" +
                        "    sys.exit(1)\n";

        Files.write(script.toPath(), content.getBytes(StandardCharsets.UTF_8));
        return script;
    }

    private static String getLanguageCode(String language) {
        Map<String, String> map = new HashMap<>();
        map.put("English", "en");
        map.put("Hindi", "hi");
        map.put("Japanese", "ja");
        map.put("Spanish", "es");
        map.put("French", "fr");
        map.put("German", "de");
        map.put("Chinese", "zh");
        map.put("Arabic", "ar");
        map.put("Russian", "ru");
        map.put("Korean", "ko");
        return map.getOrDefault(language, "en");
    }

    private static String getFileNameWithoutExtension(File file) {
        String name = file.getName();
        int dot = name.lastIndexOf('.');
        return dot > 0 ? name.substring(0, dot) : name;
    }
}