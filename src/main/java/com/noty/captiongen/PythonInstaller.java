package com.noty.captiongen;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

public class PythonInstaller {

    private static boolean whisperInstalled = false;

    public static synchronized void ensureWhisperInstalled() {
        if (whisperInstalled) return;

        LoggingUtil.info("========================================");
        LoggingUtil.info("Checking Python Whisper installation...");
        LoggingUtil.info("========================================");

        File pythonDir = new File("python");
        File pythonExe = new File(pythonDir, "python.exe");

        if (!pythonExe.exists()) {
            LoggingUtil.error("Python not found! Please ensure Python is extracted.");
            return;
        }

        if (isWhisperInstalled(pythonExe)) {
            LoggingUtil.info("✓ Whisper is already installed");
            whisperInstalled = true;
            return;
        }

        installWhisper(pythonExe);
        whisperInstalled = true;
    }

    private static boolean isWhisperInstalled(File pythonExe) {
        try {
            LoggingUtil.info("Checking if Whisper is installed...");

            File testScript = File.createTempFile("check_whisper", ".py");
            testScript.deleteOnExit();

            String script = "try:\n    import whisper\n    print('INSTALLED')\nexcept ImportError:\n    print('NOT_INSTALLED')";
            Files.write(testScript.toPath(), script.getBytes());

            ProcessBuilder pb = new ProcessBuilder(pythonExe.getAbsolutePath(), testScript.getAbsolutePath());
            pb.redirectErrorStream(true);
            Process process = pb.start();

            StringBuilder output = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line);
                }
            }

            boolean completed = process.waitFor(30, TimeUnit.SECONDS);
            if (completed && output.toString().contains("INSTALLED")) {
                LoggingUtil.info("✓ Whisper is already installed");
                return true;
            }

            LoggingUtil.info("Whisper not found. Installing...");
            return false;

        } catch (Exception e) {
            LoggingUtil.error("Failed to check Whisper: " + e.getMessage());
            return false;
        }
    }

    private static void installWhisper(File pythonExe) {
        LoggingUtil.info("========================================");
        LoggingUtil.info("Installing Whisper packages...");
        LoggingUtil.info("This may take 3-5 minutes...");
        LoggingUtil.info("========================================");

        try {
            // First ensure pip is available
            LoggingUtil.info("Ensuring pip is available...");
            runPythonCommand(pythonExe, "-m ensurepip");

            // Upgrade pip
            LoggingUtil.info("Upgrading pip...");
            runPythonCommand(pythonExe, "-m pip install --upgrade pip");

            // Install setuptools
            LoggingUtil.info("Installing setuptools...");
            runPythonCommand(pythonExe, "-m pip install setuptools");

            // Install wheel
            LoggingUtil.info("Installing wheel...");
            runPythonCommand(pythonExe, "-m pip install wheel");

            // Install numpy
            LoggingUtil.info("Installing numpy...");
            runPythonCommand(pythonExe, "-m pip install numpy");

            // Install torch (CPU version)
            LoggingUtil.info("Installing torch (CPU version)...");
            runPythonCommand(pythonExe, "-m pip install torch --index-url https://download.pytorch.org/whl/cpu");

            // Install openai-whisper
            LoggingUtil.info("Installing openai-whisper...");
            runPythonCommand(pythonExe, "-m pip install openai-whisper");

            // Install ffmpeg-python
            LoggingUtil.info("Installing ffmpeg-python...");
            runPythonCommand(pythonExe, "-m pip install ffmpeg-python");

            // Install tqdm
            LoggingUtil.info("Installing tqdm...");
            runPythonCommand(pythonExe, "-m pip install tqdm");

            // Verify installation
            LoggingUtil.info("Verifying Whisper installation...");
            verifyWhisperInstallation(pythonExe);

            LoggingUtil.info("========================================");
            LoggingUtil.info("✓ Whisper packages installed successfully!");
            LoggingUtil.info("========================================");

        } catch (Exception e) {
            LoggingUtil.error("Failed to install Whisper: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void runPythonCommand(File pythonExe, String command) throws Exception {
        // Split command properly
        String[] parts = command.split(" ");
        List<String> cmd = new ArrayList<>();
        cmd.add(pythonExe.getAbsolutePath());
        cmd.addAll(Arrays.asList(parts));

        ProcessBuilder pb = new ProcessBuilder(cmd);
        pb.redirectErrorStream(true);
        Process process = pb.start();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.contains("Collecting") || line.contains("Downloading") ||
                        line.contains("Installing") || line.contains("Successfully")) {
                    LoggingUtil.info("  " + line);
                }
            }
        }

        boolean completed = process.waitFor(300, TimeUnit.SECONDS);
        if (!completed) {
            process.destroyForcibly();
            throw new Exception("Command timed out: " + command);
        }

        int exitCode = process.exitValue();
        if (exitCode != 0) {
            throw new Exception("Command failed with exit code: " + exitCode);
        }
    }

    private static void verifyWhisperInstallation(File pythonExe) throws Exception {
        File testScript = File.createTempFile("verify_whisper", ".py");
        testScript.deleteOnExit();

        String script =
                "import whisper\n" +
                        "import sys\n" +
                        "print('Whisper version:', whisper.__version__)\n" +
                        "print('✓ Whisper installed successfully')\n" +
                        "sys.exit(0)";

        Files.write(testScript.toPath(), script.getBytes());

        ProcessBuilder pb = new ProcessBuilder(pythonExe.getAbsolutePath(), testScript.getAbsolutePath());
        pb.redirectErrorStream(true);
        Process process = pb.start();

        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
                LoggingUtil.info("  " + line);
            }
        }

        boolean completed = process.waitFor(60, TimeUnit.SECONDS);
        if (completed && output.toString().contains("✓")) {
            LoggingUtil.info("✓ Whisper verification passed");
        } else {
            throw new Exception("Whisper verification failed: " + output.toString());
        }
    }
}